from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from ..config import settings

engine = create_engine(settings.database_url, future=True)
SessionFactory = sessionmaker(bind=engine, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
