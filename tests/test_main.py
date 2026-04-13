"""
Tests for the health-check endpoints defined in main.py:
    GET /          → always 200
    GET /ping      → 200 (SQLite is fine) or 500 (real DB down)
"""

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "WARMS API is running"
    assert data["version"] == "1.0.0"


def test_ping_returns_a_response(client):
    """Ping should always return something (healthy or error)."""
    response = client.get("/ping")
    assert response.status_code in (200, 500)
