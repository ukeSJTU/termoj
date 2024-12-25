"""
Problemset-specific API client.
"""

from ..models import Problemset
from .base import APIException, BaseAPIClient


class ProblemsetClient(BaseAPIClient[Problemset]):
    """Client for problemset-related API endpoints."""

    def get_problemset(self, problemset_id: int) -> Problemset:
        """
        Get details of a specific problemset.

        Args:
            problemset_id: ID of the problemset to retrieve

        Returns:
            Problemset: Problemset details
        """
        response = self.session.get(f"{self.base_url}/problemset/{problemset_id}")
        data = self._handle_response(response)
        return Problemset(**data)

    def join_problemset(self, problemset_id: int) -> None:
        """
        Join a problemset.

        Args:
            problemset_id: ID of the problemset to join

        Raises:
            Exception: If join fails or user doesn't have permission
        """
        response = self.session.post(f"{self.base_url}/problemset/{problemset_id}/join")
        if response.status_code == 204:
            # Success with no content
            return

        if response.status_code == 403:
            raise APIException(
                "You do not have permission to join this problemset.", response
            )

        self._handle_response(response)

    def quit_problemset(self, problemset_id: int) -> None:
        """
        Quit a problemset.

        Args:
            problemset_id: ID of the problemset to quit

        Raises:
            Exception: If quit fails or user doesn't have permission
        """
        response = self.session.post(f"{self.base_url}/problemset/{problemset_id}/quit")
        self._handle_response(response)
