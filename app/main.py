import shlex
import subprocess
from typing import Any

import uvicorn
from fastapi import BackgroundTasks, FastAPI
from loguru import logger

from app.schemas import TestRunRequest
from config.logger import configure_logging
from config.settings import settings

configure_logging()

app = FastAPI(
    title="QA Orchestrator API",
    version="1.0.0",
    description="Microservice for automated test execution management.",
)


def run_pytest_worker(request: TestRunRequest) -> None:
    """
    Executes pytest in a subprocess based on the provided configuration.
    Runs in the background to prevent blocking the API response.
    """
    logger.info(
        f"START: Test run sequence | Suite: {request.test_suite} | "
        f"Browser: {request.browser}"
    )

    command = [
        "pytest",
        request.test_suite,
        "--alluredir",
        "allure-results",
    ]

    command.extend(["--browser", request.browser])

    if not request.headless:
        command.append("--headed")

    logger.debug(f"EXEC: {shlex.join(command)}")

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if process.returncode == 0:
            logger.info("FINISH: All tests passed successfully.")
        elif process.returncode == 1:
            logger.warning("FINISH: Test execution completed with failures.")
        else:
            logger.error(
                f"FINISH: Execution interrupted. Error code: {process.returncode}"
            )
            logger.debug(f"STDERR: {process.stderr}")

    except Exception as e:
        logger.critical(f"INFRA ERROR: Subprocess failure: {e}")


@app.post("/run", status_code=202)
async def trigger_test_run(
    request: TestRunRequest, background_tasks: BackgroundTasks
) -> dict[str, Any]:
    """
    Initiates an asynchronous test run.
    """
    background_tasks.add_task(run_pytest_worker, request)

    return {
        "status": "accepted",
        "message": "Test execution initiated in background.",
        "request_id": id(request),
        "details": {
            "suite": request.test_suite,
            "browser": request.browser,
        },
    }


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """System health check endpoint."""
    return {
        "status": "online",
        "environment": settings.app_env,
        "api_version": "1.0.0",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
