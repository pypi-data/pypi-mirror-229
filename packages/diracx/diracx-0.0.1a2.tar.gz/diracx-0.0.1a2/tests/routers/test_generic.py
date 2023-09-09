def test_openapi(test_client):
    r = test_client.get("/openapi.json")
    assert r.status_code == 200
    assert r.json()


def test_oidc_configuration(test_client):
    r = test_client.get("/.well-known/openid-configuration")
    assert r.status_code == 200
    assert r.json()
