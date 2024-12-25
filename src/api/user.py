"""
User-specific API client.
"""

from typing import List, Union

from ..models import Course, Problemset, Profile
from .base import BaseAPIClient


class UserClient(BaseAPIClient[Union[Profile, List[Course], List[Problemset]]]):
    """Client for user-related API endpoints."""

    def get_profile(self) -> Profile:
        """
        Get current user's profile.

        Returns:
            Profile: User profile information
        """
        response = self.session.get(f"{self.base_url}/user/profile")
        # return self._handle_response(response)
        data = self._handle_response(response)
        return Profile(**data)

    def get_user_courses(self) -> List[Course]:
        """
        Get list of courses the current user is enrolled in.

        Returns:
            List[Course]: List of enrolled course details
        """
        response = self.session.get(f"{self.base_url}/user/courses")
        data = self._handle_response(response)
        return [Course(**course) for course in data.get("courses", [])]

    def get_user_problemsets(self) -> List[Problemset]:
        """
        Get list of problemsets (contests/homework/exams) the current user is enrolled in.

        Returns:
            List[Problemset]: List of enrolled problemset details
        """
        response = self.session.get(f"{self.base_url}/user/problemsets")
        data = self._handle_response(response)
        return [Problemset(**problemset) for problemset in data.get("problemsets", [])]

    def get_oauth_token(self, data: dict) -> dict:
        """
        Get OAuth token using provided credentials.

        Args:
            data: Dictionary containing OAuth parameters (grant_type, client_id, client_secret, code, redirect_uri)

        Returns:
            dict: OAuth token response containing access_token, token_type, expires_in, and scope
        """
        response = self.session.post(f"{self.base_url}/oauth/token", data=data)
        return self._handle_response(response)
