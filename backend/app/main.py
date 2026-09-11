import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import select

from .database import Base, engine, get_db
from .models import Complaint, ReportAudit
from .schemas import AdminLogin, AuditOut, ComplaintCreate, ComplaintOut, DashboardOut, ReportOut, SendReportRequest, TokenOut
from .services import analyse, anonymous_id, dashboard, report
from .realtime import hub
from .auth import authenticate, current_admin, issue_token
from .email_service import deliver_report
from .safety import rate_limit, sanitize_submission

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Campus Voice API", version="0.1.0")
origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://127.0.0.1:3000",
).split(",")
allowed_origins = [origin.strip() for origin in origins if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/complaints", response_model=ComplaintOut, status_code=201)
async def create_complaint(payload: ComplaintCreate, request: Request, db: Session = Depends(get_db)):
    rate_limit(request.client.host if request.client else "unknown")
    message = sanitize_submission(payload.message)
    analysis = analyse(message, payload.mood)
    analysis["ai_summary"] = analysis.pop("summary")
    complaint = Complaint(anonymous_id=anonymous_id(), department=payload.department, message=message, mood=payload.mood, **analysis)
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    await hub.publish({"type": "complaint_created", "complaint": ComplaintOut.model_validate(complaint).model_dump(mode="json")})
    return complaint


@app.get("/api/dashboard", response_model=DashboardOut)
def get_dashboard(db: Session = Depends(get_db)):
    return dashboard(db)


@app.get("/api/admin/reports/daily", response_model=ReportOut)
def get_daily_report(admin: str = Depends(current_admin), db: Session = Depends(get_db)):
    return report(db)


@app.post("/api/admin/login", response_model=TokenOut)
def admin_login(payload: AdminLogin):
    if not authenticate(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return {"access_token": issue_token(payload.username)}


@app.post("/api/admin/reports/daily/send", response_model=AuditOut)
def approve_and_send_report(payload: SendReportRequest, admin: str = Depends(current_admin), db: Session = Depends(get_db)):
    recipient = payload.recipient or os.getenv("ADMIN_REPORT_RECIPIENT")
    if not recipient or "@" not in recipient:
        raise HTTPException(status_code=422, detail="A valid report recipient is required")
    daily_report = report(db)
    subject = f"Daily Campus Frustration Report — {datetime.utcnow():%d %B}"
    status, message_id, error = deliver_report(recipient, subject, daily_report)
    audit = ReportAudit(approved_by=admin, recipient=recipient, subject=subject, status=status, provider_message_id=message_id, error_message=error)
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


@app.get("/api/admin/report-audits", response_model=list[AuditOut])
def report_audits(admin: str = Depends(current_admin), db: Session = Depends(get_db)):
    return list(db.scalars(select(ReportAudit).order_by(ReportAudit.created_at.desc()).limit(50)))


@app.get("/api/complaints/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)


# Render deploys this API and the static student interface as one HTTPS service.
# Keeping them same-origin avoids exposing a second public API URL or CORS errors.
frontend_dir = os.getenv("FRONTEND_DIR", str(Path(__file__).resolve().parents[2]))
if Path(frontend_dir).is_dir():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
