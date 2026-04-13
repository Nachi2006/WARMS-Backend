"""
Tests for /announcements endpoints:
    POST   /announcements          (admin only)
    GET    /announcements          (any authenticated user)
    PATCH  /announcements/{id}     (admin only)
    DELETE /announcements/{id}     (admin only – soft-delete)
"""


# ─── helpers ─────────────────────────────────────────────────────────────────

def _create_announcement(client, admin_headers, title="Test Title", body="Test body"):
    r = client.post(
        "/announcements",
        json={"title": title, "body": body},
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


# ─── create ──────────────────────────────────────────────────────────────────

def test_create_announcement_as_admin(client, admin_headers):
    r = client.post(
        "/announcements",
        json={"title": "Park Closure", "body": "Closed on Monday"},
        headers=admin_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "Park Closure"
    assert data["is_active"] is True


def test_create_announcement_as_visitor_forbidden(client, visitor_headers):
    r = client.post(
        "/announcements",
        json={"title": "Bad", "body": "Oops"},
        headers=visitor_headers,
    )
    assert r.status_code == 403


def test_create_announcement_as_ranger_forbidden(client, ranger_headers):
    r = client.post(
        "/announcements",
        json={"title": "Bad", "body": "Oops"},
        headers=ranger_headers,
    )
    assert r.status_code == 403


def test_create_announcement_unauthenticated(client):
    r = client.post("/announcements", json={"title": "Bad", "body": "Oops"})
    assert r.status_code == 401


# ─── list ────────────────────────────────────────────────────────────────────

def test_list_announcements_returns_active_only(client, admin_headers, visitor_headers):
    a1 = _create_announcement(client, admin_headers, title="Active One")
    a2 = _create_announcement(client, admin_headers, title="Will Be Deactivated")

    # deactivate the second announcement
    client.delete(f"/announcements/{a2['id']}", headers=admin_headers)

    r = client.get("/announcements", headers=visitor_headers)
    assert r.status_code == 200
    titles = [a["title"] for a in r.json()]
    assert "Active One" in titles
    assert "Will Be Deactivated" not in titles


def test_list_announcements_unauthenticated(client):
    r = client.get("/announcements")
    assert r.status_code == 401


# ─── update ──────────────────────────────────────────────────────────────────

def test_update_announcement_title(client, admin_headers):
    ann = _create_announcement(client, admin_headers, title="Old Title")
    r = client.patch(
        f"/announcements/{ann['id']}",
        json={"title": "New Title"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "New Title"


def test_update_nonexistent_announcement(client, admin_headers):
    r = client.patch(
        "/announcements/99999",
        json={"title": "Ghost"},
        headers=admin_headers,
    )
    assert r.status_code == 404


def test_update_announcement_as_visitor_forbidden(client, admin_headers, visitor_headers):
    ann = _create_announcement(client, admin_headers)
    r = client.patch(
        f"/announcements/{ann['id']}",
        json={"title": "Hack"},
        headers=visitor_headers,
    )
    assert r.status_code == 403


# ─── delete (soft) ───────────────────────────────────────────────────────────

def test_deactivate_announcement(client, admin_headers):
    ann = _create_announcement(client, admin_headers)
    r = client.delete(f"/announcements/{ann['id']}", headers=admin_headers)
    assert r.status_code == 204


def test_deactivate_nonexistent_announcement(client, admin_headers):
    r = client.delete("/announcements/99999", headers=admin_headers)
    assert r.status_code == 404


def test_deactivate_announcement_as_visitor_forbidden(client, admin_headers, visitor_headers):
    ann = _create_announcement(client, admin_headers)
    r = client.delete(f"/announcements/{ann['id']}", headers=visitor_headers)
    assert r.status_code == 403
