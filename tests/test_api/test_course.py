"""Tests for the Course API client."""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
import requests

from src.models import Course, Problemset, ProblemsetType


@patch("requests.Session.get")
def test_get_courses_success(mock_get, api_client):
    """Test successful courses list retrieval with pagination."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "courses": [
            {
                "id": 42,
                "name": "string",
                "description": "string",
                "tag": {"id": 42, "name": "string"},
                "term": {
                    "id": 42,
                    "name": "string",
                    "start_time": "2024-12-25T10:34:21.962Z",
                    "end_time": "2024-12-25T10:34:21.962Z",
                },
                "url": "/OnlineJudge/api/v1/course/42",
                "join_url": "/OnlineJudge/api/v1/course/42/join",
                "quit_url": "/OnlineJudge/api/v1/course/42/quit",
                "html_url": "/OnlineJudge/course/42",
            }
        ],
        "next": "/OnlineJudge/api/v1/endpoint?cursor=42",
    }
    mock_get.return_value = mock_response

    courses, next_cursor = api_client.get_courses()

    assert len(courses) == 1
    assert isinstance(courses[0], Course)
    assert courses[0].id == 42
    assert courses[0].name == "string"
    assert courses[0].description == "string"
    assert courses[0].tag.id == 42
    assert courses[0].tag.name == "string"
    assert courses[0].term.id == 42
    assert courses[0].term.name == "string"
    assert courses[0].term.start_time == datetime(
        2024, 12, 25, 10, 34, 21, 962000, tzinfo=timezone.utc
    )
    assert courses[0].term.end_time == datetime(
        2024, 12, 25, 10, 34, 21, 962000, tzinfo=timezone.utc
    )

    assert next_cursor == "42"

    mock_get.assert_called_once_with(f"{api_client.course.base_url}/course/", params={})


@patch("requests.Session.get")
def test_get_courses_with_filters(mock_get, api_client):
    """Test courses list retrieval with filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"courses": []}
    mock_get.return_value = mock_response

    api_client.course.get_courses(keyword="test", term=1, tag=2, cursor=100)
    mock_get.assert_called_once_with(
        f"{api_client.course.base_url}/course/",
        params={"keyword": "test", "term": 1, "tag": 2, "cursor": 100},
    )


@patch("requests.Session.get")
def test_get_courses_with_cursor(mock_get, api_client):
    """Test courses list retrieval with cursor."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"courses": []}
    mock_get.return_value = mock_response

    api_client.course.get_courses(cursor=100)
    mock_get.assert_called_once_with(
        f"{api_client.course.base_url}/course/",
        params={"cursor": 100},
    )


@patch("requests.Session.get")
def test_get_course_success(mock_get, api_client):
    """Test successful course details retrieval."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 42,
        "name": "string",
        "description": "string",
        "tag": {"id": 42, "name": "string"},
        "term": {
            "id": 42,
            "name": "string",
            "start_time": "2024-12-25T10:35:12.747Z",
            "end_time": "2024-12-25T10:35:12.747Z",
        },
        "url": "/OnlineJudge/api/v1/course/42",
        "join_url": "/OnlineJudge/api/v1/course/42/join",
        "quit_url": "/OnlineJudge/api/v1/course/42/quit",
        "html_url": "/OnlineJudge/course/42",
    }
    mock_get.return_value = mock_response

    result = api_client.course.get_course(42)
    assert isinstance(result, Course)
    assert result.id == 42
    assert result.name == "string"
    assert result.description == "string"
    assert result.tag.id == 42
    assert result.tag.name == "string"
    assert result.term.id == 42
    assert result.term.name == "string"
    mock_get.assert_called_once_with(f"{api_client.course.base_url}/course/42")


@patch("requests.Session.post")
def test_join_course_success(mock_post, api_client):
    """Test successful course join."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.course.join_course(42)
    mock_post.assert_called_once_with(f"{api_client.course.base_url}/course/42/join")


@patch("requests.Session.post")
def test_quit_course_success(mock_post, api_client):
    """Test successful course quit."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.course.quit_course(42)
    mock_post.assert_called_once_with(f"{api_client.course.base_url}/course/42/quit")


@patch("requests.Session.get")
def test_get_course_problemsets_success(mock_get, api_client):
    """Test successful course problemsets retrieval."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "problemsets": [
            {
                "id": 42,
                "name": "Assignment 1",
                "description": "First Assignment",
                "type": "homework",
                "start_time": "2023-09-01T00:00:00Z",
                "end_time": "2023-09-15T00:00:00Z",
                "late_submission_deadline": None,
                "allowed_languages": ["cpp", "python"],
                "url": "/OnlineJudge/api/v1/problemset/42",
                "join_url": "/OnlineJudge/api/v1/problemset/42/join",
                "quit_url": "/OnlineJudge/api/v1/problemset/42/quit",
                "html_url": "/OnlineJudge/problemset/42",
            }
        ]
    }
    mock_get.return_value = mock_response

    result = api_client.course.get_course_problemsets(42)
    assert len(result) == 1
    assert isinstance(result[0], Problemset)
    assert result[0].id == 42
    assert result[0].name == "Assignment 1"
    assert result[0].type == ProblemsetType.homework
    mock_get.assert_called_once_with(
        f"{api_client.course.base_url}/course/42/problemsets"
    )


@patch("requests.Session.get")
def test_get_course_failure(mock_get, api_client):
    """Test course retrieval failure."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        api_client.course.get_course(42)
    mock_get.assert_called_once()


@patch("requests.Session.post")
def test_join_course_failure(mock_post, api_client):
    """Test course join failure."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.course.join_course(42)
    mock_post.assert_called_once()


@patch("requests.Session.post")
def test_quit_course_failure(mock_post, api_client):
    """Test course quit failure."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.course.quit_course(42)
    mock_post.assert_called_once()


@patch("requests.Session.get")
def test_get_course_problemsets_failure(mock_get, api_client):
    """Test course problemsets retrieval failure."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        api_client.course.get_course_problemsets(42)
    mock_get.assert_called_once()
