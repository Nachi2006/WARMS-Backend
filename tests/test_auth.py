"""
Tests for /auth endpoints:
    POST /auth/signup
    POST /auth/login
    GET  /auth/me
"""


# ─── signup ──────────────────────────────────────────────────────────────────

def test_signup_success(client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepass1",
        "role": "user",
    }
    r = client.post("/auth/signup", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_signup_duplicate_email(client):
    payload = {
        "username": "dup",
        "email": "dup@example.com",
        "password": "securepass1",
        "role": "user",
    }
    client.post("/auth/signup", json=payload)
    r = client.post("/auth/signup", json=payload)
    assert r.status_code == 400
    assert "already registered" in r.json()["detail"]


def test_signup_short_password(client):
    r = client.post(
        "/auth/signup",
        json={"username": "u", "email": "a@b.com", "password": "short", "role": "user"},
    )
    assert r.status_code == 422


def test_signup_invalid_email(client):
    r = client.post(
        "/auth/signup",
        json={"username": "u", "email": "not-an-email", "password": "password123", "role": "user"},
    )
    assert r.status_code == 422


# ─── login ───────────────────────────────────────────────────────────────────

def test_login_success(client):
    client.post(
        "/auth/signup",
        json={"username": "logme", "email": "logme@ex.com", "password": "password123", "role": "user"},
    )
    r = client.post("/auth/login", json={"email": "logme@ex.com", "password": "password123"})
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/signup",
        json={"username": "logme2", "email": "logme2@ex.com", "password": "password123", "role": "user"},
    )
    r = client.post("/auth/login", json={"email": "logme2@ex.com", "password": "wrongpassword"})
    assert r.status_code == 401


def test_login_unknown_email(client):
    r = client.post("/auth/login", json={"email": "nobody@ex.com", "password": "password123"})
    assert r.status_code == 401


def test_login_account_lockout(client):
    """After 5 failed attempts the account should be locked (403)."""
    client.post(
        "/auth/signup",
        json={"username": "lockme", "email": "lock@ex.com", "password": "password123", "role": "user"},
    )
    for _ in range(5):
        client.post("/auth/login", json={"email": "lock@ex.com", "password": "wrong"})

    r = client.post("/auth/login", json={"email": "lock@ex.com", "password": "password123"})
    assert r.status_code == 403
    assert "locked" in r.json()["detail"].lower()


# ─── /auth/me ────────────────────────────────────────────────────────────────

def test_get_me_authenticated(client, visitor_headers):
    r = client.get("/auth/me", headers=visitor_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "visitor@test.com"


def test_get_me_unauthenticated(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_get_me_invalid_token(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer totallywrong"})
    assert r.status_code == 401
