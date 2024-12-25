"""Tests for the Submission API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.api_client import APIClient
from src.models import Submission, SubmissionBrief, SubmissionLanguage, SubmissionStatus


@patch("requests.Session.get")
def test_get_submission_detail(mock_get, api_client):
    """Test getting submission details."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "friendly_name": "ACM",
        "problem": {
            "id": 1000,
            "title": "A+B",
            "url": "/OnlineJudge/api/v1/problem/42",
            "submit_url": "/OnlineJudge/api/v1/problem/42/submit",
            "html_url": "/OnlineJudge/problem/42",
        },
        "public": True,
        "language": "cpp",
        "score": 100,
        "message": "string",
        "details": {},
        "time_msecs": 2233,
        "memory_bytes": 1048576,
        "status": "accepted",
        "should_show_score": True,
        "created_at": "2024-12-25T10:12:35.728Z",
        "code_url": "/OnlineJudge/oj-submissions/42.code?X-Amz-Algorithm=...",
        "abort_url": "/OnlineJudge/api/v1/submission/42/abort",
        "html_url": "/OnlineJudge/code/42/",
    }
    mock_get.return_value = mock_response

    result = api_client.get_submission(42)
    assert isinstance(result, Submission)
    assert result.id == 42
    assert result.score == 100
    assert result.time_msecs == 2233
    assert result.memory_bytes == 1048576
    assert result.should_show_score is True
    assert result.status == SubmissionStatus.accepted
    mock_get.assert_called_once_with(f"{api_client.submission.base_url}/submission/42")


@patch("requests.Session.get")
def test_get_submissions_no_filters(mock_get, api_client):
    """Test getting submissions list without filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "submissions": [
            {
                "id": 42,
                "friendly_name": "ACM",
                "problem": {
                    "id": 1000,
                    "title": "A+B",
                    "url": "/OnlineJudge/api/v1/problem/42",
                    "submit_url": "/OnlineJudge/api/v1/problem/42/submit",
                    "html_url": "/OnlineJudge/problem/42",
                },
                "status": "accepted",
                "language": "cpp",
                "created_at": "2024-12-25T10:15:48.745Z",
                "url": "/OnlineJudge/api/v1/submission/42",
                "html_url": "/OnlineJudge/code/42",
            }
        ],
        "next": "/OnlineJudge/api/v1/endpoint?cursor=42",
    }
    mock_get.return_value = mock_response

    result = api_client.get_submissions()
    assert len(result) == 1
    assert isinstance(result[0], SubmissionBrief)
    submission = result[0]
    assert submission.id == 42
    assert submission.status == SubmissionStatus.accepted
    assert submission.language == SubmissionLanguage.cpp
    assert submission.problem.id == 1000
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={}
    )


@patch("requests.Session.get")
def test_get_submissions_with_username(mock_get, api_client):
    """Test getting submissions list filtered by username."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"submissions": []}
    mock_get.return_value = mock_response

    api_client.get_submissions(username="testuser")
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={"username": "testuser"}
    )


@patch("requests.Session.get")
def test_get_submissions_with_problem_id(mock_get, api_client):
    """Test getting submissions list filtered by problem ID."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"submissions": []}
    mock_get.return_value = mock_response

    api_client.get_submissions(problem_id=1000)
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={"problem_id": 1000}
    )


@patch("requests.Session.get")
def test_get_submissions_with_status(mock_get, api_client):
    """Test getting submissions list filtered by status."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"submissions": []}
    mock_get.return_value = mock_response

    api_client.get_submissions(status="accepted")
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={"status": "accepted"}
    )


@patch("requests.Session.get")
def test_get_submissions_with_language(mock_get, api_client):
    """Test getting submissions list filtered by language."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"submissions": []}
    mock_get.return_value = mock_response

    api_client.get_submissions(lang="cpp")
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={"lang": "cpp"}
    )


@patch("requests.Session.get")
def test_get_submissions_with_cursor(mock_get, api_client):
    """Test getting submissions list with cursor pagination."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "submissions": [],
        "next": "/OnlineJudge/api/v1/submission/?cursor=next_page",
    }
    mock_get.return_value = mock_response

    api_client.get_submissions(cursor="next_page")
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={"cursor": "next_page"}
    )


@patch("requests.Session.get")
def test_get_submissions_with_all_filters(mock_get, api_client):
    """Test getting submissions list with all filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"submissions": []}
    mock_get.return_value = mock_response

    api_client.get_submissions(
        username="testuser",
        problem_id=1000,
        status="accepted",
        lang="cpp",
        cursor="next_page",
    )
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/",
        params={
            "username": "testuser",
            "problem_id": 1000,
            "status": "accepted",
            "lang": "cpp",
            "cursor": "next_page",
        },
    )


@patch("requests.Session.post")
def test_abort_submission_success(mock_post, api_client):
    """Test successfully aborting a submission."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.abort_submission(42)
    mock_post.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/42/abort"
    )


@patch("requests.Session.post")
def test_abort_submission_not_found(mock_post, api_client):
    """Test aborting a non-existent submission."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.abort_submission(99999)


@patch("requests.Session.post")
def test_abort_submission_forbidden(mock_post, api_client):
    """Test aborting a submission without permission."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.abort_submission(42)


@patch("requests.Session.get")
def test_get_submission_not_found(mock_get, api_client):
    """Test getting a non-existent submission."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        api_client.get_submission(99999)


@patch("requests.Session.get")
def test_empty_submissions_list(mock_get, api_client):
    """Test handling of empty submissions list."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"submissions": []}
    mock_get.return_value = mock_response

    result = api_client.get_submissions()
    assert isinstance(result, list)
    assert len(result) == 0
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={}
    )


@patch("requests.Session.get")
def test_get_submission_with_all_fields(mock_get, api_client):
    """Test getting submission details with all possible fields."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "friendly_name": "ACM",
        "problem": {"id": 1000, "title": "A+B"},
        "public": True,
        "language": "cpp",
        "score": 100,
        "message": "Accepted",
        "details": {
            "testcases": [
                {"status": "accepted", "time": 0.001, "memory": 1024},
                {"status": "accepted", "time": 0.002, "memory": 2048},
            ]
        },
        "time_msecs": 2,
        "memory_bytes": 2048,
        "status": "accepted",
        "should_show_score": True,
        "created_at": "2023-01-01T00:00:00Z",
        "code_url": "/OnlineJudge/oj-submissions/42.code",
        "abort_url": "/OnlineJudge/api/v1/submission/42/abort",
        "html_url": "/OnlineJudge/code/42/",
    }
    mock_get.return_value = mock_response

    result = api_client.get_submission(42)
    assert isinstance(result, Submission)
    assert result.id == 42
    assert result.score == 100
    assert result.message == "Accepted"
    assert len(result.details["testcases"]) == 2
    assert result.time_msecs == 2
    assert result.memory_bytes == 2048
    assert result.status == SubmissionStatus.accepted
    assert result.should_show_score is True
    assert result.code_url == "/OnlineJudge/oj-submissions/42.code"
    assert result.abort_url == "/OnlineJudge/api/v1/submission/42/abort"
    mock_get.assert_called_once_with(f"{api_client.submission.base_url}/submission/42")
