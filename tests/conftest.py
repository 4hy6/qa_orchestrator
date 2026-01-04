import pytest

from app.clients import BookerClient
from app.schemas import Booking, BookingDates
from config.settings import settings


@pytest.fixture(scope="session")
def client():
    """
    Creates a single instance of BookerClient for the entire test session.
    Manages the HTTP session lifecycle.
    """
    client_instance = BookerClient(base_url=str(settings.base_url))

    yield client_instance

    client_instance.session.close()


@pytest.fixture(scope="session")
def auth_token(client):
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
def test_booking_data():
    """Returns a valid Booking model with hardcoded test data."""
    return Booking(
        firstname="Alex",
        lastname="Tester",
        totalprice=150,
        depositpaid=True,
        bookingdates=BookingDates(checkin="2024-01-01", checkout="2024-01-10"),
        additionalneeds="WiFi",
    )


@pytest.fixture
def created_booking(client, test_booking_data):
    """
    Creates a booking in the system and returns the response object.
    Useful for tests that need an existing booking (Get/Update/Delete).
    """
    response = client.create_booking(test_booking_data)
    return response
