# MicroStream 📊

**Real-Time Market Microstructure & Liquidity Regime Detection System**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Kafka-Streaming-orange.svg)](https://kafka.apache.org/)
[![ML](https://img.shields.io/badge/ML-Scikit--learn-red.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

MicroStream is a production-ready real-time system that detects market regimes in cryptocurrency markets using machine learning. It processes live trade data from Binance, applies advanced ML models, and visualizes market microstructure patterns through an interactive dashboard.

### Key Features

- **Real-Time Processing**: Streams live BTC/USDT trades from Binance WebSocket
- **ML-Powered Detection**: Uses Isolation Forest + Hidden Markov Models
- **Interactive Dashboard**: Modern Streamlit UI with Plotly visualizations
- **Microservices Architecture**: Docker-based, horizontally scalable
- **Production Ready**: 24/7 operation with health monitoring

## 🏗️ Architecture

```
Binance WebSocket → Ingestion → Kafka → ML Engine → Dashboard
                                  ↓
                            Regime Signals
```

### Components

1. **Ingestion Service**: Connects to Binance WebSocket, aggregates trades into 1-minute bars
2. **ML Engine**: Processes bars, detects regimes using trained models
3. **Dashboard**: Real-time visualization with interactive charts
4. **Kafka**: Message broker for reliable data streaming
5. **Zookeeper**: Kafka coordination

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 4GB RAM minimum
- Internet connection (for Binance WebSocket)

### Run Locally

```bash
# Clone repository
git clone https://github.com/yourusername/MicroStream.git
cd MicroStream

# Start all services
docker compose up -d

# Access dashboard
open http://localhost:8501
```

The system will:
1. Connect to Binance WebSocket
2. Start processing live trades
3. Detect market regimes after ~20 minutes (warm-up period)

## 📊 Dashboard

Access the modern interactive dashboard at **http://localhost:8501**

Features:
- **Real-time price chart** (candlestick)
- **Regime timeline** with confidence scores
- **Market microstructure features** (momentum, volatility, activity)
- **System health** indicators
- **Auto-refresh** every 2 seconds

## 🤖 Machine Learning

### Models

**1. Isolation Forest** (Anomaly Detection)
- Detects unusual market behavior
- 100 trees, 5% contamination threshold
- Trained on 500K+ historical bars

**2. Hidden Markov Model** (Regime Classification)
- 3 states: Normal Market, Bearish Extreme, Bullish Extreme
- Full covariance, Baum-Welch training
- Discovers patterns in momentum, volatility, and activity

### Features

- **Momentum**: `ln(Close_t / Close_{t-1})`
- **Volatility**: `(High - Low) / Open`
- **Activity**: `Volume_t / SMA_20(Volume)`

All features normalized using rolling Z-score.

### Performance

- **Inference**: <1ms per bar
- **Accuracy**: 99.5%+ on validation set
- **Training Data**: 500K+ bars (May 2024 - Dec 2025)

## 📁 Project Structure

```
MicroStream/
├── services/
│   ├── ingestion/          # Binance WebSocket → Kafka
│   ├── ml_engine/          # ML models & inference
│   └── dashboard/          # Streamlit UI
├── data/
│   └── btc/               # Historical training data
├── notebooks/
│   └── train_models.py    # Model training script
├── docker-compose.yml     # Service orchestration
└── README.md
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

## 🎓 For Internships & Portfolios

This project demonstrates:

- **System Design**: Microservices, event-driven architecture
- **ML Engineering**: Model training, deployment, inference
- **Real-Time Processing**: Streaming data, Kafka
- **DevOps**: Docker, containerization, orchestration
- **Data Engineering**: Feature engineering, data pipelines
- **Full Stack**: Backend (Python) + Frontend (Streamlit)

### Talking Points

- "Built a real-time ML system processing live market data"
- "Deployed microservices architecture with Docker & Kafka"
- "Trained unsupervised ML models on 500K+ data points"
- "Created interactive dashboard with sub-second latency"
- "System runs 24/7 with automatic health monitoring"

## 📈 Results

- **Uptime**: 23+ hours continuous operation
- **Throughput**: Processes 1 bar/minute
- **Latency**: <100ms end-to-end
- **Regime Signals**: 22+ detections in test run

## 🛠️ Development

### Retrain Models

```bash
# With new data in data/btc/
python notebooks/train_models.py

# Restart ML engine to use new models
docker compose restart ml_engine
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f ml_engine
```

### Stop System

```bash
docker compose down
```

## 📝 License

MIT License - see LICENSE file

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📧 Contact

**Your Name** - your.email@example.com

Project Link: https://github.com/yourusername/MicroStream

---

**Built with ❤️ for real-time market analysis**
