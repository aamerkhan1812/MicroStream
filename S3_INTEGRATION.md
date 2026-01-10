# AWS S3 Integration Guide

## 🎯 What S3 Adds to Your System

### **Benefits:**
1. ✅ **Persistent Storage** - Data survives restarts
2. ✅ **Warm Starts** - Resume with full memory
3. ✅ **Historical Analysis** - Query past regime signals
4. ✅ **Model Versioning** - Track model improvements
5. ✅ **Scalability** - Unlimited storage

---

## 📦 **Setup Instructions**

### **1. Install AWS SDK**

Add to `requirements.txt`:
```txt
boto3>=1.34.0
```

Install:
```bash
pip install boto3
```

### **2. Configure AWS Credentials**

Add to `.env`:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=microstream-data
```

### **3. Create S3 Bucket**

Using AWS CLI:
```bash
aws s3 mb s3://microstream-data --region us-east-1
```

Or via AWS Console:
1. Go to S3 console
2. Click "Create bucket"
3. Name: `microstream-data`
4. Region: `us-east-1`
5. Keep default settings
6. Click "Create"

---

## 🗂️ **S3 Bucket Structure**

```
s3://microstream-data/
├── models/
│   ├── isolation_forest.pkl
│   ├── hmm_regime.pkl
│   └── versions/
│       ├── isolation_forest_v1.pkl
│       └── hmm_regime_v1.pkl
│
├── signals/
│   ├── 2026-01-10/
│   │   └── regime_signals.parquet
│   ├── 2026-01-11/
│   │   └── regime_signals.parquet
│   └── ...
│
├── ohlcv/
│   └── BTCUSDT/
│       ├── 2026-01-10.parquet
│       ├── 2026-01-11.parquet
│       └── ...
│
└── state/
    └── feature_history_latest.json
```

---

## 🔧 **Integration with Existing Services**

### **ML Engine - Auto-save Models**

Modify `services/ml_engine/main.py`:

```python
from s3_manager import S3DataManager
import os

class MLInferenceEngine:
    def __init__(self):
        # ... existing code ...
        
        # Initialize S3 manager
        if os.getenv('AWS_ACCESS_KEY_ID'):
            self.s3_manager = S3DataManager(
                bucket_name=os.getenv('S3_BUCKET_NAME', 'microstream-data'),
                region=os.getenv('AWS_REGION', 'us-east-1')
            )
            
            # Try to load models from S3
            self._load_models_from_s3()
        else:
            self.s3_manager = None
    
    def _load_models_from_s3(self):
        """Load models from S3 if available"""
        if self.s3_manager:
            # Download latest models
            self.s3_manager.download_model(
                'isolation_forest.pkl',
                'models/isolation_forest.pkl'
            )
            self.s3_manager.download_model(
                'hmm_regime.pkl',
                'models/hmm_regime.pkl'
            )
```

### **Daily Archival - Cron Job**

Create `services/ml_engine/archival_job.py`:

```python
"""
Daily archival job - runs at midnight
Saves all signals from the day to S3
"""

import schedule
import time
from datetime import datetime, timedelta
from s3_manager import S3DataManager
import pandas as pd

def archive_daily_data():
    """Archive yesterday's data to S3"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get signals from Kafka or local cache
    signals_df = get_daily_signals(yesterday)
    
    # Upload to S3
    s3_manager = S3DataManager('microstream-data')
    s3_manager.archive_daily_signals(signals_df, yesterday)
    
    print(f"✓ Archived {len(signals_df)} signals for {yesterday}")

# Schedule daily at midnight
schedule.every().day.at("00:00").do(archive_daily_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### **Warm Start - Load Feature History**

Modify `services/ml_engine/feature_engineering.py`:

```python
from s3_manager import S3DataManager

class FeatureEngineer:
    def __init__(self, window_size: int = 20):
        # ... existing code ...
        
        # Try to warm start from S3
        self._warm_start_from_s3()
    
    def _warm_start_from_s3(self):
        """Load feature history from S3 for warm start"""
        try:
            s3_manager = S3DataManager('microstream-data')
            features = s3_manager.load_feature_history()
            
            if features:
                self.feature_history = deque(features, maxlen=self.window_size)
                logger.info(f"✓ Warm started with {len(features)} features from S3")
        except:
            logger.info("No S3 warm start available, starting fresh")
```

---

## 📊 **Usage Examples**

### **Example 1: Upload Models After Training**

```python
from s3_manager import S3DataManager

# After training
s3_manager = S3DataManager('microstream-data')

# Upload models
s3_manager.upload_model(
    'services/ml_engine/models/isolation_forest.pkl',
    'isolation_forest.pkl'
)

s3_manager.upload_model(
    'services/ml_engine/models/hmm_regime.pkl',
    'hmm_regime.pkl'
)
```

### **Example 2: Query Historical Regimes**

```python
# Load signals from last week
signals_df = s3_manager.load_historical_signals(
    start_date='2026-01-03',
    end_date='2026-01-10'
)

# Analyze regime distribution
print(signals_df['regime_name'].value_counts())
```

### **Example 3: Backup OHLCV Data**

```python
# Daily backup of OHLCV data
today = datetime.now().strftime('%Y-%m-%d')

s3_manager.upload_ohlcv_data(
    df=daily_ohlcv_df,
    symbol='BTCUSDT',
    date=today
)
```

---

## 💰 **Cost Estimation**

### **S3 Storage Costs (us-east-1)**

| Data Type | Daily Size | Monthly Cost |
|-----------|------------|--------------|
| Models | 1.2 MB | ~$0.00003 |
| Signals (1440 bars/day) | ~500 KB | ~$0.015 |
| OHLCV Data | ~200 KB | ~$0.006 |
| **Total** | ~2 MB/day | **~$0.60/month** |

**Very affordable!** 💵

---

## 🚀 **Deployment with S3**

### **Update docker-compose.yml**

```yaml
ml_engine:
  environment:
    - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    - AWS_REGION=${AWS_REGION}
    - S3_BUCKET_NAME=${S3_BUCKET_NAME}
```

### **Update .env**

```bash
# Add AWS credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=microstream-data
```

---

## ✅ **Benefits Summary**

| Feature | Without S3 | With S3 |
|---------|-----------|---------|
| **Data Persistence** | Lost on restart | ✅ Permanent |
| **Warm Start** | 20 min warm-up | ✅ Instant |
| **Historical Analysis** | Not available | ✅ Full history |
| **Model Versioning** | Manual | ✅ Automated |
| **Disaster Recovery** | None | ✅ Full backup |
| **Cost** | $0 | ~$0.60/month |

---

## 🎯 **Next Steps**

1. ✅ Create S3 bucket
2. ✅ Add AWS credentials to `.env`
3. ✅ Install boto3: `pip install boto3`
4. ✅ Test S3 upload: `python services/ml_engine/s3_manager.py`
5. ✅ Integrate with ML engine
6. ✅ Set up daily archival cron job

**S3 integration is ready to use!** 🚀
