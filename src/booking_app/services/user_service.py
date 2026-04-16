from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas.user import UserCreate
from ..models.user import User
from ..shared.exceptions import EmailAlreadyExistsError


def create_user(session: Session, data: UserCreate) -> User:
    new_user = User(
        full_name=data.full_name,
        email=data.email,
    )
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise EmailAlreadyExistsError()

    session.refresh(new_user)
    return new_user
