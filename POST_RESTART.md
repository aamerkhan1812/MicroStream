# 🚀 POST-RESTART DEPLOYMENT GUIDE

## You've Restarted - Great! Now Deploy the System

### Step 1: Verify Docker is Running

Open PowerShell and check:
```powershell
docker --version
```

You should see: `Docker version 24.x.x` or similar.

If you get an error:
1. Open **Docker Desktop** from Start Menu
2. Wait for the whale icon in system tray to stop animating
3. Try the command again

---

### Step 2: Deploy MicroStream (Automated)

Navigate to the project and run the deployment script:

```powershell
cd d:\MicroStream
.\deploy.ps1
```

**What this does:**
- ✓ Checks Docker is running
- ✓ Verifies ML models exist
- ✓ Builds all Docker images (first time: ~5-10 min)
- ✓ Starts all services (Zookeeper, Kafka, Ingestion, ML Engine, Dashboard)
- ✓ Opens the dashboard automatically

---

### Step 3: Access the Dashboard

The script will automatically open: **http://localhost:8501**

You'll see:
- 🟢 Real-time BTC/USDT price chart
- 🎨 Background colors showing market regime
- 📊 Anomaly detection timeline
- 📈 Feature metrics

---

## Alternative: Manual Deployment

If you prefer manual control:

```powershell
cd d:\MicroStream
docker compose up --build
```

Then manually open: http://localhost:8501

---

## Monitoring the System

### View All Logs
```powershell
docker compose logs -f
```

### View Specific Service
```powershell
docker compose logs -f ml_engine      # ML inference
docker compose logs -f ingestion      # Binance WebSocket
docker compose logs -f dashboard      # Streamlit UI
```

### Check Service Status
```powershell
docker compose ps
```

---

## Stopping the System

```powershell
docker compose down
```

---

## Troubleshooting

### "Cannot connect to Docker daemon"
- Open Docker Desktop
- Wait for it to fully start
- Try again

### "Port already in use"
```powershell
docker compose down
netstat -ano | findstr :8501
```

### Services won't start
```powershell
docker compose logs
docker compose restart
```

---

## 🎉 That's It!

Once deployed, the system will:
- Connect to Binance WebSocket
- Aggregate trades into 1-minute bars
- Detect market regimes in real-time
- Show everything on the dashboard

**Enjoy your real-time market microstructure analysis system!** 🚀
