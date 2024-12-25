"""Tests for the Problem API client."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.api_client import APIClient
from src.models import Problem, ProblemBrief, Submission, SubmissionLanguage


@pytest.fixture
def api_client():
    """Create an API client instance for testing."""
    return APIClient()


@patch("requests.Session.get")
def test_get_problems_no_filters(mock_get, api_client):
    """Test getting problems list without filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "problems": [
            {
                "id": 1000,
                "title": "A+B",
                "url": "/OnlineJudge/api/v1/problem/1000",
                "submit_url": "/OnlineJudge/api/v1/problem/1000/submit",
                "html_url": "/OnlineJudge/problem/1000",
            }
        ]
    }
    mock_get.return_value = mock_response

    result = api_client.get_problems()
    assert len(result) == 1
    assert isinstance(result[0], ProblemBrief)
    assert result[0].id == 1000
    assert result[0].title == "A+B"
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={}
    )


@patch("requests.Session.get")
def test_get_problems_with_keyword(mock_get, api_client):
    """Test getting problems list with keyword filter."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"problems": []}
    mock_get.return_value = mock_response

    api_client.get_problems(keyword="test")
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={"keyword": "test"}
    )


@patch("requests.Session.get")
def test_get_problems_with_problemset(mock_get, api_client):
    """Test getting problems list with problemset filter."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"problems": []}
    mock_get.return_value = mock_response

    api_client.get_problems(problemset_id=42)
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={"problemset_id": 42}
    )


@patch("requests.Session.get")
def test_get_problems_with_cursor(mock_get, api_client):
    """Test getting problems list with cursor pagination."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "problems": [],
        "next": "/OnlineJudge/api/v1/problem/?cursor=42",
    }
    mock_get.return_value = mock_response

    api_client.get_problems(cursor=42)
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={"cursor": 42}
    )


@patch("requests.Session.get")
def test_get_problems_with_all_filters(mock_get, api_client):
    """Test getting problems list with all filters."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"problems": []}
    mock_get.return_value = mock_response

    api_client.get_problems(keyword="test", problemset_id=42, cursor=10)
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/",
        params={"keyword": "test", "problemset_id": 42, "cursor": 10},
    )


@patch("requests.Session.get")
def test_get_problem_detail(mock_get, api_client):
    """Test getting problem details."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1000,
        "title": "A+B",
        "description": "string",
        "input": "string",
        "output": "string",
        "examples": [
            {
                "name": "string",
                "input": "string",
                "output": "string",
                "description": "string",
            }
        ],
        "example_input": "string",
        "example_output": "string",
        "data_range": "string",
        "languages_accepted": ["cpp"],
        "allow_public_submissions": True,
    }
    mock_get.return_value = mock_response

    result = api_client.get_problem(1000)
    assert isinstance(result, Problem)
    assert result.id == 1000
    assert result.title == "A+B"
    assert result.description == "string"
    assert len(result.examples) == 1
    assert SubmissionLanguage.cpp in result.languages_accepted
    mock_get.assert_called_once_with(f"{api_client.problem.base_url}/problem/1000")


@patch("requests.Session.post")
def test_submit_solution_private(mock_post, api_client):
    """Test submitting a private solution."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 42,
        "friendly_name": "ACM",
        "problem": {"id": 1000, "title": "A+B"},
        "public": False,
        "language": "cpp",
        "status": "pending",
    }
    mock_post.return_value = mock_response

    code = """
    #include <stdio.h>
    int main() {
        int a, b;
        scanf("%d %d", &a, &b);
        printf("%d\\n", a + b);
        return 0;
    }
    """
    result = api_client.submit_solution(1000, code, "cpp")
    assert isinstance(result, Submission)
    assert result.id == 42
    assert result.language == SubmissionLanguage.cpp
    assert result.public == False
    mock_post.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/1000/submit",
        data={"language": "cpp", "code": code, "public": False},
    )


@patch("requests.Session.post")
def test_submit_solution_public(mock_post, api_client):
    """Test submitting a public solution."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 42,
        "friendly_name": "ACM",
        "problem": {"id": 1000, "title": "A+B"},
        "public": True,
        "language": "python",
        "status": "pending",
    }
    mock_post.return_value = mock_response

    code = "print(sum(map(int, input().split())))"
    result = api_client.submit_solution(1000, code, "python", public=True)
    assert isinstance(result, Submission)
    assert result.id == 42
    assert result.language == SubmissionLanguage.python
    assert result.public == True
    mock_post.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/1000/submit",
        data={"language": "python", "code": code, "public": True},
    )


@patch("requests.Session.get")
def test_get_problem_not_found(mock_get, api_client):
    """Test getting a non-existent problem."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        api_client.get_problem(99999)


@patch("requests.Session.post")
def test_submit_solution_invalid_language(mock_post, api_client):
    """Test submitting a solution with invalid language."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 400
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response

    with pytest.raises(Exception):
        api_client.submit_solution(1000, "code", "invalid_lang")


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
    assert isinstance(result, Problem)
    assert result.id == 1000
    assert result.title == "A+B"
    assert len(result.examples) == 2
    assert result.data_range == "1 ≤ A, B ≤ 100"
    assert len(result.languages_accepted) == 3
    assert result.allow_public_submissions is True
    mock_get.assert_called_once_with(f"{api_client.problem.base_url}/problem/1000")


@patch("requests.Session.get")
def test_empty_problems_list(mock_get, api_client):
    """Test handling of empty problems list."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"problems": []}
    mock_get.return_value = mock_response

    result = api_client.get_problems()
    assert isinstance(result, list)
    assert len(result) == 0
    mock_get.assert_called_once_with(
        f"{api_client.problem.base_url}/problem/", params={}
    )
