# Railway Deployment - Real-Time with Redis (Lightweight)
# Uses Redis instead of Kafka for Railway's resource limits

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt redis

# Copy all services
COPY services/ ./services/
COPY notebooks/ ./notebooks/
COPY .env .env

# Create models directory
RUN mkdir -p services/ml_engine/models

# Expose dashboard port
EXPOSE 8501

# Copy startup script
COPY start_railway.sh .
RUN chmod +x start_railway.sh

CMD ["./start_railway.sh"]
