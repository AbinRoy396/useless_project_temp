import re
import time
from collections import defaultdict, deque

from fastapi import HTTPException

# A lightweight first-line safeguard. A production deployment should add a
# provider moderation endpoint and a shared Redis-backed rate limiter.
BLOCKED_PATTERNS = (
    r"\b(kill|murder|shoot|stab)\b",
    r"\b(bomb|explosive)\b",
    r"\b(suicide|self[- ]?harm)\b",
)
NAME_WITH_TITLE = re.compile(r"\b(?:mr|mrs|ms|dr|professor|prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?", re.IGNORECASE)
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
PHONE = re.compile(r"\b(?:\+?\d[\d -]{8,}\d)\b")
_hits: dict[str, deque[float]] = defaultdict(deque)
RATE_LIMIT = 20
WINDOW_SECONDS = 10 * 60


def rate_limit(client_key: str) -> None:
    now = time.monotonic()
    recent = _hits[client_key]
    while recent and recent[0] <= now - WINDOW_SECONDS:
        recent.popleft()
    if len(recent) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many submissions. Please try again in a few minutes.")
    recent.append(now)


def sanitize_submission(message: str) -> str:
    if any(re.search(pattern, message, re.IGNORECASE) for pattern in BLOCKED_PATTERNS):
        raise HTTPException(status_code=422, detail="This report needs immediate human support and cannot be submitted through Campus Voice.")
    # Do not retain names, emails, or phone numbers in anonymous feedback.
    cleaned = NAME_WITH_TITLE.sub("[staff member]", message)
    cleaned = EMAIL.sub("[email removed]", cleaned)
    cleaned = PHONE.sub("[phone removed]", cleaned)
    return cleaned.strip()
