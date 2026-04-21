from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from ..schemas.booking import BookingCreate, BookingRead
from ..db.session import get_session
from ..services import booking_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def post_booking(booking: BookingCreate, session: Session = Depends(get_session)):
    return booking_service.create_booking(session, booking)


@router.post("/{booking_id}/confirm", response_model=BookingRead)
def confirm_booking(booking_id: int, session: Session = Depends(get_session)):
    return booking_service.confirm_booking(session, booking_id)


@router.post("/{booking_id}/cancel", response_model=BookingRead)
def cancel_booking(booking_id: int, session: Session = Depends(get_session)):
    return booking_service.cancel_booking(session, booking_id)


@router.post("/{booking_id}/complete", response_model=BookingRead)
def complete_booking(booking_id: int, session: Session = Depends(get_session)):
    return booking_service.complete_booking(session, booking_id)


@router.get("/", response_model=list[BookingRead])
def get_bookings(session: Session = Depends(get_session)):
    return booking_service.list_bookings(session)


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: int, session: Session = Depends(get_session)):
    return booking_service.get_booking(session, booking_id)
