from typing import Any

import allure

from app.clients.base import BaseClient
from app.schemas import AuthRequest, AuthResponse, Booking, BookingResponse


class BookerClient(BaseClient):
    """
    Client for interacting with the Restful-Booker API.
    """

    AUTH_ENDPOINT = "/auth"
    BOOKING_ENDPOINT = "/booking"

    @allure.step("Authenticate user")
    def create_auth_token(self, username: str, password: str) -> str:
        payload = AuthRequest(username=username, password=password)

        response = self.post(endpoint=self.AUTH_ENDPOINT, payload=payload)

        auth_response = AuthResponse(**response.json())
        return auth_response.token

    @allure.step("Create booking")
    def create_booking(self, booking_data: Booking) -> BookingResponse:
        response = self.post(endpoint=self.BOOKING_ENDPOINT, payload=booking_data)
        return BookingResponse(**response.json())

    @allure.step("Get booking")
    def get_booking(self, booking_id: int) -> Booking:
        response = self.get(endpoint=f"{self.BOOKING_ENDPOINT}/{booking_id}")
        return Booking(**response.json())

    @allure.step("Update booking")
    def update_booking(
        self, booking_id: int, booking_data: Booking, token: str
    ) -> Booking:
        headers = {"Cookie": f"token={token}"}
        response = self.put(
            endpoint=f"{self.BOOKING_ENDPOINT}/{booking_id}",
            payload=booking_data,
            headers=headers,
        )
        return Booking(**response.json())

    @allure.step("Partial update booking (PATCH)")
    def partial_update_booking(
        self, booking_id: int, payload: dict[str, Any], token: str
    ) -> Booking:
        headers = {"Cookie": f"token={token}"}
        response = self.patch(
            endpoint=f"{self.BOOKING_ENDPOINT}/{booking_id}",
            payload=payload,
            headers=headers,
        )
        return Booking(**response.json())

    @allure.step("Delete booking")
    def delete_booking(self, booking_id: int, token: str) -> None:
        headers = {"Cookie": f"token={token}"}
        self.delete(endpoint=f"{self.BOOKING_ENDPOINT}/{booking_id}", headers=headers)

    @allure.step("Get booking IDs")
    def get_booking_ids(self, params: dict[str, Any] | None = None) -> list[int]:
        response = self.get(endpoint=self.BOOKING_ENDPOINT, params=params)
        return [item["bookingid"] for item in response.json()]
