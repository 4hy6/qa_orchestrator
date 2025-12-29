from typing import Any
from urllib.parse import urljoin

import requests
from loguru import logger
from requests import Response, Session

from app.exceptions import APIClientError
from app.schemas.common import HttpMethod


class BaseClient:
    """
    Base class for all API clients.
    Wraps requests.Session to handle connection pooling, logging, and error handling.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session: Session = requests.Session()

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Response:
        """
        Internal method to execute HTTP requests with logging and error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (e.g. "/auth")
            **kwargs: Additional arguments for requests (json, params, headers)

        Returns:
            requests.Response object

        Raises:
            APIClientError: If the request fails (network error, timeout)
        """
        url = urljoin(self.base_url, endpoint)

        logger.debug(
            f"Request: {method} {url} | "
            f"Params: {kwargs.get('params')} | "
            f"Body: {kwargs.get('json')}"
        )

        try:
            response = self.session.request(method=method, url=url, **kwargs)

            logger.debug(
                f"Response: {response.status_code} | "
                f"Time: {response.elapsed.total_seconds()}s"
            )
            return response

        except requests.RequestException as e:
            logger.error(f"Request failed: {method} {url} | Error: {e}")
            raise APIClientError(f"Network error during {method} {url}") from e

    def get(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.GET, endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.POST, endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.PUT, endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.DELETE, endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.PATCH, endpoint, **kwargs)
