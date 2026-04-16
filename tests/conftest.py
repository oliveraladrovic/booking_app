import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Connection, Transaction
from typing import Generator
from fastapi.testclient import TestClient

from booking_app.config import settings
from booking_app.models import Base
from booking_app.main import app
from booking_app.db.session import get_session

engine = create_engine(settings.test_database_url)
TestingSessionFactory = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_connection() -> Generator[Connection, None, None]:
    connection = engine.connect()
    transaction = connection.begin()

    yield connection

    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def db_session(db_connection: Connection) -> Generator[Session, None, None]:
    session = TestingSessionFactory(bind=db_connection)
    # ---------------Dio koji ne razumijem u potpunosti--------------
    nested = db_connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session_: Session, transaction_: Transaction):
        nonlocal nested

        if transaction_.nested and not transaction_._parent_nasted:
            nested = db_connection.begin_nested()

    # ----------------------------------------------------------------
    yield session

    session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_session() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
