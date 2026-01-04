import json
from pathlib import Path
from typing import Any

import allure
import pytest
from pydantic import BaseModel

from app.clients import BookerClient
from app.exceptions import APIClientError
from app.schemas import Booking, BookingResponse


class NegativeScenario(BaseModel):
    """
    Schema for validating test data from JSON.
    Ensures that our test scenarios are well-formed.
    """

    case: str
    payload_update: dict[str, Any]
    expected_status: int


def load_scenarios() -> list[NegativeScenario]:
    """Helper to load and VALIDATE scenarios from JSON."""
    path = Path(__file__).parent / "data" / "negative_scenarios.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
        return [NegativeScenario(**item) for item in data]


@allure.feature("Booking Operations")
@allure.story("Negative Scenarios")
class TestBookingNegative:
    @allure.title("Create Booking with invalid data: {scenario.case}")
    @pytest.mark.parametrize("scenario", load_scenarios())
    def test_create_booking_negative(
        self,
        client: BookerClient,
        test_booking_data: Booking,
        scenario: NegativeScenario,
    ) -> None:
        payload = test_booking_data.to_payload()

        payload.update(scenario.payload_update)

        expected_status = scenario.expected_status

        with allure.step(f"Send POST request with invalid data: {scenario.case}"):
            if expected_status >= 400:
                with pytest.raises(APIClientError) as exc_info:
                    client.post(endpoint=client.BOOKING_ENDPOINT, payload=payload)

                with allure.step("Verify error status code"):
                    assert exc_info.value.status_code == expected_status, (
                        f"Expected {expected_status}, "
                        f"but got {exc_info.value.status_code}. "
                        f"Error message: {exc_info.value.message}"
                    )
            else:
                response = client.post(
                    endpoint=client.BOOKING_ENDPOINT, payload=payload
                )

                with allure.step("Verify success status code"):
                    assert (
                        response.status_code == expected_status
                    ), f"Expected {expected_status}, but got {response.status_code}."

    @allure.title("Delete booking with invalid token")
    def test_delete_booking_invalid_token(
        self, client: BookerClient, created_booking: BookingResponse
    ) -> None:
        """Verifies 403 Forbidden when deleting with an incorrect token."""

        bad_token = "invalid_token_xyz"

        with allure.step("Try to delete with bad token"):
            with pytest.raises(APIClientError) as exc:
                client.delete_booking(created_booking.bookingid, bad_token)

        with allure.step("Check exception status code"):
            assert exc.value.status_code == 403
