# Railway Deployment - FULL Real-Time System
# All services in one container

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Install Kafka
RUN wget https://archive.apache.org/dist/kafka/3.6.1/kafka_2.13-3.6.1.tgz && \
    tar -xzf kafka_2.13-3.6.1.tgz && \
    mv kafka_2.13-3.6.1 /opt/kafka && \
    rm kafka_2.13-3.6.1.tgz

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all services
COPY services/ ./services/
COPY notebooks/ ./notebooks/
COPY .env .env

# Create models directory
RUN mkdir -p services/ml_engine/models

# Expose dashboard port
EXPOSE 8501

# Copy and set startup script
COPY start_full_system.sh .
RUN chmod +x start_full_system.sh

CMD ["./start_full_system.sh"]
