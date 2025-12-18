"""
Conftest file for pytest fixtures and configuration.
"""
import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "user": {
            "username": "testuser",
            "email": "test@example.com"
        }
    }