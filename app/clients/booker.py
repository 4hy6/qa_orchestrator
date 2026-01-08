from typing import Any

import allure

from app.clients.base import BaseAPIClient
from app.schemas import AuthRequest, AuthResponse, Booking, BookingResponse


class BookerClient(BaseAPIClient):
    """
    Implementation of the Restful-Booker API interface.
    """

    AUTH_ENDPOINT = "/auth"
    BOOKING_ENDPOINT = "/booking"

    @allure.step("Authentication")
    def create_auth_token(self, username: str, password: str) -> str:
        """Obtains session token for protected endpoints."""
        payload = AuthRequest(username=username, password=password)
        response = self.post(endpoint=self.AUTH_ENDPOINT, payload=payload)
        return AuthResponse(**response.json()).token

    @allure.step("Create Booking")
    def create_booking(self, booking_data: Booking) -> BookingResponse:
        response = self.post(endpoint=self.BOOKING_ENDPOINT, payload=booking_data)
        return BookingResponse(**response.json())

    @allure.step("Retrieve Booking")
    def get_booking(self, booking_id: int) -> Booking:
        response = self.get(endpoint=f"{self.BOOKING_ENDPOINT}/{booking_id}")
        return Booking(**response.json())

    @allure.step("Update Booking")
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

    @allure.step("Partial Update Booking")
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

    @allure.step("Delete Booking")
    def delete_booking(self, booking_id: int, token: str) -> None:
        headers = {"Cookie": f"token={token}"}
        self.delete(endpoint=f"{self.BOOKING_ENDPOINT}/{booking_id}", headers=headers)

    @allure.step("List Bookings")
    def get_booking_ids(self, params: dict[str, Any] | None = None) -> list[int]:
        response = self.get(endpoint=self.BOOKING_ENDPOINT, params=params)
        return [item["bookingid"] for item in response.json()]
