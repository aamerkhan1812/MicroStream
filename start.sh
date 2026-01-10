#!/bin/bash
# Simplified Railway startup - Dashboard only

set -e

echo "Starting MicroStream Dashboard on Railway..."

# Train models if not exist
if [ ! -f "services/ml_engine/models/isolation_forest.pkl" ]; then
    echo "Training models..."
    python notebooks/train_models.py
fi

# Start dashboard
cd services/dashboard
streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
