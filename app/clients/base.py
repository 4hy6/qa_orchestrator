from typing import Any, cast
from urllib.parse import urljoin

import allure
import requests
from loguru import logger
from pydantic import BaseModel
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.exceptions import APIClientError
from app.schemas.common import HttpMethod


class BaseClient:
    """
    Base class for all API clients.
    Wraps requests.Session to handle connection pooling, logging, retries,
    and error handling.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.session: Session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            raise_on_status=False,
        )

        adapter = HTTPAdapter(max_retries=retries)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        # ----------------------------

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

        with allure.step(f"{method} {url}"):
            try:
                response = self.session.request(
                    method=method, url=url, timeout=(10, 30), **kwargs
                )

                logger.debug(
                    f"Response: {response.status_code} | "
                    f"Time: {response.elapsed.total_seconds()}s"
                )

                try:
                    response.raise_for_status()
                except requests.HTTPError as e:
                    logger.error(
                        f"HTTP Error: {e.response.status_code} {e.response.reason} "
                        f"for {method} {url}"
                    )
                    raise APIClientError(
                        message=f"API Error {e.response.status_code}: {e}",
                        status_code=e.response.status_code,
                        payload=self._get_error_payload(e.response),
                    ) from e

                return response

            except requests.RequestException as e:
                logger.error(f"Network Request failed: {method} {url} | Error: {e}")
                raise APIClientError(f"Network error during {method} {url}") from e

    def _get_error_payload(self, response: Response) -> dict[str, Any] | None:
        """Helper to safely extract JSON from error response."""
        try:
            return cast(dict[str, Any], response.json())
        except Exception:
            return None

    def _prepare_payload(
        self, payload: BaseModel | dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """
        Helper: Prepares payload for transmission.
        Delegates serialization logic to the model itself (SSOT).
        """
        if payload is None:
            return None

        if isinstance(payload, BaseModel):
            if hasattr(payload, "to_payload"):
                return payload.to_payload()

            return payload.model_dump(by_alias=True, mode="json")

        return payload

    def get(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.GET, endpoint, **kwargs)

    def post(
        self,
        endpoint: str,
        payload: BaseModel | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        json_data = self._prepare_payload(payload)
        return self._request(HttpMethod.POST, endpoint, json=json_data, **kwargs)

    def put(
        self,
        endpoint: str,
        payload: BaseModel | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        json_data = self._prepare_payload(payload)
        return self._request(HttpMethod.PUT, endpoint, json=json_data, **kwargs)

    def patch(
        self,
        endpoint: str,
        payload: BaseModel | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Response:
        json_data = self._prepare_payload(payload)
        return self._request(HttpMethod.PATCH, endpoint, json=json_data, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        return self._request(HttpMethod.DELETE, endpoint, **kwargs)
