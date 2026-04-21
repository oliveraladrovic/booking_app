from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from datetime import date

from ..schemas.service import ServiceRead, ServiceCreate, ServiceUpdate
from ..db.session import get_session
from ..services import service_service

router = APIRouter(prefix="/services", tags=["Services"])


@router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
def post_service(service: ServiceCreate, session: Session = Depends(get_session)):
    return service_service.create_service(session, service)


@router.get("/", response_model=list[ServiceRead])
def get_services(
    user_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    session: Session = Depends(get_session),
):
    return service_service.list_services(session, user_id, start_date, end_date)


@router.get("/{service_id}", response_model=ServiceRead)
def get_service(service_id: int, session: Session = Depends(get_session)):
    return service_service.get_service(session, service_id)


@router.patch("/{service_id}", response_model=ServiceRead)
def patch_service(
    service_id: int, service: ServiceUpdate, session: Session = Depends(get_session)
):
    return service_service.update_service(session, service_id, service)


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(service_id: int, session: Session = Depends(get_session)):
    service_service.delete_service(session, service_id)
