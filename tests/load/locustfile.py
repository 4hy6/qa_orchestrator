from datetime import date

from locust import HttpUser, between, task

from app.schemas.auth import AuthRequest, AuthResponse
from app.schemas.booking import Booking, BookingDates
from config.logger import logger
from config.settings import settings


class BookerUser(HttpUser):
    wait_time = between(1, 2)
    token: str | None = None

    def on_start(self) -> None:
        payload = AuthRequest(
            username=settings.booker_username,
            password=settings.booker_password,
        ).to_payload()

        with self.client.post("/auth", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    self.token = AuthResponse(**response.json()).token
                    logger.info(f"VUser authenticated: {self.token[:8]}...")
                except Exception as e:
                    logger.error(f"Token parsing failed: {e}")
                    response.failure(f"Auth response parsing error: {e}")
            else:
                logger.error(f"Auth failed. Status: {response.status_code}")
                response.failure("Authentication handshake failed")

    @task(3)
    def get_bookings(self) -> None:
        with self.client.get("/booking", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Get bookings failed: {response.status_code}")

    @task(1)
    def create_booking(self) -> None:
        booking_payload = Booking(  # type: ignore[call-arg]
            first_name="Load",
            last_name="Test",
            total_price=123,
            deposit_paid=True,
            booking_dates=BookingDates(
                checkin=date(2024, 1, 1),
                checkout=date(2024, 1, 2),
            ),
            additional_needs="Locust Execution",
        ).to_payload()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Cookie"] = f"token={self.token}"

        with self.client.post(
            "/booking",
            json=booking_payload,
            headers=headers,
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                pass
            else:
                logger.error(f"Payload: {booking_payload}")
                logger.error(f"Response: {response.text}")
                response.failure(f"Create booking failed: {response.status_code}")
