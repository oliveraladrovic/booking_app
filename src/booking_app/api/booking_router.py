from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from ..schemas.booking import BookingCreate, BookingRead
from ..db.session import get_session
from ..services import booking_service

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def post_booking(booking: BookingCreate, session: Session = Depends(get_session)):
    return booking_service.create_booking(session, booking)
