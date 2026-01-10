"""
Model Training Script
Train Isolation Forest and HMM models on historical BTCUSDT data
"""

import pandas as pd
import numpy as np
import glob
import os
from pathlib import Path
import joblib
import logging
from sklearn.ensemble import IsolationForest
from hmmlearn.hmm import GaussianHMM

# Add parent directory to path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'services' / 'ml_engine'))

from feature_engineering import FeatureEngineer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_historical_data(data_dir: str = None) -> pd.DataFrame:
    """Load all historical CSV files"""
    if data_dir is None:
        data_dir = str(Path(__file__).parent.parent / 'data' / 'btc')
    
    logger.info(f"Loading data from {data_dir}")
    
    csv_files = glob.glob(os.path.join(data_dir, "BTCUSDT-1m-*.csv"))
    csv_files.sort()
    
    logger.info(f"Found {len(csv_files)} CSV files")
    
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file, header=None)
        df.columns = [
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'num_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ]
        dfs.append(df)
    
    combined_df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Loaded {len(combined_df)} total bars")
    
    return combined_df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply feature engineering to historical data"""
    logger.info("Engineering features...")
    
    engineer = FeatureEngineer(window_size=20)
    features_list = []
    
    for idx, row in df.iterrows():
        bar = {
            'timestamp': row['open_time'],
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'volume': row['volume']
        }
        
        features = engineer.add_bar(bar)
        
        if features is not None:
            normalized = engineer.get_normalized_features(features)
            features_list.append(normalized)
        
        if idx % 100000 == 0:
            logger.info(f"Processed {idx}/{len(df)} bars")
    
    feature_df = pd.DataFrame(
        features_list,
        columns=['momentum', 'volatility_proxy', 'activity_ratio']
    )
    
    logger.info(f"Generated {len(feature_df)} feature vectors")
    return feature_df


def train_isolation_forest(X: np.ndarray, output_path: str):
    """Train and save Isolation Forest model"""
    logger.info("Training Isolation Forest...")
    
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        max_samples='auto',
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X)
    
    # Save model
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    
    logger.info(f"✓ Isolation Forest saved to {output_path}")
    
    # Test predictions
    scores = model.score_samples(X[:1000])
    logger.info(f"Sample anomaly scores: mean={scores.mean():.3f}, std={scores.std():.3f}")


def train_hmm(X: np.ndarray, output_path: str, n_components: int = 3):
    """Train and save HMM model"""
    logger.info(f"Training Gaussian HMM (n_components={n_components})...")
    
    model = GaussianHMM(
        n_components=n_components,
        covariance_type="full",
        n_iter=100,
        random_state=42,
        verbose=True
    )
    
    model.fit(X)
    
    # Save model
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    
    logger.info(f"✓ HMM saved to {output_path}")
    
    # Log learned parameters
    logger.info("\nTransition Matrix:")
    logger.info(model.transmat_)
    
    logger.info("\nMeans (Feature Centroids):")
    logger.info(model.means_)


def main():
    """Main training pipeline"""
    logger.info("=" * 60)
    logger.info("Model Training Pipeline")
    logger.info("=" * 60)
    
    # Step 1: Load data
    df = load_historical_data()
    
    # Use a subset for faster training (adjust as needed)
    # For full training, remove this line
    df = df.sample(n=min(500000, len(df)), random_state=42).sort_index()
    logger.info(f"Using {len(df)} samples for training")
    
    # Step 2: Feature engineering
    feature_df = engineer_features(df)
    X = feature_df.values
    
    # Remove NaN/Inf values
    X = X[~np.isnan(X).any(axis=1)]
    X = X[~np.isinf(X).any(axis=1)]
    
    logger.info(f"Final training set: {X.shape}")
    
    # Step 3: Train Isolation Forest
    model_dir = Path(__file__).parent.parent / 'services' / 'ml_engine' / 'models'
    model_dir.mkdir(parents=True, exist_ok=True)
    
    train_isolation_forest(
        X,
        output_path=str(model_dir / 'isolation_forest.pkl')
    )
    
    # Step 4: Train HMM
    train_hmm(
        X,
        output_path=str(model_dir / 'hmm_regime.pkl'),
        n_components=3
    )
    
    logger.info("=" * 60)
    logger.info("✓ Training Complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
