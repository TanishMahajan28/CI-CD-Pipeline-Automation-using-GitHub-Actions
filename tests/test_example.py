"""
Example unit tests for the application.
"""
import pytest


class TestExample:
    """Example test class."""
    
    def test_example_pass(self):
        """Example passing test."""
        assert True
        
    def test_addition(self):
        """Test basic math operation."""
        result = 2 + 2
        assert result == 4
        
    @pytest.mark.unit
    def test_with_fixture(self, sample_data):
        """Test using a fixture."""
        assert "user" in sample_data
        assert sample_data["user"]["username"] == "testuser"