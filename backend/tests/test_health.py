# tests/test_health.py
"""Health endpoint tests."""

def test_root_endpoint(client):
    """Root endpoint kaam kar raha hai?"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "docs" in data

def test_health_endpoint(client):
    """Health check returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data

def test_docs_accessible(client):
    """Swagger docs accessible hain?"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema(client):
    """OpenAPI schema valid hai?"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/api/v1/auth/login" in schema["paths"]