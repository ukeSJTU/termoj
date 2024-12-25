"""
Submission-specific API client.
"""

from typing import Dict, List, Optional, Union

import requests

from ..models import Submission, SubmissionBrief
from .base import BaseAPIClient


class SubmissionClient(BaseAPIClient[Union[Submission, List[SubmissionBrief]]]):
    """Client for submission-related API endpoints."""

    def get_submission(self, submission_id: int) -> Submission:
        """
        Get status and details of a submission.

        Args:
            submission_id: ID of the submission

        Returns:
            Submission: Submission details including status, score, runtime, etc.
        """
        response = self.session.get(f"{self.base_url}/submission/{submission_id}")
        data = self._handle_response(response)
        return Submission(**data)

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

        Args:
            username: Filter by username.
            problem_id: Filter by problem ID.
            status: Filter by submission status.
            lang: Filter by programming language.
            cursor: Pagination cursor.

        Returns:
            List[SubmissionBrief]: List of submission brief details.
        """
        params = {
            "username": username,
            "problem_id": problem_id,
            "status": status,
            "lang": lang,
            "cursor": cursor,
        }
        # Remove None values to avoid sending them as query parameters
        params = {k: v for k, v in params.items() if v is not None}

        response = self.session.get(f"{self.base_url}/submission/", params=params)
        data = self._handle_response(response)
        return [
            SubmissionBrief(**submission) for submission in data.get("submissions", [])
        ]

    def abort_submission(self, submission_id: int) -> None:
        """
        Abort a running submission.

        Args:
            submission_id: ID of the submission to abort
        """
        response = self.session.post(
            f"{self.base_url}/submission/{submission_id}/abort"
        )
        self._handle_response(response)
