# 🚀 AFTER RESTART - Quick Start Guide

## Step-by-Step Instructions

### 1️⃣ Wait for Docker Desktop to Start
- Look for the **whale icon** in your system tray (bottom-right corner)
- Wait until it says **"Docker Desktop is running"**
- This takes about 30-60 seconds

### 2️⃣ Open PowerShell
- Press `Win + X`
- Click "Windows PowerShell" or "Terminal"

### 3️⃣ Navigate to Project
```powershell
cd d:\MicroStream
```

### 4️⃣ Run Deployment Script
```powershell
.\deploy.ps1
```

That's it! The script will:
- ✓ Check Docker is running
- ✓ Build all services (5-10 min first time)
- ✓ Start the system
- ✓ Open dashboard automatically

### 5️⃣ Dashboard Opens
Your browser will open to: **http://localhost:8501**

You'll see real-time BTC regime detection!

---

## Alternative: Manual Method

If you prefer manual control:

```powershell
cd d:\MicroStream
docker compose up --build
```

Then open: http://localhost:8501

---

## Troubleshooting

**"Docker daemon not running"**
→ Open Docker Desktop and wait for it to start

**"Port 8501 already in use"**
→ Run: `docker compose down` then try again

**Need to see logs?**
→ Run: `docker compose logs -f`

---

## That's All!

Just 4 commands after restart:
1. `cd d:\MicroStream`
2. `.\deploy.ps1`
3. Wait for build to complete
4. Dashboard opens automatically! 🎉
