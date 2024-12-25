"""
Base API client functionality.
"""

from typing import Dict, Generic, Optional, TypeVar

import requests

from ..config import Config

T = TypeVar("T")


class BaseAPIClient(Generic[T]):
    """Base class for API clients with common functionality."""

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        config: Optional[Config] = None,
    ):
        """
        Initialize base client.

        Args:
            session: Optional requests session to use
            config: Optional configuration instance
        """
        self.base_url = "https://acm.sjtu.edu.cn/OnlineJudge/api/v1"
        self.session = session or requests.Session()
        self.config = config or Config()

        # Load token if available
        self.token = self.config.token
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def _handle_response(self, response: requests.Response) -> T:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: Response from API request

        Returns:
            Dict: Parsed JSON response

        Raises:
            APIException: If request fails or returns error status
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise APIException(
                    "Authentication failed. Please login first.", response
                )
            elif response.status_code == 403:
                raise APIException(
                    "Permission denied. You don't have access to this resource.",
                    response,
                )
            else:
                raise APIException(f"API request failed: {str(e)}", response)

    def set_token(self, token: str):
        """
        Set authentication token.

        Args:
            token: Personal access token from ACM-OJ
        """
        self.token = token
        self.config.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})


class APIException(Exception):
    """Custom exception for API errors."""

    def __init__(self, message: str, response: requests.Response):
        super().__init__(message)
        self.response = response
