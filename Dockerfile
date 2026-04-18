FROM python:3.12-slim

WORKDIR /app

# Install Python deps first so they're cached across code changes.
RUN pip install --no-cache-dir \
    "google-adk>=1.0.0" \
    "uvicorn[standard]>=0.30.0"

# Copy app source.
COPY main.py ./
COPY agent/ ./agent/

# Cloud Run sets $PORT at runtime; default to 8080 for local builds.
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
