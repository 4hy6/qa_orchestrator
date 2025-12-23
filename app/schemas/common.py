from enum import StrEnum


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
