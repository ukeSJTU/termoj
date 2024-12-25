"""Shared configuration for pytest"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from src.api_client import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = Mock(spec=requests.Response)
    response.status_code = 200
    response.json.return_value = {"test": "data"}
    return response
