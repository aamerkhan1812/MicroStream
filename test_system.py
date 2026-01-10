"""
Simplified test mode - processes historical data without Kafka
Demonstrates the ML pipeline working on historical data
"""
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add service paths
sys.path.append(str(Path('services/ml_engine')))

from feature_engineering import FeatureEngineer
from anomaly_detector import AnomalyDetector
from regime_classifier import RegimeClassifier

print("=" * 60)
print("MicroStream - Simplified Test Mode")
print("=" * 60)

# Load a sample of historical data
print("\n📊 Loading historical data...")
df = pd.read_csv('data/btc/BTCUSDT-1m-2024-12.csv', header=None, nrows=1000)
df.columns = [
    'open_time', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_volume', 'num_trades',
    'taker_buy_base', 'taker_buy_quote', 'ignore'
]
print(f"✓ Loaded {len(df)} bars from December 2024")

# Initialize components
print("\n🤖 Initializing ML models...")
feature_engineer = FeatureEngineer(window_size=20)
anomaly_detector = AnomalyDetector(model_path='services/ml_engine/models/isolation_forest.pkl')
regime_classifier = RegimeClassifier(model_path='services/ml_engine/models/hmm_regime.pkl')
print("✓ Models loaded successfully")

# Process bars
print("\n⚙️  Processing bars...")
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
        is_anomaly = anomaly_detector.is_anomaly(normalized)
        regime_state, regime_probs = regime_classifier.predict_regime(normalized)
        
        results.append({
            'timestamp': bar['timestamp'],
            'datetime': datetime.fromtimestamp(bar['timestamp'] / 1000),
            'close': bar['close'],
            'volume': bar['volume'],
            'anomaly_score': anomaly_score,
            'is_anomaly': is_anomaly,
            'regime': regime_state,
            'regime_name': regime_classifier.get_regime_name(regime_state),
            'regime_confidence': regime_probs[regime_state]
        })
        
        if idx % 100 == 0 and idx > 0:
            latest = results[-1]
            print(f"  {latest['datetime']} | "
                  f"Price: ${latest['close']:,.2f} | "
                  f"Regime: {latest['regime_name']} ({latest['regime_confidence']:.1%}) | "
                  f"Anomaly: {latest['anomaly_score']:.3f}")

# Save results
print("\n💾 Saving results...")
results_df = pd.DataFrame(results)
results_df.to_csv('test_results.csv', index=False)
print(f"✓ Results saved to test_results.csv")

# Summary statistics
print("\n" + "=" * 60)
print("📈 SUMMARY")
print("=" * 60)
print(f"Total bars processed: {len(results)}")
print(f"\nRegime Distribution:")
regime_counts = results_df['regime_name'].value_counts()
for regime, count in regime_counts.items():
    pct = count / len(results) * 100
    print(f"  {regime}: {count} ({pct:.1f}%)")

print(f"\nAnomalies Detected: {results_df['is_anomaly'].sum()} ({results_df['is_anomaly'].sum() / len(results) * 100:.1f}%)")

print(f"\nPrice Range:")
print(f"  Min: ${results_df['close'].min():,.2f}")
print(f"  Max: ${results_df['close'].max():,.2f}")
print(f"  Mean: ${results_df['close'].mean():,.2f}")

print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Review test_results.csv for detailed results")
print("2. Install Docker to run the full real-time system")
print("3. Or install Kafka locally for streaming mode")
