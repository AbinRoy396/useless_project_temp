import html
import os

import resend
from resend.exceptions import ResendError


def _report_text(report: dict) -> str:
    return f"""Dear Principal,

Campus Voice has completed today's analysis.

Total complaints: {report['total_complaints']}
Campus frustration: {report['campus_score']} / 100
Top concern: {report['top_concern']}

Assessment: {report['executive_summary']}

Today's respectful roast:
{report['roast']}

Regards,
Campus Voice
"""


def _report_html(report: dict) -> str:
    text = html.escape(_report_text(report))
    return f"<pre style=\"font-family:Arial,sans-serif;white-space:pre-wrap\">{text}</pre>"


def deliver_report(recipient: str, subject: str, report: dict) -> tuple[str, str | None, str | None]:
    """Deliver an approved report through Resend HTTPS or record a preview.

    The caller owns audit logging. Preview mode intentionally makes no network
    call; production delivery requires EMAIL_MODE=resend and a Render secret.
    """
    mode = os.getenv("EMAIL_MODE", "preview").lower()
    if mode == "preview":
        return "preview", None, None
    if mode != "resend":
        return "failed", None, "EMAIL_MODE must be preview or resend."

    api_key = os.getenv("RESEND_API_KEY")
    sender = os.getenv("EMAIL_FROM")
    if not api_key or not sender:
        return "failed", None, "RESEND_API_KEY and EMAIL_FROM must be configured."

    resend.api_key = api_key
    try:
        response = resend.Emails.send({
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "text": _report_text(report),
            "html": _report_html(report),
        })
        message_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        return "sent", message_id, None
    except ResendError as error:
        return "failed", None, str(error)[:500]
    except Exception:
        # Do not expose provider internals or credentials in the audit log.
        return "failed", None, "Resend delivery request failed. Check the service logs."
