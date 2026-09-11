import os
import smtplib
from email.message import EmailMessage


def deliver_report(recipient: str, subject: str, report: dict) -> tuple[str, str | None, str | None]:
    """Returns status, SMTP message ID, and any safe error description.

    Preview mode is deliberate: no email leaves the machine until EMAIL_MODE=smtp.
    """
    if os.getenv("EMAIL_MODE", "preview").lower() != "smtp":
        return "preview", None, None
    host = os.getenv("SMTP_HOST")
    sender = os.getenv("SMTP_FROM")
    if not host or not sender:
        return "failed", None, "SMTP_HOST and SMTP_FROM must be configured."
    message = EmailMessage()
    message["From"] = sender
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(f"""Dear Principal,

Campus Voice has completed today's analysis.

Total complaints: {report['total_complaints']}
Campus frustration: {report['campus_score']} / 100
Top concern: {report['top_concern']}

Assessment: {report['executive_summary']}

Today's respectful roast:
{report['roast']}

Regards,
Campus Voice
""")
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=15) as client:
            if os.getenv("SMTP_STARTTLS", "true").lower() == "true":
                client.starttls()
            username, password = os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD")
            if username and password:
                client.login(username, password)
            client.send_message(message)
        return "sent", message["Message-ID"], None
    except (OSError, smtplib.SMTPException) as error:
        return "failed", None, str(error)[:500]
