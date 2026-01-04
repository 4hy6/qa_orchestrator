from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class HttpMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ContentType(StrEnum):
    JSON = "application/json"
    XML = "application/xml"
    FORM_URLENCODED = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"
    TEXT = "text/plain"


class BaseSchema(BaseModel):
    """
    Base schema for EXTERNAL APIs.
    Single Source of Truth for serialization rules.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
    )

    def to_payload(self) -> dict[str, Any]:
        """
        Converts model to API-compatible dictionary.
        Rules:
        1. Aliases are enforced (snake_case -> camelCase).
        2. Types are serialized (date -> str).
        """
        return self.model_dump(by_alias=True, mode="json")
