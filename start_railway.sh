#!/bin/bash
# Railway Startup - Real-Time with Redis
set -e

echo "=========================================="
echo "MicroStream - Real-Time (Railway)"
echo "=========================================="

# Start Redis (lightweight message broker)
echo "[1/5] Starting Redis..."
redis-server --daemonize yes --save "" --appendonly no
sleep 2

# Train models if needed
echo "[2/5] Checking ML models..."
if [ ! -f "services/ml_engine/models/isolation_forest.pkl" ]; then
    echo "Training models..."
    python notebooks/train_models.py
else
    echo "Models ready ✓"
fi

# Start Ingestion (Binance WebSocket → Redis)
echo "[3/5] Starting Binance Ingestion..."
cd services/ingestion
REDIS_MODE=1 python main.py > /tmp/ingestion.log 2>&1 &
cd ../..
sleep 2

# Start ML Engine (Redis → Processing → Redis)
echo "[4/5] Starting ML Engine..."
cd services/ml_engine
REDIS_MODE=1 python main.py > /tmp/ml_engine.log 2>&1 &
cd ../..
sleep 2

# Start Dashboard (Redis → Display)
echo "[5/5] Starting Dashboard..."
echo "=========================================="
echo "✓ Real-Time System Ready!"
echo "✓ Binance: LIVE streaming"
echo "✓ Redis: Running"
echo "✓ ML Engine: Active"
echo "=========================================="

cd services/dashboard
exec REDIS_MODE=1 streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
