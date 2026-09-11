from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


Department = Literal["CSE", "ECE", "Mechanical", "Commerce", "Hostel", "General campus"]


class ComplaintCreate(BaseModel):
    message: str = Field(min_length=3, max_length=500)
    department: Department
    mood: int = Field(ge=1, le=10)


class ComplaintOut(BaseModel):
    id: int
    anonymous_id: str
    department: str
    message: str
    mood: int
    created_at: datetime
    category: str
    sentiment: str
    severity: int
    frustration_score: float
    ai_summary: str

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    total_complaints: int
    average_frustration: float
    campus_score: float
    level: str
    categories: list[dict]
    departments: list[dict]
    recent_complaints: list[ComplaintOut]


class ReportOut(BaseModel):
    total_complaints: int
    campus_score: float
    top_concern: str
    executive_summary: str
    suggested_actions: list[str]
    roast: str


class AdminLogin(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=200)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SendReportRequest(BaseModel):
    recipient: str | None = Field(default=None, max_length=320)


class AuditOut(BaseModel):
    id: int
    created_at: datetime
    approved_by: str
    recipient: str
    subject: str
    status: str
    provider_message_id: str | None
    error_message: str | None

    model_config = {"from_attributes": True}
