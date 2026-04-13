"""
Tests for /inventory endpoints:
    GET    /inventory          (admin or ranger)
    POST   /inventory          (admin only)
    PUT    /inventory/{id}     (admin only)
    DELETE /inventory/{id}     (admin only)
"""


def _create_item(client, admin_headers, name="Radio Alpha", category="radio", quantity=5):
    r = client.post(
        "/inventory",
        json={"name": name, "category": category, "quantity": quantity, "status": "available"},
        headers=admin_headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


# ─── list ────────────────────────────────────────────────────────────────────

def test_list_inventory_as_admin(client, admin_headers):
    _create_item(client, admin_headers, name="Vehicle 1", category="vehicle", quantity=2)
    r = client.get("/inventory", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


def test_list_inventory_as_ranger(client, admin_headers, ranger_headers):
    _create_item(client, admin_headers)
    r = client.get("/inventory", headers=ranger_headers)
    assert r.status_code == 200


def test_list_inventory_as_visitor_forbidden(client, visitor_headers):
    r = client.get("/inventory", headers=visitor_headers)
    assert r.status_code == 403


def test_list_inventory_unauthenticated(client):
    r = client.get("/inventory")
    assert r.status_code == 401


# ─── create ──────────────────────────────────────────────────────────────────

def test_create_item_as_admin(client, admin_headers):
    r = client.post(
        "/inventory",
        json={"name": "Trap Beta", "category": "trap", "quantity": 10, "status": "available"},
        headers=admin_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Trap Beta"
    assert data["quantity"] == 10
    assert data["status"] == "available"


def test_create_item_as_ranger_forbidden(client, ranger_headers):
    r = client.post(
        "/inventory",
        json={"name": "Sneak", "category": "other", "quantity": 1},
        headers=ranger_headers,
    )
    assert r.status_code == 403


def test_create_item_invalid_category(client, admin_headers):
    r = client.post(
        "/inventory",
        json={"name": "Bad", "category": "spaceship", "quantity": 1},
        headers=admin_headers,
    )
    assert r.status_code == 422


# ─── update ──────────────────────────────────────────────────────────────────

def test_update_item(client, admin_headers):
    item = _create_item(client, admin_headers)
    r = client.put(
        f"/inventory/{item['id']}",
        json={"quantity": 99, "status": "in_use"},
        headers=admin_headers,
    )
    assert r.status_code == 200
    assert r.json()["quantity"] == 99
    assert r.json()["status"] == "in_use"


def test_update_nonexistent_item(client, admin_headers):
    r = client.put(
        "/inventory/99999",
        json={"quantity": 1},
        headers=admin_headers,
    )
    assert r.status_code == 404


def test_update_item_as_ranger_forbidden(client, admin_headers, ranger_headers):
    item = _create_item(client, admin_headers)
    r = client.put(
        f"/inventory/{item['id']}",
        json={"quantity": 1},
        headers=ranger_headers,
    )
    assert r.status_code == 403


# ─── delete ──────────────────────────────────────────────────────────────────

def test_delete_item(client, admin_headers):
    item = _create_item(client, admin_headers)
    r = client.delete(f"/inventory/{item['id']}", headers=admin_headers)
    assert r.status_code == 204
    # Verify it is gone
    r2 = client.get("/inventory", headers=admin_headers)
    ids = [i["id"] for i in r2.json()]
    assert item["id"] not in ids


def test_delete_nonexistent_item(client, admin_headers):
    r = client.delete("/inventory/99999", headers=admin_headers)
    assert r.status_code == 404


def test_delete_item_as_visitor_forbidden(client, admin_headers, visitor_headers):
    item = _create_item(client, admin_headers)
    r = client.delete(f"/inventory/{item['id']}", headers=visitor_headers)
    assert r.status_code == 403
