import pytest

from app.clients import BookerClient
from app.exceptions import APIClientError
from app.schemas import Booking, BookingResponse


def test_create_booking(client: BookerClient, test_booking_data: Booking) -> None:
    """
    Test positive creation of a booking.
    Verifies that the returned data matches the sent data.
    """
    response: BookingResponse = client.create_booking(test_booking_data)

    assert response.bookingid is not None
    assert response.booking.first_name == test_booking_data.first_name
    assert response.booking.total_price == test_booking_data.total_price


def test_get_booking(client: BookerClient, created_booking: BookingResponse) -> None:
    """
    Test retrieving an existing booking.
    Uses 'created_booking' fixture to ensure a booking exists.
    """
    booking = client.get_booking(created_booking.bookingid)

    assert booking.first_name == created_booking.booking.first_name
    assert booking.last_name == created_booking.booking.last_name


def test_update_booking(
    client: BookerClient,
    auth_token: str,
    created_booking: BookingResponse,
    test_booking_data: Booking,
) -> None:
    """
    Test updating a booking.
    Requires 'auth_token' for permission.
    """
    update_data = test_booking_data.model_copy()
    update_data.first_name = "UpdatedName"

    updated_booking = client.update_booking(
        booking_id=created_booking.bookingid,
        booking_data=update_data,
        token=auth_token,
    )

    assert updated_booking.first_name == "UpdatedName"
    assert updated_booking.total_price == test_booking_data.total_price


def test_delete_booking(
    client: BookerClient, auth_token: str, created_booking: BookingResponse
) -> None:
    """
    Test deleting a booking.
    Verifies that subsequent access returns 404.
    """
    client.delete_booking(created_booking.bookingid, auth_token)

    with pytest.raises(APIClientError) as exc_info:
        client.get_booking(created_booking.bookingid)

    assert exc_info.value.status_code == 404
