from collections.abc import Generator
from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.clients import BookerClient
from app.db import Base, SessionLocal, engine
from app.exceptions import APIClientError
from app.schemas import Booking, BookingDates, BookingResponse
from config.settings import settings


@pytest.fixture(scope="session", autouse=True)
def init_db() -> None:
    """
    Initializes the database schema before the test session starts.
    Creates tables if they do not exist.
    """
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """
    Provides a transactional scope around a series of operations.
    Yields a SQLAlchemy Session.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def client() -> Generator[BookerClient, None, None]:
    """
    Creates a single instance of BookerClient for the entire test session.
    Manages the HTTP session lifecycle.
    """
    client_instance = BookerClient(base_url=str(settings.base_url))

    yield client_instance

    client_instance.session.close()


@pytest.fixture(scope="session")
def auth_token(client: BookerClient) -> str:
    """
    Performs authentication once per session and returns the token.
    Depends on the 'client' fixture.
    """
    token = client.create_auth_token(
        username=settings.booker_username,
        password=settings.booker_password,
    )
    return token


@pytest.fixture
def test_booking_data() -> Booking:
    """Returns a valid Booking model with hardcoded test data."""

    return Booking(  # type: ignore[call-arg]
        first_name="Alex",
        last_name="Tester",
        total_price=150,
        deposit_paid=True,
        booking_dates=BookingDates(
            checkin=date(2024, 1, 1), checkout=date(2024, 1, 10)
        ),
        additional_needs="WiFi",
    )


@pytest.fixture
def created_booking(
    client: BookerClient, auth_token: str, test_booking_data: Booking
) -> Generator[BookingResponse, None, None]:
    """
    Creates a booking, yields it for the test, and deletes it afterwards.
    Ensures no 'zombie data' is left in the system (Teardown pattern).
    """
    response = client.create_booking(test_booking_data)

    yield response

    try:
        client.delete_booking(response.bookingid, auth_token)
    except APIClientError:
        pass
