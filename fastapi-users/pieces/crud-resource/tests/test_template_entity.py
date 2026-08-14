def test_template_entity_crud(client, auth) -> None:
    created = client.post(
        "/template-entity", json={"name": "first", "description": "d"}, headers=auth
    )
    assert created.status_code == 201
    row_id = created.json()["id"]

    assert len(client.get("/template-entity", headers=auth).json()) == 1
    assert client.get(f"/template-entity/{row_id}", headers=auth).json()["name"] == "first"

    patched = client.patch(f"/template-entity/{row_id}", json={"name": "second"}, headers=auth)
    assert patched.status_code == 200 and patched.json()["name"] == "second"

    assert client.delete(f"/template-entity/{row_id}", headers=auth).status_code == 204
    assert client.get(f"/template-entity/{row_id}", headers=auth).status_code == 404


def test_template_entity_requires_auth(client) -> None:
    assert client.get("/template-entity").status_code == 401
