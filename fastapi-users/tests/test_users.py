def test_healthz(client) -> None:
    assert client.get("/healthz").json()["status"] == "ok"


def test_register_and_login(client) -> None:
    res = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "sup3rsecret", "full_name": "New"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "new@example.com"
    assert "hashed_password" not in body  # the hash never leaves the model layer

    dup = client.post(
        "/auth/register", json={"email": "new@example.com", "password": "sup3rsecret"}
    )
    assert dup.status_code == 409

    ok = client.post("/auth/login", json={"email": "new@example.com", "password": "sup3rsecret"})
    assert ok.status_code == 200 and ok.json()["access_token"]

    bad = client.post("/auth/login", json={"email": "new@example.com", "password": "wrong-pass"})
    assert bad.status_code == 401


def test_me_requires_a_token(client, auth) -> None:
    assert client.get("/users/me").status_code == 401
    res = client.get("/users/me", headers=auth)
    assert res.status_code == 200 and res.json()["email"] == "a@example.com"


def test_user_lifecycle(client, auth) -> None:
    user_id = client.get("/users/me", headers=auth).json()["id"]

    listed = client.get("/users", headers=auth)
    assert listed.status_code == 200 and len(listed.json()) == 1

    patched = client.patch(f"/users/{user_id}", json={"full_name": "Ada L."}, headers=auth)
    assert patched.status_code == 200 and patched.json()["full_name"] == "Ada L."

    assert client.delete(f"/users/{user_id}", headers=auth).status_code == 204
    assert client.get(f"/users/{user_id}", headers=auth).status_code == 401
