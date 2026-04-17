from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..schemas.user import UserCreate, UserUpdate
from ..models.user import User
from ..shared.exceptions import EmailAlreadyExistsError, UserNotFoundError


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


def list_users(session: Session) -> list[User]:
    return session.scalars(select(User)).all()


def get_user(session: Session, user_id: int) -> User:
    return _get_user_or_404(session, user_id)


def update_user(session: Session, user_id: int, user_data: UserUpdate) -> User:
    user = _get_user_or_404(session, user_id)
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        return user

    updated = False
    for field, value in update_data.items():
        if field == "email" and value == user.email:
            continue

        setattr(user, field, value)
        updated = True

    if not updated:
        return user

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise EmailAlreadyExistsError()

    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> None:
    user = _get_user_or_404(session, user_id)

    # Soft delete: anonymize user and deactivate
    user.full_name = "Deleted User"
    user.email = f"user{user.id}@deleted-user.com"
    user.is_active = False
    session.commit()


def _get_user_or_404(session: Session, user_id: int) -> User:
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise UserNotFoundError()

    return user
