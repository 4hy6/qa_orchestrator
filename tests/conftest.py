from collections.abc import Generator
from datetime import date
from typing import Any

import pytest
from loguru import logger
from sqlalchemy.orm import Session

from app.clients import BookerClient
from app.db import SessionLocal
from app.db.models import TestRun
from app.exceptions import APIClientError
from app.schemas import Booking, BookingDates, BookingResponse
from config.settings import settings


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="session")
def client() -> Generator[BookerClient, None, None]:
    client_instance = BookerClient(base_url=str(settings.base_url))

    yield client_instance

    client_instance.session.close()


@pytest.fixture(scope="session")
def auth_token(client: BookerClient) -> str:
    token = client.create_auth_token(
        username=settings.booker_username,
        password=settings.booker_password,
    )
    return token


@pytest.fixture
def test_booking_data() -> Booking:
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
    response = client.create_booking(test_booking_data)

    yield response

    try:
        client.delete_booking(response.bookingid, auth_token)
    except APIClientError as e:
        from loguru import logger

        logger.warning(f"Failed to cleanup booking {response.bookingid}: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, Any, None]:
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        test_name = item.name
        status = report.outcome.upper()
        duration = report.duration

        session = SessionLocal()
        try:
            test_run = TestRun(
                test_name=test_name,
                status=status,
                duration=duration,
            )
            session.add(test_run)
            session.commit()
            logger.debug(f"Saved test result: {test_name} [{status}]")
        except Exception as e:
            logger.error(f"Failed to save test result to DB: {e}")
        finally:
            session.close()
