import re
import secrets
from collections import Counter
from datetime import datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Complaint

CATEGORY_KEYWORDS = {
    "Wi-Fi": ("wifi", "wi-fi", "internet", "network"), "Timetable": ("timetable", "schedule", "reschedule"),
    "Attendance": ("attendance", "absent"), "Infrastructure": ("projector", "classroom", "bench", "ac ", "toilet"),
    "Canteen": ("canteen", "food", "meal"), "Transport": ("bus", "transport"), "Examination": ("exam", "examination", "result"),
    "Hostel": ("hostel", "room"), "Fees": ("fee", "fees", "payment"), "Academic": ("assignment", "course", "syllabus"),
}


def anonymous_id() -> str:
    return f"STU-{secrets.token_hex(3).upper()}"


def analyse(message: str, mood: int) -> dict:
    """Deterministic and safe placeholder for a structured LLM classifier."""
    text = message.lower()
    category = next((name for name, words in CATEGORY_KEYWORDS.items() if any(word in text for word in words)), "Other")
    intensity = len(re.findall(r"!", message)) + sum(word in text for word in ("again", "always", "worst", "urgent", "dead"))
    score = round(min(10, max(1, mood + intensity * 0.45)), 1)
    sentiment = "frustrated" if score >= 6 else "concerned" if score >= 4 else "neutral"
    return {"category": category, "sentiment": sentiment, "severity": round(score), "frustration_score": score, "summary": message.strip()[:180]}


def today_complaints(db: Session) -> list[Complaint]:
    start = datetime.combine(datetime.utcnow().date(), time.min)
    return list(db.scalars(select(Complaint).where(Complaint.created_at >= start).order_by(Complaint.created_at.desc())))


def dashboard(db: Session) -> dict:
    complaints = today_complaints(db)
    count = len(complaints)
    average = round(sum(c.frustration_score for c in complaints) / count, 1) if count else 0
    volume_score = min(100, count * 4)
    severity = round(sum(c.severity for c in complaints) / count * 10, 1) if count else 0
    campus = round(average * 10 * .4 + volume_score * .3 + severity * .2, 1) if count else 0
    level = "Principal emergency" if campus >= 80 else "Serious" if campus >= 60 else "Concerning" if campus >= 40 else "Peaceful"
    categories = [{"name": name, "count": value} for name, value in Counter(c.category for c in complaints).most_common()]
    departments = [{"name": name, "count": value} for name, value in Counter(c.department for c in complaints).most_common()]
    return {"total_complaints": count, "average_frustration": average, "campus_score": campus, "level": level, "categories": categories, "departments": departments, "recent_complaints": complaints[:10]}


def category_summary(categories: list[dict]) -> str:
    """Summarize every category count without exposing complaint text."""
    return ", ".join(f"{item['name']}: {item['count']}" for item in categories)


def build_respectful_roast(data: dict) -> str:
    """Create a parody from the complete daily aggregate, never raw reports."""
    categories = data["categories"]
    if not categories:
        return "The campus has filed no complaints today. We consider this a rare and suspicious moment of peace."
    top = categories[0]
    return (
        f"Across {data['total_complaints']} reports spanning {len(categories)} categories, students averaged "
        f"{data['average_frustration']}/10 frustration. {top['name']} leads with {top['count']} reports. "
        f"Full signal board: {category_summary(categories)}. "
        "At this point, the campus issue tracker has more plot twists than the timetable."
    )


def report(db: Session) -> dict:
    # dashboard() reads every complaint submitted today and aggregates them before
    # this report (including the roast) is composed. Raw complaint text never
    # reaches the roast layer.
    data = dashboard(db)
    top = data["categories"][0]["name"] if data["categories"] else "No concern yet"
    actions = [f"Assign an owner to investigate {top}.", "Publish a clear acknowledgement and resolution timeline.", "Review progress with student representatives this week."]
    breakdown = category_summary(data["categories"]) or "No category signals yet"
    return {**data, "top_concern": top, "executive_summary": f"{data['total_complaints']} anonymous reports were received today. The campus frustration index is {data['campus_score']}/100. Full category aggregate: {breakdown}.", "suggested_actions": actions, "roast": build_respectful_roast(data)}
