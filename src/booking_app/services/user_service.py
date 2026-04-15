from sqlalchemy.orm import Session

from ..schemas.user import UserCreate
from ..models.user import User


def create_user(session: Session, data: UserCreate) -> User:
    new_user = User(
        full_name=data.full_name,
        email=data.email,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user
