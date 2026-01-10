#!/bin/bash
# Railway startup script - runs all services

set -e

echo "Starting MicroStream on Railway..."

# Start Zookeeper in background
/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties &
sleep 5

# Start Kafka in background
/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties &
sleep 10

# Create Kafka topics
/opt/kafka/bin/kafka-topics.sh --create --topic market_raw_bars --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || true
/opt/kafka/bin/kafka-topics.sh --create --topic market_regime_signals --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || true

# Train models if not exist
if [ ! -f "services/ml_engine/models/isolation_forest.pkl" ]; then
    echo "Training models..."
    python notebooks/train_models.py
fi

# Start ingestion service in background
cd services/ingestion
python main.py &
cd ../..

# Start ML engine in background
cd services/ml_engine
python main.py &
cd ../..

# Start dashboard (foreground - Railway needs this)
cd services/dashboard
streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
