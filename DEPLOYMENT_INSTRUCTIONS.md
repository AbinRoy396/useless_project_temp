# Deploy PrinciPain on Render

This project is configured for one public Render URL, such as `https://principain.onrender.com`.

The URL serves both the frontend and FastAPI backend. Students submit complaints at the same address, avoiding a separate frontend/API URL and mobile CORS setup.

## Before deploying

1. Create a GitHub repository and push the contents of `useless_project_temp` to it. Never push `backend/.env`, `.env.production`, virtual environments, or database files.
2. Change the local `ADMIN_PASSWORD=Admin` before public launch. It is not secure for a student-facing service.
3. Keep Gmail credentials only in Render environment variables—not GitHub.

## Create the Render deployment

1. Create a Render account and choose **New → Blueprint**.
2. Connect the GitHub repository and select `render.yaml`.
3. Render creates:
   - `principain-db`: PostgreSQL database
   - `principain`: Docker web service
4. Choose the free plans for an exhibition test, then apply the blueprint.

If the `principain` name is unavailable, Render creates a different URL. The app still works because frontend API calls use its same origin.

## Set Render secrets

In **principain web service → Environment**, enter:

| Variable | Value |
| --- | --- |
| `ADMIN_PASSWORD` | New long, unique admin password |
| `EMAIL_MODE` | `preview` first; `smtp` only after testing |
| `SMTP_USERNAME` | Gmail sender address |
| `SMTP_PASSWORD` | Gmail App Password, never the normal Gmail password |
| `SMTP_FROM` | Same Gmail sender address |

`DATABASE_URL`, `FRONTEND_DIR`, report recipient, and generated token secret are supplied by `render.yaml`. Do not copy your local `.env` to Render.

## Validate before sharing

1. Open `https://YOUR_RENDER_URL/health`; it must return `{"status":"ok"}`.
2. Open the root URL on a phone using mobile data.
3. Submit a test complaint and confirm it appears in Campus Pulse.
4. Open Daily Report, sign in as admin, and verify an audit record.
5. Only then set `EMAIL_MODE=smtp`, redeploy, and send one test report.
6. Generate the exhibition QR code from the root Render URL.

## Exhibition note

Free Render instances can sleep after inactivity. Open the site and submit one test report a few minutes before judging. Use an always-on plan for all-day reliability.

## Optional domain

Once the temporary URL works, add your domain in **Render → Settings → Custom Domains** and update `ALLOWED_ORIGINS` to that exact `https://` domain.
