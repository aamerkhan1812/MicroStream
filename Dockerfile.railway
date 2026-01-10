# Railway Deployment - Simplified Single Service
# Railway works best with single services, not docker-compose

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Kafka (embedded mode for Railway)
RUN curl -O https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz && \
    tar -xzf kafka_2.13-3.6.0.tgz && \
    mv kafka_2.13-3.6.0 /opt/kafka && \
    rm kafka_2.13-3.6.0.tgz

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all services
COPY services/ ./services/
COPY notebooks/ ./notebooks/
COPY .env .env

# Expose dashboard port
EXPOSE 8501

# Start script
COPY start.sh .
RUN chmod +x start.sh

CMD ["./start.sh"]
