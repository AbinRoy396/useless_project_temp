FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini .
COPY backend/entrypoint.sh .
COPY index.html app.js pages.css pages.js ./frontend/
COPY submit.html pulse.html ai-engine.html roast.html admin.html email.html exhibition.html ./frontend/
RUN chmod +x entrypoint.sh
ENV FRONTEND_DIR=/app/frontend
EXPOSE 8001
CMD ["./entrypoint.sh"]
