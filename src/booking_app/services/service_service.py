from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime

from ..schemas.service import ServiceCreate, ServiceUpdate
from ..models import Service, Booking
from ..shared.exceptions import ServiceNotFoundError
from ..shared.enums import BookingStatus


def create_service(session: Session, service: ServiceCreate) -> Service:
    new_service = Service(
        name=service.name,
        description=service.description,
        duration_minutes=service.duration_minutes,
    )
    session.add(new_service)
    session.commit()
    session.refresh(new_service)
    return new_service


def list_services(
    session: Session,
    user_id: int | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[Service]:
    services = session.query(Service)
    if user_id is not None:
        services = services.join(Service.bookings).filter(Booking.user_id == user_id)
    if start_date is not None:
        services = services.filter(Booking.start_time > start_date)
    if end_date is not None:
        services = services.filter(Booking.start_time < end_date)
    if any(value is not None for value in (user_id, start_date, end_date)):
        services = services.filter(
            Booking.status != BookingStatus.cancelled,
            Booking.status != BookingStatus.completed,
        )
    services = services.all()
    return services


def get_service(session: Session, service_id: int) -> Service:
    return _get_service_or_404(session, service_id)


def update_service(
    session: Session, service_id: int, service_data: ServiceUpdate
) -> Service:
    service = _get_service_or_404(session, service_id)
    update_data = service_data.model_dump(exclude_unset=True)

    if not update_data:
        return service

    for field, value in update_data.items():
        setattr(service, field, value)

    session.commit()
    session.refresh(service)
    return service


def delete_service(session: Session, service_id: int) -> None:
    service = _get_service_or_404(session, service_id)

    # Soft delete: deactivate service
    if service.is_active:
        service.is_active = False
        session.commit()


def _get_service_or_404(session: Session, service_id: int) -> Service:
    service = session.scalar(select(Service).where(Service.id == service_id))
    if service is None:
        raise ServiceNotFoundError()

    return service
