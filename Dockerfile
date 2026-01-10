# Railway Deployment - Simplified (No Kafka needed!)
# Uses Railway's managed services instead

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all services
COPY services/ ./services/
COPY notebooks/ ./notebooks/
COPY .env .env

# Train models on first run
RUN python notebooks/train_models.py || echo "Model training will happen on first run"

# Expose dashboard port
EXPOSE 8501

# Start only the dashboard (Railway provides Kafka separately)
CMD cd services/dashboard && streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
