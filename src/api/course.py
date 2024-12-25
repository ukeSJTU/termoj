"""
Course-specific API client.
"""

from typing import List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlparse

from ..models import Course, Problemset
from .base import APIException, BaseAPIClient


class CourseClient(BaseAPIClient[Union[Course, List[Course], List[Problemset]]]):
    """Client for course-related API endpoints."""

    def get_courses(
        self,
        keyword: Optional[str] = None,
        term: Optional[int] = None,
        tag: Optional[int] = None,
        cursor: Optional[int] = None,
    ) -> Tuple[List[Course], Optional[int]]:
        """
        Get list of courses with optional filters.

        Args:
            keyword: Optional search keyword to filter courses
            term: Optional term ID to filter courses
            tag: Optional tag ID to filter courses
            cursor: Optional pagination cursor

        Returns:
            List[Course]: List of course details
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if term:
            params["term"] = term
        if tag:
            params["tag"] = tag
        if cursor:
            params["cursor"] = cursor

        response = self.session.get(f"{self.base_url}/course/", params=params)
        data = self._handle_response(response)
        courses = [Course(**course) for course in data.get("courses", [])]

        # Extract cursor from 'next' query param
        next_cursor = None
        if data.get("next"):
            parsed_url = urlparse(data["next"])
            query_params = parse_qs(parsed_url.query)
            next_cursor = query_params.get("cursor", [None])[0]

        return courses, next_cursor

    def get_course(self, course_id: int) -> Course:
        """
        Get detailed information about a specific course.

        Args:
            course_id: ID of the course

        Returns:
            Course: Course details including name, description, etc.
        """
        response = self.session.get(f"{self.base_url}/course/{course_id}")
        data = self._handle_response(response)
        return Course(**data)

    def join_course(self, course_id: int) -> None:
        """
        Join a course.

        Args:
            course_id: ID of the course to join
        """
        response = self.session.post(f"{self.base_url}/course/{course_id}/join")

        if response.status_code == 204:
            # Success with no content
            return

        if response.status_code == 403:
            raise APIException(
                "You do not have permission to join this course.", response
            )

        self._handle_response(response)

    def quit_course(self, course_id: int) -> None:
        """
        Quit a course.

        Args:
            course_id: ID of the course to quit
        """
        response = self.session.post(f"{self.base_url}/course/{course_id}/quit")
        self._handle_response(response)

    def get_course_problemsets(self, course_id: int) -> List[Problemset]:
        """
        Get list of problemsets for a specific course.

        Args:
            course_id: ID of the course

        Returns:
            List[Problemset]: List of problemset details
        """
        response = self.session.get(f"{self.base_url}/course/{course_id}/problemsets")
        data = self._handle_response(response)
        return [Problemset(**problemset) for problemset in data.get("problemsets", [])]
