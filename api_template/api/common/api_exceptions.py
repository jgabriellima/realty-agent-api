import logging
from http import HTTPStatus
from typing import Optional

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """Base class for all API exceptions."""

    def __init__(self, status_code: int, error_code: str, error_msg: Optional[str] = None):
        self.status_code = HTTPStatus(status_code)
        self.error_code = error_code
        self.error_msg = error_msg
        logger.error(
            f"Error: {self.error_code}, Message: {self.error_msg}, Status: {self.status_code}"
        )

    def to_dict(self):
        return {"error": {"code": self.error_code, "message": self.error_msg}}


class RequestError(BaseAPIException):
    """Exception raised for request errors."""


class ValidationError(BaseAPIException):
    """Exception raised for validation errors."""
