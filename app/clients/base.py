from typing import Any
from urllib.parse import urljoin

import requests
from loguru import logger
from pydantic import BaseModel
from requests import Response, Session

from app.exceptions import APIClientError
from app.schemas.common import HttpMethod


class BaseClient:
    """
    Base class for all API clients.
    Wraps requests.Session to handle connection pooling, logging, and error handling.
    Now supports automatic Pydantic model serialization.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session: Session = requests.Session()

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Response:
        """
        Internal method to execute HTTP requests with logging and error handling.
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

    def _prepare_payload(
        self, payload: BaseModel | dict | None
    ) -> dict[str, Any] | None:
        """
        Helper: Converts Pydantic models to dicts ready for JSON serialization.
        Enforces by_alias=True and mode='json' globally.
        """
        if payload is None:
            return None

        if isinstance(payload, BaseModel):
            return payload.model_dump(by_alias=True, mode="json")

        return payload

    def get(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.GET, endpoint, **kwargs)

    def post(
        self, endpoint: str, payload: BaseModel | dict | None = None, **kwargs: Any
    ) -> Response:
        json_data = self._prepare_payload(payload)
        return self._request(HttpMethod.POST, endpoint, json=json_data, **kwargs)

    def put(
        self, endpoint: str, payload: BaseModel | dict | None = None, **kwargs: Any
    ) -> Response:
        json_data = self._prepare_payload(payload)
        return self._request(HttpMethod.PUT, endpoint, json=json_data, **kwargs)

    def patch(
        self, endpoint: str, payload: BaseModel | dict | None = None, **kwargs: Any
    ) -> Response:
        json_data = self._prepare_payload(payload)
        return self._request(HttpMethod.PATCH, endpoint, json=json_data, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.DELETE, endpoint, **kwargs)
