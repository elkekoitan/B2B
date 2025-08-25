FROM python:3.11-slim

WORKDIR /app

# Sistem dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Agent kodu
COPY . .

# Log klasörü
RUN mkdir -p /app/logs

# Non-root user
RUN useradd -m -u 1001 agentuser && chown -R agentuser:agentuser /app
USER agentuser

EXPOSE 8001

CMD ["python", "main.py"]