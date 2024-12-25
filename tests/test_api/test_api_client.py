"""Tests for the API client module."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from src.api.base import APIException
from src.api_client import APIClient
from src.models import (
    Problem,
    ProblemBrief,
    ProblemsetType,
    Submission,
    SubmissionLanguage,
    SubmissionStatus,
)


def test_api_client_initialization():
    """Test APIClient initialization."""
    client = APIClient()
    assert isinstance(client.session, requests.Session)


def test_set_token(api_client):
    """Test setting authentication token."""
    test_token = "test-token"
    api_client.set_token(test_token)
    assert api_client.token == test_token
    assert api_client.session.headers["Authorization"] == f"Bearer {test_token}"


# Problem API Tests
@patch("requests.Session.get")
def test_get_problems_success(mock_get, api_client):
    """Test successful problems retrieval."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "problems": [
            {
                "id": 1000,
                "title": "A+B",
                "url": "/OnlineJudge/api/v1/problem/42",
                "submit_url": "/OnlineJudge/api/v1/problem/42/submit",
                "html_url": "/OnlineJudge/problem/42",
            }
        ]
    }
    mock_get.return_value = mock_response

    result = api_client.get_problems()
    assert len(result) == 1
    assert result[0].id == 1000
    assert result[0].title == "A+B"
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={}
    )


@patch("requests.Session.get")
def test_get_problems_with_filters(mock_get, api_client):
    """Test problems retrieval with filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"problems": []}
    mock_get.return_value = mock_response

    api_client.get_problems(keyword="test")
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={"keyword": "test"}
    )


@patch("requests.Session.get")
def test_get_problem_detail(mock_get, api_client):
    """Test getting problem details."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1000,
        "title": "A+B",
        "description": "Calculate A+B",
        "input": "Two integers A and B",
        "output": "One integer",
        "examples": [
            {
                "name": "Example 1",
                "input": "1 2",
                "output": "3",
                "description": "Basic case",
            }
        ],
        "languages_accepted": ["cpp", "python"],
        "allow_public_submissions": True,
    }
    mock_get.return_value = mock_response

    result = api_client.get_problem(1000)
    assert result.id == 1000
    assert result.title == "A+B"
    assert SubmissionLanguage.cpp in result.languages_accepted
    mock_get.assert_called_once()


@patch("requests.Session.post")
def test_submit_solution(mock_post, api_client):
    """Test submitting a solution."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 42}
    mock_post.return_value = mock_response

    code = """
    #include <stdio.h>
    int main() {
        printf("Hello World!\\n");
        return 0;
    }
    """
    result = api_client.submit_solution(1000, code, "cpp")
    assert result.id == 42
    mock_post.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/1000/submit",
        data={"language": "cpp", "code": code, "public": False},
    )


@patch("requests.Session.post")
def test_submit_solution_with_public(mock_post, api_client):
    """Test submitting a public solution."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 42}
    mock_post.return_value = mock_response

    code = "print('Hello World!')"
    result = api_client.problem.submit_solution(1000, code, "python", public=True)
    assert result.id == 42
    mock_post.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/1000/submit",
        data={"language": "python", "code": code, "public": True},
    )


# Submission API Tests
@patch("requests.Session.get")
def test_get_submissions(mock_get, api_client):
    """Test getting submissions list."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "submissions": [
            {
                "id": 42,
                "friendly_name": "ACM",
                "problem": {"id": 1000, "title": "A+B"},
                "status": "accepted",
                "language": "cpp",
                "created_at": "2023-01-01T00:00:00Z",
                "url": "/OnlineJudge/api/v1/submission/42",
                "html_url": "/OnlineJudge/code/42",
            }
        ]
    }
    mock_get.return_value = mock_response

    result = api_client.get_submissions()
    assert len(result) == 1
    assert result[0].id == 42
    assert result[0].status == SubmissionStatus.accepted
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={}
    )


@patch("requests.Session.get")
def test_get_submissions_with_filters(mock_get, api_client):
    """Test getting submissions list with filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"submissions": []}
    mock_get.return_value = mock_response

    api_client.get_submissions(
        username="testuser", problem_id=1000, status="accepted", lang="cpp"
    )

    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/",
        params={
            "username": "testuser",
            "problem_id": 1000,
            "status": "accepted",
            "lang": "cpp",
        },
    )


@patch("requests.Session.get")
def test_get_submission_detail(mock_get, api_client):
    """Test getting submission details."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "friendly_name": "ACM",
        "problem": {"id": 1000, "title": "A+B"},
        "public": True,
        "language": "cpp",
        "score": 100,
        "status": "accepted",
        "created_at": "2023-01-01T00:00:00Z",
        "code_url": "/OnlineJudge/oj-submissions/42.code",
        "html_url": "/OnlineJudge/code/42/",
    }
    mock_get.return_value = mock_response

    result = api_client.get_submission(42)
    assert result.id == 42
    assert result.public == True
    assert result.score == 100
    assert result.status == SubmissionStatus.accepted
    mock_get.assert_called_once()


@patch("requests.Session.post")
def test_abort_submission(mock_post, api_client):
    """Test aborting a submission."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.abort_submission(42)
    mock_post.assert_called_once()


# Course API Tests
@patch("requests.Session.get")
def test_get_courses(mock_get, api_client):
    """Test getting courses list with minimal data."""
    # Mock API Response
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "courses": [
            {
                "id": 42,
                "name": "Test Course",
                "description": "Test Description",
                "tag": None,
                "term": None,
                "url": "/OnlineJudge/api/v1/course/42",
                "join_url": "/OnlineJudge/api/v1/course/42/join",
                "quit_url": "/OnlineJudge/api/v1/course/42/quit",
                "html_url": "/OnlineJudge/course/42",
            }
        ]
    }
    mock_get.return_value = mock_response

    # Call Method
    courses, next_cursor = api_client.get_courses()

    # Assertions
    assert len(courses) == 1
    assert courses[0].id == 42
    assert courses[0].name == "Test Course"
    assert courses[0].description == "Test Description"
    assert next_cursor is None  # No pagination cursor in this response

    # Ensure correct API call
    mock_get.assert_called_once_with(f"{api_client.course.base_url}/course/", params={})


@patch("requests.Session.get")
def test_get_courses_with_filters(mock_get, api_client):
    """Test getting courses list with filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"courses": []}
    mock_get.return_value = mock_response

    api_client.get_courses(keyword="test", term=1, tag=2)
    mock_get.assert_called_once_with(
        f"{api_client.course.base_url}/course/",
        params={"keyword": "test", "term": 1, "tag": 2},
    )


@patch("requests.Session.get")
def test_get_course_detail(mock_get, api_client):
    """Test getting course details."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "name": "Test Course",
        "description": "Test Description",
        "tag": {"id": 1, "name": "Programming"},
        "term": {
            "id": 1,
            "name": "Fall 2023",
            "start_time": "2023-09-01T00:00:00Z",
            "end_time": "2024-01-31T00:00:00Z",
        },
        "url": "/OnlineJudge/api/v1/course/42",
        "join_url": "/OnlineJudge/api/v1/course/42/join",
        "quit_url": "/OnlineJudge/api/v1/course/42/quit",
        "html_url": "/OnlineJudge/course/42",
    }
    mock_get.return_value = mock_response

    result = api_client.get_course(42)
    assert result.id == 42
    assert result.name == "Test Course"
    assert result.tag.name == "Programming"
    assert result.term.name == "Fall 2023"
    mock_get.assert_called_once()


@patch("requests.Session.post")
def test_join_course(mock_post, api_client):
    """Test joining a course."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.join_course(42)
    mock_post.assert_called_once()


@patch("requests.Session.post")
def test_quit_course(mock_post, api_client):
    """Test quitting a course."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.quit_course(42)
    mock_post.assert_called_once()


@patch("requests.Session.get")
def test_get_course_problemsets(mock_get, api_client):
    """Test getting course problemsets."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "problemsets": [
            {
                "id": 42,
                "name": "Assignment 1",
                "description": "First Assignment",
                "allowed_languages": ["cpp", "python"],
                "start_time": "2023-09-01T00:00:00Z",
                "end_time": "2023-09-15T00:00:00Z",
                "type": "homework",
                "url": "/OnlineJudge/api/v1/problemset/42",
                "join_url": "/OnlineJudge/api/v1/problemset/42/join",
                "quit_url": "/OnlineJudge/api/v1/problemset/42/quit",
                "html_url": "/OnlineJudge/problemset/42",
            }
        ]
    }
    mock_get.return_value = mock_response

    result = api_client.get_course_problemsets(42)
    assert len(result) == 1
    assert result[0].id == 42
    assert result[0].name == "Assignment 1"
    assert SubmissionLanguage.cpp in result[0].allowed_languages
    mock_get.assert_called_once()


# Error Cases
@patch("requests.Session.get")
def test_unauthorized_request(mock_get, api_client):
    """Test handling of unauthorized requests."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        api_client.get_profile()
    assert "Authentication failed" in str(exc_info.value)


@patch("requests.Session.get")
def test_not_found_request(mock_get, api_client):
    """Test handling of not found resources."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        api_client.get_problem(99999)


@patch("requests.Session.post")
def test_forbidden_request(mock_post, api_client):
    """Test handling of forbidden requests."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.join_course(42)


@patch("requests.Session.get")
def test_server_error(mock_get, api_client):
    """Test handling of server errors."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        api_client.get_courses()


@patch("requests.Session.get")
def test_pagination_handling(mock_get, api_client):
    """Test handling of paginated responses."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "problems": [{"id": 1, "title": "Problem 1"}],
        "next": "/OnlineJudge/api/v1/problem/?cursor=42",
    }
    mock_get.return_value = mock_response

    result = api_client.get_problems()
    assert len(result) == 1
    assert result[0].id == 1
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={}
    )


@patch("requests.Session.get")
def test_empty_response_handling(mock_get, api_client):
    """Test handling of empty responses."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_get.return_value = mock_response

    result = api_client.get_user_courses()
    assert isinstance(result, list)
    assert len(result) == 0
    mock_get.assert_called_once_with(f"{api_client.user.base_url}/user/courses")


@patch("requests.Session.get")
def test_get_problem_with_all_fields(mock_get, api_client):
    """Test getting problem details with all possible fields."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1000,
        "title": "A+B",
        "description": "Calculate A+B",
        "input": "Two integers A and B",
        "output": "One integer",
        "examples": [
            {
                "name": "Example 1",
                "input": "1 2",
                "output": "3",
                "description": "Basic case",
            },
            {
                "name": "Example 2",
                "input": "-1 1",
                "output": "0",
                "description": "Negative numbers",
            },
        ],
        "example_input": "Sample input",
        "example_output": "Sample output",
        "data_range": "1 ≤ A, B ≤ 100",
        "languages_accepted": ["cpp", "python", "git"],
        "allow_public_submissions": True,
    }
    mock_get.return_value = mock_response

    result = api_client.get_problem(1000)
    assert result.id == 1000
    assert result.title == "A+B"
    assert len(result.examples) == 2
    assert result.data_range == "1 ≤ A, B ≤ 100"
    assert len(result.languages_accepted) == 3
    mock_get.assert_called_once_with(f"{api_client.problem.base_url}/problem/1000")


@patch("requests.Session.get")
def test_submission_with_all_fields(mock_get, api_client):
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
            "testcases": [{"status": "accepted", "time": 0.001, "memory": 1024}]
        },
        "time_msecs": 1,
        "memory_bytes": 1024,
        "status": "accepted",
        "should_show_score": True,
        "created_at": "2023-01-01T00:00:00Z",
        "code_url": "/OnlineJudge/oj-submissions/42.code",
        "abort_url": "/OnlineJudge/api/v1/submission/42/abort",
        "html_url": "/OnlineJudge/code/42/",
    }
    mock_get.return_value = mock_response

    result = api_client.get_submission(42)
    assert result.id == 42
    assert result.score == 100
    assert result.time_msecs == 1
    assert result.memory_bytes == 1024
    assert result.should_show_score is True
    assert result.details["testcases"][0]["status"] == "accepted"
    mock_get.assert_called_once_with(f"{api_client.submission.base_url}/submission/42")


@patch("requests.Session.get")
def test_course_with_all_fields(mock_get, api_client):
    """Test getting course details with all possible fields."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "name": "Advanced Programming",
        "description": "Course Description",
        "tag": {"id": 1, "name": "Programming"},
        "term": {
            "id": 1,
            "name": "Fall 2023",
            "start_time": "2023-09-01T00:00:00Z",
            "end_time": "2024-01-31T00:00:00Z",
        },
        "url": "/OnlineJudge/api/v1/course/42",
        "join_url": "/OnlineJudge/api/v1/course/42/join",
        "quit_url": "/OnlineJudge/api/v1/course/42/quit",
        "html_url": "/OnlineJudge/course/42",
    }
    mock_get.return_value = mock_response

    result = api_client.get_course(42)
    assert result.id == 42
    assert result.name == "Advanced Programming"
    assert result.tag.id == 1
    assert result.term.name == "Fall 2023"
    assert result.join_url == "/OnlineJudge/api/v1/course/42/join"
    assert result.quit_url == "/OnlineJudge/api/v1/course/42/quit"

    mock_get.assert_called_once_with(f"{api_client.course.base_url}/course/42")


@patch("requests.Session.get")
def test_malformed_response_handling(mock_get, api_client):
    """Test handling of malformed JSON responses."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_get.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        api_client.get_profile()
    assert "Invalid JSON" in str(exc_info.value)


@patch("requests.Session.get")
def test_get_problem_with_problemset_filter(mock_get, api_client):
    """Test getting problems with problemset filter."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"problems": []}
    mock_get.return_value = mock_response

    api_client.get_problems(problemset_id=42)
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={"problemset_id": 42}
    )


@patch("requests.Session.get")
def test_get_submissions_with_cursor(mock_get, api_client):
    """Test getting submissions with cursor pagination."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "submissions": [],
        "next": "/OnlineJudge/api/v1/submission/?cursor=42",
    }
    mock_get.return_value = mock_response

    api_client.get_submissions(cursor=42)
    mock_get.assert_called_once_with(
        f"{api_client.submission.base_url}/submission/", params={"cursor": 42}
    )


@patch("requests.Session.get")
def test_get_courses_with_cursor(mock_get, api_client):
    """Test getting courses with cursor pagination."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "courses": [],
        "next": "/OnlineJudge/api/v1/course/?cursor=42",
    }
    mock_get.return_value = mock_response

    api_client.get_courses(cursor=42)
    mock_get.assert_called_once_with(
        f"{api_client.course.base_url}/course/", params={"cursor": 42}
    )


@patch("requests.Session.post")
def test_abort_submission_forbidden(mock_post, api_client):
    """Test forbidden abort submission request."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Forbidden", response=mock_response
    )
    mock_post.return_value = mock_response

    with pytest.raises(APIException) as exc_info:
        api_client.abort_submission(42)

    assert exc_info.value.response.status_code == 403
    assert (
        str(exc_info.value)
        == "Permission denied. You don't have access to this resource."
    )


@patch("requests.Session.post")
def test_join_problemset(mock_post, api_client):
    """Test joining a problemset."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.problemset.join_problemset(42)
    mock_post.assert_called_once_with(
        f"{api_client.problem.base_url}/problemset/42/join"
    )


@patch("requests.Session.post")
def test_quit_problemset(mock_post, api_client):
    """Test quitting a problemset."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.problemset.quit_problemset(42)
    mock_post.assert_called_once_with(
        f"{api_client.problem.base_url}/problemset/42/quit"
    )


@patch("requests.Session.get")
def test_get_problemset_detail(mock_get, api_client):
    """Test getting problemset details."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "course": {"id": 1, "name": "Programming Course"},
        "name": "Final Exam",
        "description": "Course Final Exam",
        "allowed_languages": ["cpp", "python"],
        "start_time": "2023-12-20T09:00:00Z",
        "end_time": "2023-12-20T12:00:00Z",
        "late_submission_deadline": None,
        "type": "exam",
        "problems": [
            {"id": 1000, "title": "A+B", "url": "/OnlineJudge/api/v1/problem/1000"}
        ],
        "url": "/OnlineJudge/api/v1/problemset/42",
        "join_url": "/OnlineJudge/api/v1/problemset/42/join",
        "quit_url": "/OnlineJudge/api/v1/problemset/42/quit",
        "html_url": "/OnlineJudge/problemset/42",
    }
    mock_get.return_value = mock_response

    result = api_client.problemset.get_problemset(42)
    assert result.id == 42
    assert result.type == ProblemsetType.exam
    assert result.course.name == "Programming Course"
    assert len(result.problems) == 1
    mock_get.assert_called_once_with(f"{api_client.problem.base_url}/problemset/42")


@patch("requests.Session.get")
def test_submission_status_variations(mock_get, api_client):
    """Test different submission status variations."""
    statuses = [
        "accepted",
        "wrong_answer",
        "compile_error",
        "runtime_error",
        "time_limit_exceeded",
        "memory_limit_exceeded",
        "disk_limit_exceeded",
        "memory_leak",
        "pending",
        "compiling",
        "judging",
        "void",
        "aborted",
        "skipped",
        "system_error",
        "bad_problem",
        "unknown_error",
    ]

    for status in statuses:
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "submissions": [
                {
                    "id": 42,
                    "friendly_name": "ACM",
                    "problem": {"id": 1000, "title": "A+B"},
                    "status": status,
                    "language": "cpp",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = api_client.get_submissions(status=status)
        assert result[0].status.value == status
        mock_get.assert_called_with(
            f"{api_client.submission.base_url}/submission/", params={"status": status}
        )


@patch("requests.Session.get")
def test_language_variations(mock_get, api_client):
    """Test different programming language variations."""
    languages = ["cpp", "python", "git", "verilog", "quiz"]

    for lang in languages:
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "submissions": [{"id": 42, "language": lang, "status": "accepted"}]
        }
        mock_get.return_value = mock_response

        result = api_client.get_submissions(lang=lang)
        assert result[0].language.value == lang
        mock_get.assert_called_with(
            f"{api_client.submission.base_url}/submission/", params={"lang": lang}
        )
