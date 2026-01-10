"""
AWS S3 Integration Module
Handles data persistence and retrieval from S3
"""

import boto3
import json
import pandas as pd
import joblib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)


class S3DataManager:
    """
    Manages data persistence to/from AWS S3
    """
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1'):
        """
        Initialize S3 client
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region
        """
        self.bucket_name = bucket_name
        self.region = region
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        logger.info(f"S3 client initialized for bucket: {bucket_name}")
    
    # ==================== MODEL MANAGEMENT ====================
    
    def upload_model(self, model_path: str, model_name: str) -> bool:
        """
        Upload trained model to S3
        
        Args:
            model_path: Local path to model file
            model_name: Name to save in S3 (e.g., 'isolation_forest.pkl')
        
        Returns:
            True if successful
        """
        try:
            s3_key = f"models/{model_name}"
            
            self.s3_client.upload_file(
                Filename=model_path,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"✓ Uploaded model to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload model: {e}")
            return False
    
    def download_model(self, model_name: str, local_path: str) -> bool:
        """
        Download model from S3
        
        Args:
            model_name: Model name in S3
            local_path: Where to save locally
        
        Returns:
            True if successful
        """
        try:
            s3_key = f"models/{model_name}"
            
            # Create directory if needed
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.s3_client.download_file(
                Bucket=self.bucket_name,
                Key=s3_key,
                Filename=local_path
            )
            
            logger.info(f"✓ Downloaded model from s3://{self.bucket_name}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return False
    
    # ==================== DATA ARCHIVAL ====================
    
    def archive_daily_signals(self, signals_df: pd.DataFrame, date: str) -> bool:
        """
        Archive daily regime signals to S3
        
        Args:
            signals_df: DataFrame with regime signals
            date: Date string (YYYY-MM-DD)
        
        Returns:
            True if successful
        """
        try:
            s3_key = f"signals/{date}/regime_signals.parquet"
            
            # Convert to parquet (compressed)
            parquet_buffer = signals_df.to_parquet(compression='gzip')
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=parquet_buffer
            )
            
            logger.info(f"✓ Archived {len(signals_df)} signals to S3: {date}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to archive signals: {e}")
            return False
    
    def load_historical_signals(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Load historical signals from S3
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with signals or None
        """
        try:
            # List all signal files in date range
            prefix = "signals/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            dfs = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                # Extract date from key
                if start_date <= key.split('/')[1] <= end_date:
                    # Download and read parquet
                    obj_data = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    df = pd.read_parquet(obj_data['Body'])
                    dfs.append(df)
            
            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                logger.info(f"✓ Loaded {len(combined_df)} historical signals")
                return combined_df
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load historical signals: {e}")
            return None
    
    # ==================== FEATURE HISTORY (WARM START) ====================
    
    def save_feature_history(self, feature_history: list, timestamp: str) -> bool:
        """
        Save feature history for warm restart
        
        Args:
            feature_history: List of feature vectors
            timestamp: Current timestamp
        
        Returns:
            True if successful
        """
        try:
            s3_key = f"state/feature_history_latest.json"
            
            data = {
                'timestamp': timestamp,
                'features': [f.tolist() for f in feature_history]
            }
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(data)
            )
            
            logger.info(f"✓ Saved feature history ({len(feature_history)} vectors)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save feature history: {e}")
            return False
    
    def load_feature_history(self) -> Optional[list]:
        """
        Load feature history for warm restart
        
        Returns:
            List of feature vectors or None
        """
        try:
            s3_key = "state/feature_history_latest.json"
            
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            data = json.loads(response['Body'].read())
            features = [np.array(f) for f in data['features']]
            
            logger.info(f"✓ Loaded feature history ({len(features)} vectors)")
            return features
            
        except Exception as e:
            logger.error(f"Failed to load feature history: {e}")
            return None
    
    # ==================== OHLCV DATA ====================
    
    def upload_ohlcv_data(self, df: pd.DataFrame, symbol: str, date: str) -> bool:
        """
        Upload OHLCV data to S3
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol (e.g., 'BTCUSDT')
            date: Date string (YYYY-MM-DD)
        
        Returns:
            True if successful
        """
        try:
            s3_key = f"ohlcv/{symbol}/{date}.parquet"
            
            parquet_buffer = df.to_parquet(compression='gzip')
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=parquet_buffer
            )
            
            logger.info(f"✓ Uploaded OHLCV data: {symbol} {date}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload OHLCV data: {e}")
            return False


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Initialize S3 manager
    s3_manager = S3DataManager(
        bucket_name='microstream-data',
        region='us-east-1'
    )
    
    # Example 1: Upload trained models
    s3_manager.upload_model(
        model_path='models/isolation_forest.pkl',
        model_name='isolation_forest.pkl'
    )
    
    # Example 2: Archive daily signals
    signals_df = pd.DataFrame({
        'timestamp': [1736507400000],
        'regime': [1],
        'anomaly_score': [-0.234]
    })
    s3_manager.archive_daily_signals(signals_df, '2026-01-10')
    
    # Example 3: Load historical signals
    historical_df = s3_manager.load_historical_signals('2026-01-01', '2026-01-10')
