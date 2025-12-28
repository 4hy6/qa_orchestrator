import platform
import sys

from app.schemas.run_test import BrowserType, TestRunRequest
from config.logger import logger
from config.settings import settings


def main() -> None:
    logger.info("Starting QA Orchestrator Diagnostics...")

    # 1. System Info
    logger.debug(f"Python Version: {sys.version}")
    logger.debug(f"Platform: {platform.system()} {platform.release()}")

    # 2. Settings Check
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Target API: {settings.base_url}")

    # 3. Logic Check (Pydantic)
    try:
        logger.info("Validating sample request model...")
        sample_request = TestRunRequest(
            test_suite="Smoke Tests", browser=BrowserType.CHROME
        )
        logger.success(f"Model Validated: {sample_request.model_dump_json()}")
    except Exception as e:
        logger.critical(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
