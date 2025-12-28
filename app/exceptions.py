class QAOrchestratorError(Exception):
    """Base exception for all application-specific errors."""


class ConfigurationError(QAOrchestratorError):
    """Raised when critical configuration is missing or invalid."""


class APIClientError(QAOrchestratorError):
    """Base exception for external API interactions."""
