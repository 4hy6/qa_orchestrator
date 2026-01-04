import allure
import pytest

from app.clients import BookerClient
from app.exceptions import APIClientError
from app.schemas import Booking, BookingResponse


@allure.feature("Booking Operations")
@allure.story("CRUD Operations")
class TestBookingCRUD:
    @allure.title("Create a new valid booking")
    def test_create_booking(
        self, client: BookerClient, test_booking_data: Booking
    ) -> None:
        response: BookingResponse = client.create_booking(test_booking_data)

        with allure.step("Verify response matches request data"):
            assert response.bookingid is not None
            assert response.booking.first_name == test_booking_data.first_name
            assert response.booking.last_name == test_booking_data.last_name
            assert response.booking.total_price == test_booking_data.total_price
            assert response.booking.deposit_paid == test_booking_data.deposit_paid
            assert (
                response.booking.booking_dates.checkin
                == test_booking_data.booking_dates.checkin
            )
            assert (
                response.booking.additional_needs == test_booking_data.additional_needs
            )

    @allure.title("Get an existing booking by ID")
    def test_get_booking(
        self, client: BookerClient, created_booking: BookingResponse
    ) -> None:
        booking = client.get_booking(created_booking.bookingid)

        with allure.step("Verify fetched data matches created booking"):
            assert booking.first_name == created_booking.booking.first_name
            assert booking.last_name == created_booking.booking.last_name
            assert booking.total_price == created_booking.booking.total_price

    @allure.title("Search booking by First Name")
    def test_search_booking(
        self, client: BookerClient, created_booking: BookingResponse
    ) -> None:
        target_name = created_booking.booking.first_name

        booking_ids = client.get_booking_ids(params={"firstname": target_name})

        with allure.step("Verify created booking ID is found in search results"):
            assert created_booking.bookingid in booking_ids

    @allure.title("Update an existing booking (PUT)")
    def test_update_booking(
        self,
        client: BookerClient,
        auth_token: str,
        created_booking: BookingResponse,
        test_booking_data: Booking,
    ) -> None:
        update_data = test_booking_data.model_copy()
        update_data.first_name = "UpdatedName"

        updated_booking = client.update_booking(
            booking_id=created_booking.bookingid,
            booking_data=update_data,
            token=auth_token,
        )

        with allure.step("Verify firstname is updated and price is unchanged"):
            assert updated_booking.first_name == "UpdatedName"
            assert updated_booking.total_price == test_booking_data.total_price

    @allure.title("Partial Update (PATCH)")
    def test_partial_update_booking(
        self,
        client: BookerClient,
        auth_token: str,
        created_booking: BookingResponse,
    ) -> None:
        new_price = 9999
        patch_payload = {"totalprice": new_price}

        updated_booking = client.partial_update_booking(
            booking_id=created_booking.bookingid,
            payload=patch_payload,
            token=auth_token,
        )

        with allure.step("Verify ONLY price is updated"):
            assert updated_booking.total_price == new_price
            assert updated_booking.first_name == created_booking.booking.first_name

    @allure.title("Delete a booking")
    def test_delete_booking(
        self, client: BookerClient, auth_token: str, created_booking: BookingResponse
    ) -> None:
        client.delete_booking(created_booking.bookingid, auth_token)

        with allure.step("Verify 404 Not Found"):
            with pytest.raises(APIClientError) as exc:
                client.get_booking(created_booking.bookingid)
            assert exc.value.status_code == 404
