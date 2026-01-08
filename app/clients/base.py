import json
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


class HTTPClient:
    """
    Synchronous HTTP transport layer with session management and retry logic.
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

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        return self.session.request(method=method, url=url, timeout=(10, 30), **kwargs)


class BaseAPIClient:
    """
    Abstract API client providing shared infrastructure for test orchestration:
    logging, Allure reporting, and automatic Pydantic model serialization.
    """

    def __init__(self, base_url: str) -> None:
        self._http = HTTPClient(base_url)

    @property
    def session(self) -> Session:
        return self._http.session

    def _request(self, method: str, endpoint: str, **kwargs: Any) -> Response:
        """
        Executes request through transport layer with
        integrated reporting and error mapping.
        """

        url = urljoin(self._http.base_url, endpoint)

        logger.debug(f"Request: {method} {url} | Body: {kwargs.get('json')}")

        with allure.step(f"{method} {url}"):
            if kwargs.get("json"):
                allure.attach(
                    json.dumps(kwargs.get("json"), indent=2),
                    name="Request Body",
                    attachment_type=allure.attachment_type.JSON,
                )

            try:
                response = self._http.request(method=method, url=url, **kwargs)

                allure.attach(
                    f"Status Code: {response.status_code}\n{response.text}",
                    name="Response Body",
                    attachment_type=allure.attachment_type.TEXT,
                )

                logger.debug(
                    f"Response: {response.status_code} | "
                    f"Time: {response.elapsed.total_seconds()}s"
                )

                try:
                    response.raise_for_status()

                except requests.HTTPError as e:
                    logger.error(f"HTTP Error: {e.response.status_code}")

                    raise APIClientError(
                        message=f"API Error {e.response.status_code}: {e}",
                        status_code=e.response.status_code,
                        payload=self._get_error_payload(e.response),
                    ) from e

                return response

            except requests.RequestException as e:
                logger.error(f"Network Error: {e}")

                raise APIClientError(f"Network error during {method} {url}") from e

    def _get_error_payload(self, response: Response) -> dict[str, Any] | None:
        try:
            return cast(dict[str, Any], response.json())

        except Exception:
            return None

    def _prepare_payload(
        self,
        payload: BaseModel | dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """
        Normalizes various payload types into JSON-compatible dictionaries.
        Supports Pydantic models with optional custom 'to_payload' methods.
        """

        if payload is None:
            return None

        if isinstance(payload, BaseModel):
            if hasattr(payload, "to_payload"):
                return payload.to_payload()  # type: ignore

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
