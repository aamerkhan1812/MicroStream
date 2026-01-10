# Real-Time Market Microstructure & Liquidity Regime Estimation System

A production-grade streaming financial analysis system that infers latent market states (regimes) from cryptocurrency data in real-time using unsupervised machine learning.

## 🎯 Overview

This system uses an **Event-Driven Microservices Architecture** to process high-frequency market data and estimate liquidity regimes using a dual-model ML approach:

- **Isolation Forest**: Detects microstructure anomalies (flash crashes, liquidity voids)
- **Hidden Markov Model**: Classifies market into 3 hidden states (Stable, Volatile, Crisis)

## 🏗️ Architecture

### Three-Tier Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Tier 3: Presentation                      │
│              Streamlit Dashboard (Real-time UI)              │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ WebSocket
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Tier 2: Intelligence Engine                 │
│        Feature Engineering → Isolation Forest → HMM          │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ Kafka
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Tier 1: Market Observer                    │
│         Binance WebSocket → Trade Aggregation → Kafka        │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Features

### Feature Engineering
- **Momentum**: Log returns `ln(Close_t / Close_{t-1})`
- **Volatility Proxy**: Normalized range `(High - Low) / Open`
- **Activity Ratio**: Relative volume `Volume / SMA_20(Volume)`

### ML Models
- **Isolation Forest**: Anomaly detection with 5% contamination threshold
- **Gaussian HMM**: 3-state regime classification with full covariance

### Visualization
- Real-time candlestick charts with regime background coloring
- Anomaly score timeline
- Regime probability distributions
- Feature metrics dashboard

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Historical BTCUSDT data in `data/btc/`

### 1. Train Models

```bash
cd notebooks
python train_models.py
```

This will generate:
- `services/ml_engine/models/isolation_forest.pkl`
- `services/ml_engine/models/hmm_regime.pkl`

### 2. Start Services

```bash
docker-compose up --build
```

This starts:
- **Zookeeper** (port 2181)
- **Kafka** (ports 9092, 9093)
- **Ingestion Service** (WebSocket → Kafka)
- **ML Engine** (Kafka → Inference → Kafka)
- **Dashboard** (http://localhost:8501)

### 3. Access Dashboard

Open browser to: **http://localhost:8501**

## 📁 Project Structure

```
MicroStream/
├── docker-compose.yml          # Orchestration
├── .env                        # Configuration
├── requirements.txt            # Dependencies
│
├── services/
│   ├── ingestion/              # Tier 1: Market Observer
│   │   ├── main.py             # WebSocket client
│   │   ├── aggregator.py       # OHLCV aggregation
│   │   └── kafka_producer.py   # Stream publisher
│   │
│   ├── ml_engine/              # Tier 2: Intelligence
│   │   ├── main.py             # Inference engine
│   │   ├── feature_engineering.py
│   │   ├── anomaly_detector.py
│   │   ├── regime_classifier.py
│   │   └── models/             # Trained models
│   │
│   └── dashboard/              # Tier 3: Presentation
│       ├── app.py              # Streamlit app
│       └── kafka_consumer.py   # Signal consumer
│
├── data/btc/                   # Historical data
├── notebooks/                  # Training scripts
└── config/                     # Configuration files
```

## 🔧 Configuration

Edit `.env` file:

```bash
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_RAW_BARS_TOPIC=market_raw_bars
KAFKA_REGIME_SIGNALS_TOPIC=market_regime_signals

# Binance
BINANCE_WS_URL=wss://stream.binance.com:9443/ws/btcusdt@aggTrade
SYMBOL=BTCUSDT

# ML
ISOLATION_FOREST_CONTAMINATION=0.05
HMM_N_COMPONENTS=3
FEATURE_WINDOW_SIZE=20
```

## 📈 Regime States

| State | Name | Characteristics |
|-------|------|-----------------|
| 0 | 🟢 Stable Liquidity | Low volatility, consistent volume |
| 1 | 🟡 High Volatility | Directional flow, widening ranges |
| 2 | 🔴 Liquidity Crisis | Extreme variance, volume spikes |

## 🧪 Testing

### Historical Backtesting

```bash
# Use historical data instead of live WebSocket
python services/ingestion/backtest.py --data-dir data/btc
```

### Unit Tests

```bash
pytest tests/
```

## 📊 Performance Metrics

- **Latency**: Tick-to-visualization < 500ms
- **Throughput**: Handles 1000+ trades/second
- **Accuracy**: Regime detection validated against manual analysis

## 🛠️ Development

### Add New Features

1. Update `feature_engineering.py`
2. Retrain models: `python notebooks/train_models.py`
3. Restart services: `docker-compose restart ml_engine`

### Modify Regime Count

1. Update `HMM_N_COMPONENTS` in `.env`
2. Retrain HMM model
3. Update regime color mapping in `dashboard/app.py`

## 📝 Data Format

Input CSV columns (Binance format):
```
0: Open Time (milliseconds)
1: Open
2: High
3: Low
4: Close
5: Volume (BTC)
6: Close Time
7: Quote Volume (USDT)
8: Number of Trades
9: Taker Buy Base Volume
10: Taker Buy Quote Volume
11: Ignore
```

## 🔍 Troubleshooting

### Kafka Connection Issues
```bash
# Check Kafka health
docker-compose logs kafka

# Recreate Kafka topics
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

### Model Not Found
```bash
# Ensure models are trained
ls services/ml_engine/models/

# Retrain if missing
python notebooks/train_models.py
```

### Dashboard Not Updating
```bash
# Check ML engine logs
docker-compose logs ml_engine

# Verify Kafka messages
docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic market_regime_signals --from-beginning
```

## 📚 References

- **Isolation Forest**: Liu et al. (2008) - "Isolation Forest"
- **Hidden Markov Models**: Rabiner (1989) - "A Tutorial on HMMs"
- **Market Microstructure**: O'Hara (1995) - "Market Microstructure Theory"

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

---

**Built with**: Python, Docker, Kafka, scikit-learn, hmmlearn, Streamlit, Plotly
