"""
Main API client that composes specialized clients for different resource types.
"""

import logging
from typing import Dict, List, Literal, Optional, Tuple

import requests

from .api.course import CourseClient
from .api.problem import ProblemClient
from .api.problemset import ProblemsetClient
from .api.submission import SubmissionClient
from .api.user import UserClient
from .config import Config
from .models import (
    Course,
    Problem,
    ProblemBrief,
    Problemset,
    Profile,
    Submission,
    SubmissionBrief,
)


class APIClient:
    """Client for making requests to the ACM-OJ API."""

    def __init__(self):
        """Initialize API client with specialized clients for each resource type."""
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.config = Config()

        self.logger.info("Initializing API client")
        # Initialize specialized clients
        self.user = UserClient(session=self.session, config=self.config)
        self.problem = ProblemClient(session=self.session, config=self.config)
        self.submission = SubmissionClient(session=self.session, config=self.config)
        self.course = CourseClient(session=self.session, config=self.config)
        self.problemset = ProblemsetClient(session=self.session, config=self.config)

        self._load_token()
        self.logger.info("API client initialization complete")

    def _load_token(self):
        """Load authentication token from config."""
        self.token = self.config.token
        if self.token:
            self.logger.info("Loading authentication token from config")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        else:
            self.logger.warning("No authentication token found in config")

    def set_token(self, token: str):
        """
        Set authentication token.

        Args:
            token: Personal access token from ACM-OJ
        """
        self.logger.info("Setting new authentication token")
        self.token = token
        self.config.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

        # Update token for all clients
        for client in [
            self.user,
            self.problem,
            self.submission,
            self.course,
            self.problemset,
        ]:
            client.set_token(token)
        self.logger.info("Authentication token updated for all clients")

    def clear_token(self):
        """
        Clear authentication token.

        This method removes the authentication token from the main client
        and all child clients, and clears the Authorization header from the session.
        """
        self.logger.info("Clearing user authentication token")

        # 清除主客户端的 Token
        self.token = None
        self.config.token = None

        # 移除 Authorization 头部
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        # 更新所有子客户端的 Token
        for client in [
            self.user,
            self.problem,
            self.submission,
            self.course,
            self.problemset,
        ]:
            if hasattr(client, "set_token"):
                client.set_token(None)

        self.logger.info("Authentication token cleared for all clients")

    # User endpoints delegated to UserClient
    def get_profile(self) -> Profile:
        """Get current user's profile."""
        self.logger.info("Fetching user profile")
        try:
            profile = self.user.get_profile()
            self.logger.info("Successfully retrieved user profile")
            return profile
        except Exception as e:
            self.logger.error(f"Failed to fetch user profile: {str(e)}")
            raise

    def get_user_courses(self) -> List[Course]:
        """Get list of courses the current user is enrolled in."""
        return self.user.get_user_courses()

    def get_user_problemsets(self) -> List[Problemset]:
        """Get list of problemsets the current user is enrolled in."""
        return self.user.get_user_problemsets()

    # Problem endpoints delegated to ProblemClient
    def get_problems(
        self,
        keyword: Optional[str] = None,
        problemset_id: Optional[int] = None,
        cursor: Optional[int] = None,
    ) -> List[ProblemBrief]:
        """Fetch available problems from the platform."""
        return self.problem.get_problems(keyword, problemset_id, cursor)

    def get_problem(self, problem_id: int) -> Problem:
        """Get detailed information about a specific problem."""
        return self.problem.get_problem(problem_id)

    def submit_solution(
        self, problem_id: int, code: str, language: str, public: bool = False
    ) -> Submission:
        """Submit a solution to a problem."""
        self.logger.info(f"Submitting solution for problem {problem_id} in {language}")
        try:
            submission = self.problem.submit_solution(
                problem_id, code, language, public
            )
            self.logger.info(
                f"Successfully submitted solution. Submission ID: {submission.id}"
            )
            return submission
        except Exception as e:
            self.logger.error(f"Failed to submit solution: {str(e)}")
            raise

    # Submission endpoints delegated to SubmissionClient
    def get_submission(self, submission_id: int) -> Submission:
        """Get status and details of a submission."""
        return self.submission.get_submission(submission_id)

    def get_submissions(
        self,
        username: Optional[str] = None,
        problem_id: Optional[int] = None,
        status: Optional[str] = None,
        lang: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> List[SubmissionBrief]:
        """
        Get list of submissions with optional filters.
        """

        return self.submission.get_submissions(
            username, problem_id, status, lang, cursor
        )

    def abort_submission(self, submission_id: int) -> None:
        """Abort a running submission."""
        return self.submission.abort_submission(submission_id)

    # Course endpoints delegated to CourseClient
    def get_courses(
        self,
        keyword: Optional[str] = None,
        term: Optional[int] = None,
        tag: Optional[int] = None,
        cursor: Optional[int] = None,
    ) -> Tuple[List[Course], Optional[int]]:
        """Get list of courses with optional filters."""
        return self.course.get_courses(keyword, term, tag, cursor)

    def get_course(self, course_id: int) -> Course:
        """Get detailed information about a specific course."""
        return self.course.get_course(course_id)

    def join_course(self, course_id: int) -> None:
        """Join a course."""
        return self.course.join_course(course_id)

    def quit_course(self, course_id: int) -> None:
        """Quit a course."""
        return self.course.quit_course(course_id)

    def get_course_problemsets(self, course_id: int) -> List[Problemset]:
        """Get list of problemsets for a specific course."""
        return self.course.get_course_problemsets(course_id)

    # Problemset endpoints delegated to ProblemsetClient
    def get_problemset(self, problemset_id: int) -> Problemset:
        """Get details of a specific problemset."""
        return self.problemset.get_problemset(problemset_id)

    def join_problemset(self, problemset_id: int) -> None:
        """Join a problemset."""
        return self.problemset.join_problemset(problemset_id)

    def quit_problemset(self, problemset_id: int) -> None:
        """Quit a problemset."""
        return self.problemset.quit_problemset(problemset_id)
