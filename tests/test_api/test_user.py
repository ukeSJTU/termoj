"""Tests for the User API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.api_client import APIClient
from src.models import Course, Problemset, ProblemsetType, Profile


@patch("requests.Session.get")
def test_get_profile_success(mock_get, api_client):
    """Test successful profile retrieval."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "username": "username",
        "friendly_name": "friendly_name",
        "student_id": "520030910001",
    }
    mock_get.return_value = mock_response

    result = api_client.get_profile()
    assert isinstance(result, Profile)
    assert result.username == "username"
    assert result.friendly_name == "friendly_name"
    assert result.student_id == "520030910001"
    mock_get.assert_called_once()


@patch("requests.Session.get")
def test_get_user_courses(mock_get, api_client):
    """Test getting user's courses."""
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

    result = api_client.get_user_courses()
    assert len(result) == 1
    assert isinstance(result[0], Course)
    assert result[0].id == 42
    assert result[0].name == "Test Course"
    mock_get.assert_called_once()


@patch("requests.Session.get")
def test_get_user_problemsets(mock_get, api_client):
    """Test getting user's problemsets."""
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

    result = api_client.get_user_problemsets()
    assert len(result) == 1
    assert isinstance(result[0], Problemset)
    assert result[0].id == 42
    assert result[0].name == "Assignment 1"
    assert result[0].type == ProblemsetType.homework
    mock_get.assert_called_once()


@patch("requests.Session.post")
def test_oauth_token_request(mock_post, api_client):
    """Test OAuth token request."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "acmoj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "token_type": "bearer",
        "expires_in": 31536000,
        "scope": "user:profile problem:read",
    }
    mock_post.return_value = mock_response

    data = {
        "grant_type": "authorization_code",
        "client_id": "test_client",
        "client_secret": "test_secret",
        "code": "acmoj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "redirect_uri": "http://localhost:8000/callback",
    }
    result = api_client.user.get_oauth_token(data)

    assert result["access_token"] == "acmoj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    assert result["token_type"] == "bearer"
    assert result["expires_in"] == 31536000
    mock_post.assert_called_once_with(
        f"{api_client.user.base_url}/oauth/token", data=data
    )
