"""Tests for the Problemset API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.models import Problemset, ProblemsetType


@patch("requests.Session.get")
def test_get_problemset_success(mock_get, api_client):
    """Test successful problemset retrieval."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
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
    mock_get.return_value = mock_response

    result = api_client.problemset.get_problemset(42)
    assert isinstance(result, Problemset)
    assert result.id == 42
    assert result.name == "Assignment 1"
    assert result.type == ProblemsetType.homework
    mock_get.assert_called_once_with(f"{api_client.problemset.base_url}/problemset/42")


@patch("requests.Session.post")
def test_join_problemset_success(mock_post, api_client):
    """Test successful problemset join."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.problemset.join_problemset(42)
    mock_post.assert_called_once_with(
        f"{api_client.problemset.base_url}/problemset/42/join"
    )


@patch("requests.Session.post")
def test_quit_problemset_success(mock_post, api_client):
    """Test successful problemset quit."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 204
    mock_post.return_value = mock_response

    api_client.problemset.quit_problemset(42)
    mock_post.assert_called_once_with(
        f"{api_client.problemset.base_url}/problemset/42/quit"
    )


@patch("requests.Session.get")
def test_get_problemset_failure(mock_get, api_client):
    """Test problemset retrieval failure."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        api_client.problemset.get_problemset(42)
    mock_get.assert_called_once()


@patch("requests.Session.post")
def test_join_problemset_failure(mock_post, api_client):
    """Test problemset join failure."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.problemset.join_problemset(42)
    mock_post.assert_called_once()


@patch("requests.Session.post")
def test_quit_problemset_failure(mock_post, api_client):
    """Test problemset quit failure."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 403
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.problemset.quit_problemset(42)
    mock_post.assert_called_once()
