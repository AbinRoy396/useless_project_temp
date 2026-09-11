from app.email_service import deliver_report


REPORT = {"total_complaints": 3, "campus_score": 42.0, "top_concern": "Wi-Fi", "executive_summary": "Three anonymous reports were received.", "roast": "The router has a busy social life."}


def test_preview_mode_never_delivers(monkeypatch):
    monkeypatch.setenv("EMAIL_MODE", "preview")
    assert deliver_report("principal@example.edu", "Daily report", REPORT) == ("preview", None, None)


def test_resend_mode_requires_secret_and_sender(monkeypatch):
    monkeypatch.setenv("EMAIL_MODE", "resend")
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    monkeypatch.delenv("EMAIL_FROM", raising=False)
    status, _, error = deliver_report("principal@example.edu", "Daily report", REPORT)
    assert status == "failed"
    assert error == "RESEND_API_KEY and EMAIL_FROM must be configured."
