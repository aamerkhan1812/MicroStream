"""
Anomaly Detector - Isolation Forest
Detects microstructure breakdowns (flash crashes, liquidity voids)
"""

import numpy as np
import logging
import os
import joblib
from pathlib import Path
from sklearn.ensemble import IsolationForest
from typing import Optional

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Isolation Forest for detecting market microstructure anomalies
    
    Conceptual Logic:
    - Normal market minutes require many splits to isolate
    - Anomalous minutes (structure breaks) are isolated quickly
    - Output: Anomaly score where score < 0 indicates anomaly
    """
    
    def __init__(self, contamination: float = 0.05, model_path: Optional[str] = None):
        """
        Args:
            contamination: Expected proportion of anomalies (default: 5%)
            model_path: Path to pre-trained model (optional)
        """
        self.contamination = contamination
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        
        # Load or initialize model
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new Isolation Forest model"""
        logger.info(f"Initializing Isolation Forest (contamination={self.contamination})")
        
        self.model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            max_samples='auto',
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        
        logger.info("✓ Isolation Forest initialized")
    
    def fit(self, X: np.ndarray):
        """
        Train the Isolation Forest on historical data
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
        """
        if X.shape[0] < 10:
            logger.warning("Insufficient data for training. Need at least 10 samples.")
            return
        
        logger.info(f"Training Isolation Forest on {X.shape[0]} samples...")
        
        self.model.fit(X)
        self.is_trained = True
        
        logger.info("✓ Isolation Forest training complete")
    
    def predict_anomaly_score(self, features: np.ndarray) -> float:
        """
        Predict anomaly score for a single feature vector
        
        Args:
            features: Feature vector of shape (n_features,)
        
        Returns:
            Anomaly score:
                - Positive values: Normal behavior
                - Negative values: Anomalous behavior (microstructure breakdown)
        """
        if not self.is_trained:
            logger.warning("Model not trained yet. Returning neutral score.")
            return 0.0
        
        # Reshape for sklearn (expects 2D array)
        X = features.reshape(1, -1)
        
        # Get anomaly score
        # score_samples returns the opposite of the anomaly score
        # Higher values = more normal, lower values = more anomalous
        score = self.model.score_samples(X)[0]
        
        return score
    
    def is_anomaly(self, features: np.ndarray, threshold: Optional[float] = None) -> bool:
        """
        Determine if the feature vector represents an anomaly
        
        Args:
            features: Feature vector
            threshold: Custom threshold (default: use model's decision function)
        
        Returns:
            True if anomaly detected, False otherwise
        """
        if not self.is_trained:
            return False
        
        if threshold is not None:
            score = self.predict_anomaly_score(features)
            return score < threshold
        else:
            # Use model's built-in prediction (-1 = anomaly, 1 = normal)
            X = features.reshape(1, -1)
            prediction = self.model.predict(X)[0]
            return prediction == -1
    
    def save_model(self, path: str):
        """Save the trained model to disk"""
        if not self.is_trained:
            logger.warning("Cannot save untrained model")
            return
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)
        logger.info(f"✓ Model saved to {path}")
    
    def load_model(self, path: str):
        """Load a pre-trained model from disk"""
        try:
            self.model = joblib.load(path)
            self.is_trained = True
            logger.info(f"✓ Model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load model from {path}: {e}")
            self._initialize_model()
    
    def get_anomaly_threshold(self, percentile: float = 5.0) -> float:
        """
        Calculate dynamic anomaly threshold based on score distribution
        
        Args:
            percentile: Percentile for threshold (default: 5th percentile)
        
        Returns:
            Threshold value
        """
        if not self.is_trained:
            return 0.0
        
        # This would require storing historical scores
        # For now, return a fixed threshold
        return -0.5  # Typical threshold for anomalies
