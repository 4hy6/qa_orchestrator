# app/clients/booker.py
from app.clients import BaseClient
from app.schemas import AuthRequest, AuthResponse, Booking, BookingResponse


class BookerClient(BaseClient):
    """
    Client for interacting with the Restful-Booker API.
    Encapsulates knowledge about specific endpoints and data types.
    """

    def create_auth_token(self, username: str, password: str) -> str:
        """
        Authenticates the user and retrieves an access token.
        Returns the raw token string, hiding JSON implementation details.
        """
        payload = AuthRequest(username=username, password=password)

        response = self.post(endpoint="/auth", payload=payload)

        response.raise_for_status()

        auth_response = AuthResponse(**response.json())
        return auth_response.token

    def create_booking(self, booking_data: Booking) -> BookingResponse:
        """
        Creates a new booking using strict Pydantic models.
        """
        response = self.post(endpoint="/booking", payload=booking_data)

        response.raise_for_status()
        return BookingResponse(**response.json())
