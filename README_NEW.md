# PrinciPain - Campus Frustration Reporting Platform

A full-stack web application for students to report campus frustrations and for administrators to analyze and respond to these reports.

## Project Structure

- **Frontend**: HTML/CSS/JavaScript single-page application served by Caddy
- **Backend**: FastAPI Python application with PostgreSQL database
- **Features**: AI-powered analysis, email notifications, real-time dashboard updates

## Deployment on Render

This project can be deployed on Render using the provided configuration files.

### Prerequisites

1. Create a [Render](https://render.com) account
2. Connect your GitHub repository to Render
3. Configure environment variables as needed

### Services Configuration

The deployment consists of two services:

#### Backend Service (FastAPI)
- **Type**: Web Service
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `sh entrypoint.sh`

#### Frontend Service (Static Files)
- **Type**: Web Service
- **Environment**: Static
- **Build Command**: `echo 'Building frontend'`
- **Start Command**: `caddy run --config /etc/caddy/Caddyfile`

### Environment Variables

Set these environment variables in your Render dashboard:

#### Backend Service:
- `DATABASE_URL` - PostgreSQL database connection string
- `ALLOWED_ORIGINS` - Comma-separated list of allowed origins
- `ADMIN_USERNAME` - Admin username for login
- `ADMIN_PASSWORD` - Admin password for login
- `ADMIN_TOKEN_SECRET` - Secret for JWT tokens
- `EMAIL_MODE` - Set to `smtp` for email delivery or `preview` for testing
- `SMTP_HOST` - SMTP server host (for email)
- `SMTP_PORT` - SMTP server port
- `SMTP_STARTTLS` - Enable STARTTLS
- `SMTP_USERNAME` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `SMTP_FROM` - Email sender address
- `ADMIN_REPORT_RECIPIENT` - Email recipient for daily reports

### Deployment Steps

1. Fork or clone this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure the service settings:
   - For Backend: Set build and start commands as specified above
   - For Frontend: Set build and start commands as specified above
5. Add all required environment variables
6. Deploy both services

### URL Structure

After deployment, you'll get temporary URLs like:
- **Frontend**: `https://principain.onrender.com`
- **Backend API**: `https://principain-backend.onrender.com`

### Production Considerations

1. Update database connection string to use PostgreSQL
2. Set appropriate CORS origins
3. Configure SMTP settings for email delivery
4. Change default admin credentials
5. Add custom domain (optional)

## Local Development

To run locally:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Frontend (in main directory)
caddy run --config Caddyfile
```

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /api/complaints` - Submit a complaint
- `GET /api/dashboard` - Get dashboard data
- `GET /api/reports/daily` - Get daily report
- `POST /api/admin/login` - Admin login
- `POST /api/admin/reports/daily/send` - Send daily report
- `GET /api/admin/report-audits` - Get report audit logs
- `GET /api/complaints/{id}` - Get specific complaint
- `GET /ws/dashboard` - WebSocket for real-time updates

## Technology Stack

- **Frontend**: HTML, CSS, JavaScript (Caddy web server)
- **Backend**: FastAPI, Python 3.12
- **Database**: PostgreSQL (via SQLAlchemy)
- **Authentication**: JWT tokens
- **AI Analysis**: External AI service integration
- **Email**: SMTP for notifications