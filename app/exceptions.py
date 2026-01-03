from typing import Any


class QAOrchestratorError(Exception):
    """Base exception for all application-specific errors."""


class ConfigurationError(QAOrchestratorError):
    """Raised when critical configuration is missing or invalid."""


class APIClientError(QAOrchestratorError):
    """
    Exception raised for failed API interactions.
    Contains metadata about the failure context.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(message)
