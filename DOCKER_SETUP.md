# Docker Installation & System Deployment Guide

## 🎯 Complete Installation Steps

### Step 1: Install Docker Desktop

I'm installing Docker Desktop for you via winget. This will take a few minutes.

**What's happening:**
```bash
winget install Docker.DockerDesktop
```

**After installation completes:**
1. Docker Desktop will be installed to `C:\Program Files\Docker\Docker`
2. You'll need to **restart your computer** for Docker to work
3. After restart, Docker Desktop will start automatically

---

### Step 2: Verify Docker Installation

After restarting, open PowerShell and run:

```bash
docker --version
docker compose version
```

You should see:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

---

### Step 3: Start Docker Desktop

1. Docker Desktop should auto-start after restart
2. Look for the Docker icon in your system tray (bottom-right)
3. Wait for it to show "Docker Desktop is running"

---

### Step 4: Deploy the MicroStream System

Once Docker is running, navigate to your project and start the services:

```bash
cd d:\MicroStream
docker compose up --build
```

**What this does:**
- Builds Docker images for all 3 services (Ingestion, ML Engine, Dashboard)
- Starts Zookeeper and Kafka
- Launches all microservices
- Connects to Binance WebSocket
- Begins real-time regime detection

---

### Step 5: Access the Dashboard

Open your browser to:
```
http://localhost:8501
```

You'll see:
- Real-time candlestick charts
- Regime background coloring (Green/Yellow/Red)
- Anomaly detection alerts
- Feature metrics

---

## 🔧 Troubleshooting

### Issue: "Docker daemon is not running"

**Solution:**
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon stops animating)
3. Try the command again

### Issue: "WSL 2 installation is incomplete"

**Solution:**
```bash
wsl --install
wsl --set-default-version 2
```
Then restart your computer.

### Issue: Port conflicts (8501, 9092, etc.)

**Solution:**
```bash
# Stop any conflicting services
docker compose down

# Or change ports in docker-compose.yml
```

---

## 📊 Monitoring the System

### View Logs

**All services:**
```bash
docker compose logs -f
```

**Specific service:**
```bash
docker compose logs -f ingestion
docker compose logs -f ml_engine
docker compose logs -f dashboard
```

### Check Service Status

```bash
docker compose ps
```

### Restart Services

```bash
docker compose restart
```

### Stop Everything

```bash
docker compose down
```

---

## 🚀 Production Deployment Checklist

Once Docker is working:

- [x] Models trained ✅
- [ ] Docker installed
- [ ] System started with `docker compose up`
- [ ] Dashboard accessible at localhost:8501
- [ ] Kafka topics created
- [ ] Real-time data flowing
- [ ] Regime detection working

---

## 📝 Next Steps After Installation

1. **Restart your computer** (required for Docker)
2. **Open Docker Desktop** and wait for it to start
3. **Run**: `docker compose up --build`
4. **Open**: http://localhost:8501
5. **Watch**: Real-time regime detection in action!

---

## ⚡ Quick Commands Reference

```bash
# Start system
docker compose up -d

# View logs
docker compose logs -f

# Stop system
docker compose down

# Rebuild after code changes
docker compose up --build

# Check status
docker compose ps

# Access Kafka console
docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic market_regime_signals --from-beginning
```

---

## 🎓 System Architecture Reminder

```
Browser (localhost:8501)
    ↓
Dashboard Service (Streamlit)
    ↓
Kafka (market_regime_signals)
    ↓
ML Engine (Isolation Forest + HMM)
    ↓
Kafka (market_raw_bars)
    ↓
Ingestion Service (Binance WebSocket)
```

All running in Docker containers, orchestrated by Docker Compose!
