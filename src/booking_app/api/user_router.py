from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from ..schemas.user import UserCreate, UserRead
from ..db.session import get_session
from ..services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def post_user(user: UserCreate, session: Session = Depends(get_session)):
    return user_service.create_user(session, user)
