from sqlalchemy import select
from sqlalchemy.orm import Session

from ..schemas.service import ServiceCreate, ServiceUpdate
from ..models.service import Service
from ..shared.exceptions import ServiceNotFoundError


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


def list_services(session: Session) -> list[Service]:
    return session.scalars(select(Service)).all()


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
