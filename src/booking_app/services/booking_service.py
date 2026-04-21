from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta, date

from ..schemas.booking import BookingCreate, BookingUpdate
from ..models import User, Service, Booking
from ..shared.exceptions import (
    UserNotFoundError,
    ServiceNotFoundError,
    TimeSlotOccupiedError,
    InvalidStartTimeError,
    BookingNotFoundError,
    UnableToConfirmError,
    UnableToCancelError,
    UnableToCompleteError,
    BookingUpdateError,
)
from ..shared.enums import BookingStatus


def create_booking(session: Session, booking: BookingCreate) -> Booking:

    # Check if user exists
    user = session.scalar(
        select(User).where(User.id == booking.user_id, User.is_active)
    )
    if user is None:
        raise UserNotFoundError()

    # Check if service exists
    service = session.scalar(
        select(Service).where(Service.id == booking.service_id, Service.is_active)
    )
    if service is None:
        raise ServiceNotFoundError()

    booking_start, booking_end = _calculate_time(
        booking.start_time, service.duration_minutes
    )
    _check_for_overlap(booking_start, booking_end, session)

    new_booking = Booking(
        user_id=booking.user_id,
        service_id=booking.service_id,
        start_time=booking_start,
        end_time=booking_end,
        status=BookingStatus.pending,
        notes=booking.notes,
    )
    session.add(new_booking)
    session.commit()
    session.refresh(new_booking)
    return new_booking


def confirm_booking(session: Session, booking_id: int) -> Booking:
    booking = _get_booking_or_404(session, booking_id)
    if booking.status != BookingStatus.pending:
        raise UnableToConfirmError()

    if booking.start_time < datetime.now(timezone.utc):
        raise InvalidStartTimeError()

    booking.status = BookingStatus.confirmed
    session.commit()
    return booking


def cancel_booking(session: Session, booking_id: int) -> Booking:
    booking = _get_booking_or_404(session, booking_id)
    if (
        booking.status != BookingStatus.pending
        and booking.status != BookingStatus.confirmed
    ):
        raise UnableToCancelError()

    booking.status = BookingStatus.cancelled
    session.commit()
    return booking


def complete_booking(session: Session, booking_id: int) -> Booking:
    booking = _get_booking_or_404(session, booking_id)
    if booking.status != BookingStatus.confirmed:
        raise UnableToCompleteError()

    booking.status = BookingStatus.completed
    session.commit()
    return booking


def list_bookings(
    session: Session, start_date: date | None = None, end_date: date | None = None
) -> list[Booking]:
    bookings = session.query(Booking)
    if start_date is not None:
        bookings = bookings.filter(Booking.start_time >= start_date)
    if end_date is not None:
        bookings = bookings.filter(Booking.start_time <= end_date)
    if any(value is not None for value in (start_date, end_date)):
        bookings = bookings.filter(
            Booking.status != BookingStatus.cancelled,
            Booking.status != BookingStatus.completed,
        )
    bookings = bookings.all()
    return bookings


def get_booking(session: Session, booking_id: int) -> Booking:
    return _get_booking_or_404(session, booking_id)


def update_booking(
    session: Session, booking_id: int, booking_data: BookingUpdate
) -> Booking:
    booking = _get_booking_or_404(session, booking_id)
    if booking.status != BookingStatus.pending:
        raise BookingUpdateError()

    update_data = booking_data.model_dump(exclude_unset=True)
    if not update_data:
        return booking

    for field, value in update_data.items():
        if field == "start_time":
            booking_start, booking_end = _calculate_time(
                value, booking.service.duration_minutes
            )
            _check_for_overlap(booking_start, booking_end, session, booking_id)

        setattr(booking, field, value)

    session.commit()
    return booking


def _get_booking_or_404(session: Session, booking_id: int) -> Booking:
    booking = session.scalar(select(Booking).where(Booking.id == booking_id))
    if booking is None:
        raise BookingNotFoundError()

    return booking


def _calculate_time(
    start_time: datetime, service_duration: int
) -> tuple[datetime, datetime]:
    booking_start = (
        start_time.replace(tzinfo=timezone.utc)
        if start_time.tzinfo is None
        else start_time
    )
    booking_end = booking_start + timedelta(minutes=service_duration)
    return booking_start, booking_end


def _check_for_overlap(
    booking_start: datetime,
    booking_end: datetime,
    session: Session,
    booking_id: int | None = None,
) -> None:

    if booking_start < datetime.now(timezone.utc):
        raise InvalidStartTimeError()

    overlap = session.scalar(
        select(Booking).where(
            Booking.start_time < booking_end,
            Booking.end_time > booking_start,
            Booking.status != BookingStatus.cancelled,
            Booking.id != booking_id,
        )
    )
    if overlap:
        raise TimeSlotOccupiedError()
