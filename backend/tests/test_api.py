from fastapi.testclient import TestClient

from app.main import app


def client():
    return TestClient(app)


def test_creates_sanitized_complaint():
    response = client().post("/api/complaints", json={"message": "Dr. Anita Sharma can be reached at anita@example.edu", "department": "CSE", "mood": 6})
    assert response.status_code == 201
    assert "[staff member]" in response.json()["message"]
    assert "anita@example.edu" not in response.json()["message"]


def test_blocks_unsafe_submission():
    response = client().post("/api/complaints", json={"message": "I will shoot the projector", "department": "CSE", "mood": 9})
    assert response.status_code == 422


def test_admin_approval_is_audited(monkeypatch):
    # Tests must never trigger a real SMTP delivery, regardless of local .env.
    monkeypatch.setenv("EMAIL_MODE", "preview")
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "change-me-before-production")
    test_client = client()
    login = test_client.post("/api/admin/login", json={"username": "admin", "password": "change-me-before-production"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    approval = test_client.post("/api/admin/reports/daily/send", json={"recipient": "principal@example.edu"}, headers=headers)
    assert approval.status_code == 200
    assert approval.json()["status"] == "preview"
    assert test_client.get("/api/admin/report-audits", headers=headers).status_code == 200
