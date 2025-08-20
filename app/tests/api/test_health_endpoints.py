import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test cases for health check endpoints"""

    @pytest.mark.api
    def test_health_check_success(self):
        """Test health check endpoint returns success"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert "timestamp" in data
        assert "service" in data

    @pytest.mark.api
    def test_health_check_response_format(self):
        """Test health check response has correct format"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields exist
        required_fields = ["status", "timestamp", "service"]
        for field in required_fields:
            assert field in data
            assert data[field] is not None

    @pytest.mark.api
    def test_health_check_multiple_calls(self):
        """Test multiple health check calls return consistent results"""
        responses = []
        for _ in range(3):
            response = client.get("/health")
            responses.append(response)
        
        # All should be successful
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "UP"

    @pytest.mark.api
    def test_health_check_headers(self):
        """Test health check response headers"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
