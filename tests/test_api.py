def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    # assert "text/html" in response.headers["content-type"]

def test_webhook_missing_header(client):
    response = client.post("/api/v1/webhooks/orders/create", json={})
    assert response.status_code == 401
    assert response.json() == {"detail": "Missing HMAC header"}
