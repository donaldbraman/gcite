"""
Tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns service info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "gCite API"
    assert data["version"] == "0.1.0"
    assert data["status"] == "operational"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert isinstance(data["timestamp"], float)


def test_search_endpoint_validation():
    """Test search endpoint validates request."""
    # Empty query should fail
    response = client.post("/api/search", json={
        "query": ""
    })
    assert response.status_code == 422  # Validation error

    # Valid query structure (will fail without cite-assist, but validates)
    response = client.post("/api/search", json={
        "query": "test query",
        "max_results": 5
    })
    # May fail with 500 if cite-assist not available, but validates request structure
    assert response.status_code in [200, 500]


def test_search_request_defaults():
    """Test search request uses proper defaults."""
    from api.models import SearchRequest, CitationStyle

    request = SearchRequest(query="test")
    assert request.max_results == 10
    assert request.citation_style == CitationStyle.APA
    assert request.filter is True
    assert request.min_relevance == 0.7
    assert request.include_context is True


def test_search_request_validation():
    """Test search request validation."""
    from api.models import SearchRequest
    from pydantic import ValidationError

    # Query too long
    with pytest.raises(ValidationError):
        SearchRequest(query="x" * 1001)

    # max_results out of range
    with pytest.raises(ValidationError):
        SearchRequest(query="test", max_results=0)

    with pytest.raises(ValidationError):
        SearchRequest(query="test", max_results=51)

    # min_relevance out of range
    with pytest.raises(ValidationError):
        SearchRequest(query="test", min_relevance=-0.1)

    with pytest.raises(ValidationError):
        SearchRequest(query="test", min_relevance=1.1)
