# Quick Start Guide - Local Development (Without Docker)

## ✅ Models Trained Successfully!

Your ML models have been trained and saved:
- ✅ `services/ml_engine/models/isolation_forest.pkl` (1.19 MB)
- ✅ `services/ml_engine/models/hmm_regime.pkl` (1.98 KB)

---

## 🚀 Running Without Docker

Since Docker is not available, you can run the services locally in separate terminals.

### Prerequisites

Install dependencies:
```bash
pip install -r requirements.txt
```

### Option 1: Run with Local Kafka (Recommended)

#### Step 1: Install Kafka Locally

**Windows (using Chocolatey)**:
```bash
choco install kafka
```

**Or download manually**:
1. Download Kafka from https://kafka.apache.org/downloads
2. Extract to `C:\kafka`

#### Step 2: Start Kafka Services

**Terminal 1 - Zookeeper**:
```bash
cd C:\kafka
.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
```

**Terminal 2 - Kafka**:
```bash
cd C:\kafka
.\bin\windows\kafka-server-start.bat .\config\server.properties
```

#### Step 3: Start MicroStream Services

**Terminal 3 - Ingestion Service**:
```bash
cd d:\MicroStream\services\ingestion
python main.py
```

**Terminal 4 - ML Engine**:
```bash
cd d:\MicroStream\services\ml_engine
python main.py
```

**Terminal 5 - Dashboard**:
```bash
cd d:\MicroStream\services\dashboard
streamlit run app.py
```

Then open: **http://localhost:8501**

---

### Option 2: Simplified Test Mode (No Kafka)

Create a simplified version that processes historical data directly without Kafka.

#### Create Test Script

Create `test_system.py` in the root directory:

```python
"""
Simplified test mode - processes historical data without Kafka
"""
import pandas as pd
import sys
from pathlib import Path

# Add service paths
sys.path.append(str(Path('services/ml_engine')))

from feature_engineering import FeatureEngineer
from anomaly_detector import AnomalyDetector
from regime_classifier import RegimeClassifier

# Load a sample of historical data
df = pd.read_csv('data/btc/BTCUSDT-1m-2024-12.csv', header=None, nrows=1000)
df.columns = [
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_volume', 'num_trades',
    'taker_buy_base', 'taker_buy_quote', 'ignore'
]

# Initialize components
feature_engineer = FeatureEngineer(window_size=20)
anomaly_detector = AnomalyDetector(model_path='services/ml_engine/models/isolation_forest.pkl')
regime_classifier = RegimeClassifier(model_path='services/ml_engine/models/hmm_regime.pkl')

# Process bars
results = []
for idx, row in df.iterrows():
    bar = {
        'timestamp': row['open_time'],
        'open': row['open'],
        'high': row['high'],
        'low': row['low'],
        'close': row['close'],
        'volume': row['volume']
    }
    
    features = feature_engineer.add_bar(bar)
    if features is not None:
        normalized = feature_engineer.get_normalized_features(features)
        
        anomaly_score = anomaly_detector.predict_anomaly_score(normalized)
        regime_state, regime_probs = regime_classifier.predict_regime(normalized)
        
        results.append({
            'timestamp': bar['timestamp'],
            'close': bar['close'],
            'anomaly_score': anomaly_score,
            'regime': regime_state,
            'regime_name': regime_classifier.get_regime_name(regime_state)
        })
        
        if idx % 100 == 0:
            print(f"Processed {idx} bars - Latest: {results[-1]}")

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv('test_results.csv', index=False)
print(f"\n✅ Processed {len(results)} bars")
print(f"Results saved to test_results.csv")
print(f"\nRegime distribution:")
print(results_df['regime_name'].value_counts())
```

Run it:
```bash
python test_system.py
```

---

### Option 3: Install Docker Desktop

1. Download Docker Desktop for Windows: https://www.docker.com/products/docker-desktop
2. Install and restart your computer
3. Run: `docker compose up --build`

---

## 📊 What's Next?

1. **Test the models**: Run the test script to verify regime detection
2. **Install Kafka**: For full real-time streaming
3. **Install Docker**: For production deployment

The system is ready - you just need to choose your deployment method!
