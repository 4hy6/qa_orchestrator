from datetime import date, timedelta

from app.clients import BookerClient
from app.schemas import Booking, BookingDates, BrowserType, TestRunRequest
from config.logger import configure_logging, logger
from config.settings import settings


def main():
    configure_logging()

    logger.info("Starting Orchestrator Application...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"Target URL: {settings.base_url}")

    try:
        req = TestRunRequest(test_suite="smoke/tests", browser=BrowserType.FIREFOX)
        logger.debug(
            f"Internal schema validation passed. Browser target: {req.browser}"
        )
    except Exception as e:
        logger.critical(
            f"Internal schema validation failed. System integrity compromised: {e}"
        )
        exit(1)

    client = BookerClient(base_url=str(settings.base_url))

    try:
        token = client.create_auth_token(
            username=settings.booker_username, password=settings.booker_password
        )
        logger.info(f"Authentication successful. Session Token: {token[:5]}***")
    except Exception as e:
        logger.critical(
            f"Authentication failed. Check credentials in .env. Details: {e}"
        )
        exit(1)

    today = date.today()
    booking_payload = Booking(
        first_name="Ivan",
        last_name="Automator",
        total_price=120,
        deposit_paid=True,
        booking_dates=BookingDates(
            checkin=today + timedelta(days=1), checkout=today + timedelta(days=5)
        ),
        additional_needs="Quiet Room",
    )

    try:
        logger.info(
            f"Processing booking creation for user: {booking_payload.first_name}"
        )

        created_booking = client.create_booking(booking_payload)

        logger.info(
            f"Booking successfully created. "
            f"ID: {created_booking.bookingid} | "
            f"Name: {created_booking.booking.first_name} | "
            f"Check-in: {created_booking.booking.booking_dates.checkin}"
        )

    except Exception as e:
        logger.error(f"Business transaction failed. API Error: {e}")
        exit(1)

    logger.info("Sanity check cycle completed successfully.")


if __name__ == "__main__":
    main()
