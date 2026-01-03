from enum import StrEnum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class HttpMethod(StrEnum):
    """
    HTTP methods used in API interactions.
    Using StrEnum (Python 3.11+) allows these to be used directly as strings.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ContentType(StrEnum):
    """
    Common HTTP Content-Type header values.
    """

    JSON = "application/json"
    XML = "application/xml"
    FORM_URLENCODED = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"
    TEXT = "text/plain"


class BaseSchema(BaseModel):
    """
    Base schema for EXTERNAL APIs (e.g., Restful-Booker).
    Automatically handles snake_case (Python) <-> camelCase (JSON) conversion.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        extra="ignore",
    )
