from enum import StrEnum

from pydantic import BaseModel, Field, PositiveInt


class BrowserType(StrEnum):
    """Supported browser types for UI testing."""

    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"


class TestRunRequest(BaseModel):
    """
    Schema representing a request to run automated tests.
    acts as a DTO (Data Transfer Object).
    """

    __test__ = False

    test_suite: str = Field(
        ...,
        min_length=3,
        description="Path or identifier of the test suite",
    )
    browser: BrowserType = Field(
        default=BrowserType.CHROME,
        description="Target browser for UI tests",
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode (no UI)",
    )
    retries: PositiveInt = Field(
        default=1,
        le=5,
        description="Max retries per failed test. Must be positive and <= 5",
    )
