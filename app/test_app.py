from app import app


def test_root_renders_html() -> None:
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.content_type


def test_api_info_endpoint() -> None:
    client = app.test_client()
    response = client.get("/api")
    assert response.status_code == 200
    assert response.get_json()["service"] == "mobile-banking-backend"


def test_health_endpoint() -> None:
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_account_endpoint_not_found() -> None:
    client = app.test_client()
    response = client.get("/api/v1/accounts/9999")
    assert response.status_code == 404


def test_transfer_missing_fields() -> None:
    client = app.test_client()
    response = client.post("/api/v1/transfer", json={})
    assert response.status_code == 400
