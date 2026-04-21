from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from ..schemas.booking import BookingCreate
from ..models import User, Service, Booking
from ..shared.exceptions import (
    UserNotFoundError,
    ServiceNotFoundError,
    TimeSlotOccupiedError,
    InvalidStartTimeError,
    BookingNotFoundError,
    UnableToConfirmError,
    UnableToCancelError,
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

    # Check for overlap
    booking_start = (
        booking.start_time.replace(tzinfo=timezone.utc)
        if booking.start_time.tzinfo is None
        else booking.start_time
    )
    if booking_start < datetime.now(timezone.utc):
        raise InvalidStartTimeError()

    new_end_time = booking_start + timedelta(minutes=service.duration_minutes)
    overlap = session.scalar(
        select(Booking).where(
            Booking.start_time < new_end_time,
            Booking.end_time > booking_start,
            Booking.status != BookingStatus.cancelled,
        )
    )
    if overlap:
        raise TimeSlotOccupiedError()

    new_booking = Booking(
        user_id=booking.user_id,
        service_id=booking.service_id,
        start_time=booking_start,
        end_time=new_end_time,
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


def _get_booking_or_404(session: Session, booking_id: int) -> Booking:
    booking = session.scalar(select(Booking).where(Booking.id == booking_id))
    if booking is None:
        raise BookingNotFoundError()

    return booking
