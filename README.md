# Campus Voice — Principal Frustration Engine

An anonymous student-feedback system with an exhibition-friendly dashboard and a respectful parody reporting layer.

## Delivery journey

| Milestone | Outcome | Status |
| --- | --- | --- |
| 1. Product foundation | Anonymous feedback, safety rules, score design | Complete |
| 2. Exhibition UI | Responsive form, live stream, meter, categories, report modal | Complete |
| 3. API and storage | FastAPI, SQLite local database, PostgreSQL-ready configuration | Complete |
| 4. Frontend integration | Replace browser simulation with API calls and polling/WebSockets | Next |
| 5. Admin workflow | Authentication, report approval, audited email sending | Complete (preview by default) |
| 6. Production hardening | Submission safeguards, tests, migrations, Docker/PostgreSQL scaffold | Complete locally |
| 7. Launch | Deploy API/database/UI, create QR poster, rehearse exhibition flow | Planned |

## Run the current demo

Start the API first, then serve the exhibition UI from a second terminal:

```bash
python -m http.server 8000
```

## Run the API

The backend defaults to a local SQLite file, so it works before PostgreSQL or an AI key are configured.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Visit `http://127.0.0.1:8001/docs` to test the API. Copy [backend/.env.example](./backend/.env.example) to `.env` or set `DATABASE_URL` to use PostgreSQL in deployment.

## API surface

- `POST /api/complaints` — submit an anonymous complaint and receive structured analysis.
- `GET /api/dashboard` — today's aggregate metrics and recent complaint stream.
- `GET /api/reports/daily` — a human-review report. It never sends email automatically.
- `GET /health` — deployment health check.
- `WS /ws/dashboard` — emits a dashboard refresh event whenever a complaint is created.

## Admin report approval

The report modal asks for admin credentials only when **Admin approve & send** is selected. The API issues a signed, eight-hour bearer token and records the approver, recipient, subject, status, timestamp, provider message ID, and safe error message in `report_audits`.

`EMAIL_MODE=preview` is the default: approval is audited but no email is delivered. Set `EMAIL_MODE=smtp` and configure SMTP values in [backend/.env.example](./backend/.env.example) only after changing the admin username, password, and token secret. For a multi-admin production deployment, replace the local credential mechanism with the institution’s OIDC/SSO provider.

## Verification and deployment

Run the automated checks from `backend`:

```bash
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\alembic.exe upgrade head --sql
```

[docker-compose.yml](./docker-compose.yml) provides a PostgreSQL and API deployment scaffold. Before exposing it publicly, move all passwords into a secret manager, set a specific HTTPS frontend origin in `ALLOWED_ORIGINS`, run `alembic upgrade head`, and put the API behind an HTTPS reverse proxy.

### Public production deployment

The repository now includes a production Docker Compose stack: PostgreSQL stays private, the API is proxied through Caddy, and Caddy automatically provisions HTTPS once your domain points to the server.

1. Provision a Linux server with Docker Compose and ports `80`/`443` open.
2. Point a domain/subdomain DNS A record to that server.
3. Copy `.env.production.example` to `.env.production`, then set the real domain and strong unique secrets. Do not reuse the local demo credentials.
4. From the project root run `docker compose up -d --build`.
5. Visit `https://YOUR_DOMAIN/health`, submit a test complaint, and verify the Admin audit flow.

Keep `EMAIL_MODE=preview` until the public HTTPS deployment is verified; then configure an authorized SMTP account and switch to `smtp`.

## Safety boundary

The current classifier is deterministic and only categorises reported operational issues. It does not make misconduct findings, identify students, or accuse named staff. When replacing it with an LLM, enforce the same JSON schema and moderation boundary.
