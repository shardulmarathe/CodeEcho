FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads clips data

# Bind to $PORT when the host provides one (Render/Cloud), else default to 8000.
# Single worker on purpose: the in-memory session cache and local budget fallback
# assume one process. Do not add --workers.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
