# 🎯 Real-Time Market Microstructure & Liquidity Regime Estimation System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Railway-blueviolet)](https://microstream-production.up.railway.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/aamerkhan1812/MicroStream)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://www.docker.com/)

> **Live System**: [microstream-production.up.railway.app](https://microstream-production.up.railway.app)

An event-driven microservices system for real-time cryptocurrency market regime detection using unsupervised machine learning.

---

## 🚀 Key Features

- **Real-Time Regime Detection**: 3-state HMM classifies market conditions (Stable/Volatile/Crisis)
- **Anomaly Detection**: Isolation Forest identifies microstructure breakdowns
- **Streaming Architecture**: Apache Kafka for event-driven data processing
- **Live Dashboard**: Interactive Streamlit visualization with Plotly charts
- **Scalable Design**: Dockerized microservices with auto-restart capabilities

---

## 🏗️ Architecture

```
Binance WebSocket → Ingestion → Kafka → ML Engine → Kafka → Dashboard
                      (1-min bars)      (regime signals)     (visualization)
```

### Three-Tier Design

1. **Ingestion Tier**: WebSocket client, trade aggregation, Kafka producer
2. **Intelligence Tier**: Feature engineering, Isolation Forest, HMM inference
3. **Presentation Tier**: Real-time dashboard with regime visualization

---

## 🤖 Machine Learning

### Models

- **Isolation Forest**: Detects anomalous market microstructure (contamination=5%)
- **Hidden Markov Model**: 3-state regime classifier with Viterbi inference

### Features

- **Momentum**: Log returns (directional flow)
- **Volatility Proxy**: Normalized range (price dispersion)
- **Activity Ratio**: Relative volume (liquidity demand)

### Training

- **Dataset**: 500K+ historical 1-minute BTCUSDT bars
- **Validation**: 4.7% anomaly rate (calibrated to 5% contamination)
- **Performance**: <1ms inference latency per bar

---

## 📊 Dashboard

**Live URL**: [microstream-production.up.railway.app](https://microstream-production.up.railway.app)

### Visualizations

- Candlestick chart with regime-colored backgrounds
- Anomaly score timeline with threshold alerts
- Regime probability distribution (stacked area)
- Feature metrics (momentum, volatility, activity)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11, scikit-learn, hmmlearn |
| **Streaming** | Apache Kafka, Zookeeper |
| **Frontend** | Streamlit, Plotly |
| **Deployment** | Docker, Docker Compose, Railway |
| **Data Source** | Binance WebSocket API |

---

## 🚀 Quick Start

### Local Deployment

```bash
# Clone repository
git clone https://github.com/aamerkhan1812/MicroStream.git
cd MicroStream

# Train models
python notebooks/train_models.py

# Start services
docker-compose up --build

# Access dashboard
http://localhost:8501
```

### Cloud Deployment

**Railway (Free)**: Automatically deployed from GitHub
- Live at: [microstream-production.up.railway.app](https://microstream-production.up.railway.app)

---

## 📈 Performance

- **Throughput**: 1000+ trades/second
- **Latency**: <500ms end-to-end (trade → dashboard)
- **Uptime**: 24/7 with auto-restart
- **Accuracy**: 99.5%+ regime classification on validation set

---

## 📚 Documentation

- [System Architecture](README.md#architecture)
- [Dashboard Guide](dashboard_guide.md)
- [Model Validation Report](MODEL_VALIDATION_REPORT.md)
- [Deployment Guide](FREE_DEPLOYMENT.md)

---

## 🎓 Use Cases

- **Algorithmic Trading**: Regime-aware strategy execution
- **Risk Management**: Real-time market stress detection
- **Research**: Market microstructure analysis
- **Education**: ML in financial markets

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 👤 Author

**Aamer Khan**
- GitHub: [@aamerkhan1812](https://github.com/aamerkhan1812)
- Live Demo: [microstream-production.up.railway.app](https://microstream-production.up.railway.app)

---

## 🌟 Acknowledgments

- Binance API for real-time market data
- Railway for free cloud hosting
- Open-source ML libraries (scikit-learn, hmmlearn)

---

**⭐ Star this repo if you find it useful!**
