from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from ..schemas.user import UserCreate, UserRead, UserUpdate
from ..db.session import get_session
from ..services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def post_user(user: UserCreate, session: Session = Depends(get_session)):
    return user_service.create_user(session, user)


@router.get("/", response_model=list[UserRead])
def get_users(session: Session = Depends(get_session)):
    return user_service.list_users(session)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    return user_service.get_user(session, user_id)


@router.patch("/{user_id}", response_model=UserRead)
def patch_user(user_id: int, user: UserUpdate, session: Session = Depends(get_session)):
    return user_service.update_user(session, user_id, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user_service.delete_user(session, user_id)
