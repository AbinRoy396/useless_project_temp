from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(primary_key=True)
    anonymous_id: Mapped[str] = mapped_column(String(16), index=True)
    department: Mapped[str] = mapped_column(String(60), index=True)
    message: Mapped[str] = mapped_column(Text)
    mood: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    sentiment: Mapped[str] = mapped_column(String(30))
    severity: Mapped[int] = mapped_column(Integer)
    frustration_score: Mapped[float] = mapped_column(Float)
    ai_summary: Mapped[str] = mapped_column(String(280))


class ReportAudit(Base):
    __tablename__ = "report_audits"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    approved_by: Mapped[str] = mapped_column(String(80))
    recipient: Mapped[str] = mapped_column(String(320))
    subject: Mapped[str] = mapped_column(String(240))
    status: Mapped[str] = mapped_column(String(30))
    provider_message_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
