from loguru import logger

from app.clients.base import BaseClient
from app.exceptions import APIClientError
from config.logger import configure_logging
from config.settings import settings


def main():
    configure_logging()

    logger.info("Starting Application...")

    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info(f"Base URL: {settings.base_url}")

    client = BaseClient(base_url=str(settings.base_url))

    try:
        logger.info("Executing API Request...")
        response = client.get("/ping")

        logger.info(f"Status Code: {response.status_code}")
        logger.debug(f"Response Text: {response.text}")

    except APIClientError as e:
        logger.warning(f"API is unavailable or failed: {e}")

    except Exception as e:
        logger.critical(f"Unexpected System Crash: {e}")


if __name__ == "__main__":
    main()
