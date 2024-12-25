"""
Problem-specific API client.
"""

from typing import List, Literal, Optional, Union

from ..models import Problem, ProblemBrief, Submission
from .base import BaseAPIClient


class ProblemClient(BaseAPIClient[Union[Problem, List[ProblemBrief], Submission]]):
    """Client for problem-related API endpoints."""

    def get_problems(
        self,
        keyword: Optional[str] = None,
        problemset_id: Optional[int] = None,
        cursor: Optional[int] = None,
    ) -> List[ProblemBrief]:
        """
        Fetch available problems from the platform.

        Args:
            keyword: Optional search keyword to filter problems

        Returns:
            List[ProblemBrief]: List of problem briefs containing basic details
        """
        params = {}
        if keyword:
            params["keyword"] = keyword
        if problemset_id:
            params["problemset_id"] = problemset_id
        if cursor:
            params["cursor"] = cursor

        response = self.session.get(f"{self.base_url}/problem/", params=params)
        data = self._handle_response(response)
        return [ProblemBrief(**problem) for problem in data.get("problems", [])]

    def get_problem(self, problem_id: int) -> Problem:
        """
        Get detailed information about a specific problem.

        Args:
            problem_id: ID of the problem

        Returns:
            Problem: Problem details including description, input/output format, etc.
        """
        response = self.session.get(f"{self.base_url}/problem/{problem_id}")
        data = self._handle_response(response)
        return Problem(**data)

    def submit_solution(
        self, problem_id: int, code: str, language: str, public: bool = False
    ) -> Submission:
        """
        Submit a solution to a problem.

        Args:
            problem_id: ID of the problem
            code: Source code of the solution
            language: Programming language of the solution ('cpp', 'python', etc.)

        Returns:
            Submission: Submission result details including submission ID and status
        """
        data = {"language": language, "code": code, "public": public}
        response = self.session.post(
            f"{self.base_url}/problem/{problem_id}/submit", data=data
        )
        data = self._handle_response(response)
        return Submission(**data)
