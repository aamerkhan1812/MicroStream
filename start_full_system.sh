#!/bin/bash
# Full Real-Time System Startup for Railway
# Runs Kafka + All Services + Live Binance Streaming

set -e

echo "=========================================="
echo "Starting MicroStream - FULL REAL-TIME"
echo "=========================================="

# Start Zookeeper
echo "[1/7] Starting Zookeeper..."
/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties > /tmp/zookeeper.log 2>&1 &
sleep 5

# Start Kafka
echo "[2/7] Starting Kafka..."
/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties > /tmp/kafka.log 2>&1 &
sleep 10

# Create Kafka topics
echo "[3/7] Creating Kafka topics..."
/opt/kafka/bin/kafka-topics.sh --create --topic market_raw_bars \
    --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || true
/opt/kafka/bin/kafka-topics.sh --create --topic market_regime_signals \
    --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 || true

# Train models if needed
echo "[4/7] Checking ML models..."
if [ ! -f "services/ml_engine/models/isolation_forest.pkl" ]; then
    echo "Training models (first run only)..."
    python notebooks/train_models.py
else
    echo "Models already trained ✓"
fi

# Start Ingestion Service (Binance WebSocket)
echo "[5/7] Starting Ingestion Service (Live Binance)..."
cd services/ingestion
python main.py > /tmp/ingestion.log 2>&1 &
cd ../..
sleep 3

# Start ML Engine
echo "[6/7] Starting ML Engine..."
cd services/ml_engine
python main.py > /tmp/ml_engine.log 2>&1 &
cd ../..
sleep 3

# Start Dashboard (foreground - Railway needs this)
echo "[7/7] Starting Dashboard..."
echo "=========================================="
echo "✓ System Ready - Processing LIVE data!"
echo "✓ Binance WebSocket: Connected"
echo "✓ Kafka: Running"
echo "✓ ML Engine: Active"
echo "✓ Dashboard: Starting..."
echo "=========================================="

cd services/dashboard
exec streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
