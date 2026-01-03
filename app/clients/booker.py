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

        auth_response = AuthResponse(**response.json())
        return auth_response.token

    def create_booking(self, booking_data: Booking) -> BookingResponse:
        """
        Creates a new booking using strict Pydantic models.
        """
        response = self.post(endpoint="/booking", payload=booking_data)

        return BookingResponse(**response.json())

    def get_booking(self, booking_id: int) -> Booking:
        """
        Retrieves a specific booking by ID.
        """
        response = self.get(endpoint=f"/booking/{booking_id}")
        return Booking(**response.json())

    def update_booking(
        self, booking_id: int, booking_data: Booking, token: str
    ) -> Booking:
        """
        Updates an existing booking. Requires auth token in Cookie.
        """
        headers = {"Cookie": f"token={token}"}

        response = self.put(
            endpoint=f"/booking/{booking_id}", payload=booking_data, headers=headers
        )
        return Booking(**response.json())

    def delete_booking(self, booking_id: int, token: str) -> None:
        """
        Deletes a booking. Returns nothing (201 Created).
        """
        headers = {"Cookie": f"token={token}"}

        self.delete(endpoint=f"/booking/{booking_id}", headers=headers)
