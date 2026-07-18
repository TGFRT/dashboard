# ---- Build stage ----
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy backend requirements and install
COPY automatizaciondb/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY automatizaciondb ./automatizaciondb

# Copy static UI files
COPY index.html ./static/index.html
COPY style.css ./static/style.css
COPY script.js ./static/script.js

# ---- Runtime stage ----
FROM python:3.11-slim AS runtime
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy backend code
COPY --from=builder /app/automatizaciondb ./automatizaciondb

# Copy static assets
COPY --from=builder /app/static ./static

# Expose port (Render provides $PORT env var, default to 8000)
EXPOSE ${PORT:-8000}

# Set environment variable fallback
ENV PORT=${PORT:-8000}

# Command to run the FastAPI app with uvicorn using dynamic port
CMD ["uvicorn", "automatizaciondb.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
