from fastapi.testclient import TestClient

from app.main import app


def test_daily_report_requires_admin_token(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "report-admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "report-password")
    client = TestClient(app)

    assert client.get("/api/admin/reports/daily").status_code == 401

    login = client.post("/api/admin/login", json={"username": "report-admin", "password": "report-password"})
    token = login.json()["access_token"]
    response = client.get("/api/admin/reports/daily", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
