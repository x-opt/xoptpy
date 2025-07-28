"""
Custom exceptions for the xopt registry client.
"""


class XoptRegistryClientError(Exception):
    """Base exception for xopt registry client errors."""
    pass


class APIError(XoptRegistryClientError):
    """Exception raised when the API returns an error response."""
    
    def __init__(self, status_code: int, error_message: str, response_data: dict = None):
        self.status_code = status_code
        self.error_message = error_message
        self.response_data = response_data or {}
        super().__init__(f"API Error {status_code}: {error_message}")


class ConnectionError(XoptRegistryClientError):
    """Exception raised when unable to connect to the API."""
    pass


class TimeoutError(XoptRegistryClientError):
    """Exception raised when a request times out."""
    pass


class ValidationError(XoptRegistryClientError):
    """Exception raised when response validation fails."""
    pass


class AuthenticationError(APIError):
    """Exception raised for authentication failures (401)."""
    pass


class AuthorizationError(APIError):
    """Exception raised for authorization failures (403)."""
    pass


class NotFoundError(APIError):
    """Exception raised when a resource is not found (404)."""
    pass


class ConflictError(APIError):
    """Exception raised for conflicts (409)."""
    pass


class ServerError(APIError):
    """Exception raised for server errors (5xx)."""
    pass