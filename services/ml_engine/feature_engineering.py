"""
Feature Engineering Pipeline
Transforms raw OHLCV bars into normalized feature vectors for ML inference
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
from collections import deque
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Calculates the feature vector X_t from OHLCV data
    
    Features:
    1. Momentum (Log Returns): r_t = ln(Close_t / Close_{t-1})
    2. Volatility Proxy (Normalized Range): (High_t - Low_t) / Open_t
    3. Activity Ratio (Relative Volume): Volume_t / SMA_20(Volume)
    """
    
    def __init__(self, window_size: int = 20):
        """
        Args:
            window_size: Number of bars to maintain for rolling calculations
        """
        self.window_size = window_size
        self.price_history = deque(maxlen=window_size + 1)  # +1 for lag calculation
        self.volume_history = deque(maxlen=window_size)
        self.feature_history = deque(maxlen=window_size)  # Store computed features
        
    def add_bar(self, bar: Dict[str, Any]) -> np.ndarray:
        """
        Process a new OHLCV bar and compute feature vector
        
        Args:
            bar: Dictionary with keys: open, high, low, close, volume
        
        Returns:
            Feature vector [momentum, volatility_proxy, activity_ratio]
            Returns None if insufficient history
        """
        # Extract OHLCV values
        open_price = bar['open']
        high_price = bar['high']
        low_price = bar['low']
        close_price = bar['close']
        volume = bar['volume']
        
        # Add to history
        self.price_history.append(close_price)
        self.volume_history.append(volume)
        
        # Need at least 2 bars for momentum, window_size for volume SMA
        if len(self.price_history) < 2:
            return None
        
        # Feature 1: Momentum (Log Returns)
        momentum = self._calculate_momentum()
        
        # Feature 2: Volatility Proxy (Normalized Range)
        volatility_proxy = self._calculate_volatility_proxy(high_price, low_price, open_price)
        
        # Feature 3: Activity Ratio (Relative Volume)
        activity_ratio = self._calculate_activity_ratio(volume)
        
        # Construct feature vector
        features = np.array([momentum, volatility_proxy, activity_ratio])
        
        # Store for normalization
        self.feature_history.append(features)
        
        return features
    
    def _calculate_momentum(self) -> float:
        """
        Calculate log returns: ln(Close_t / Close_{t-1})
        """
        if len(self.price_history) < 2:
            return 0.0
        
        close_t = self.price_history[-1]
        close_t_1 = self.price_history[-2]
        
        # Avoid log(0) or division by zero
        if close_t_1 == 0 or close_t == 0:
            return 0.0
        
        momentum = np.log(close_t / close_t_1)
        return momentum
    
    def _calculate_volatility_proxy(self, high: float, low: float, open_price: float) -> float:
        """
        Calculate normalized range: (High - Low) / Open
        Proxy for spread and liquidity consumption
        """
        if open_price == 0:
            return 0.0
        
        volatility_proxy = (high - low) / open_price
        return volatility_proxy
    
    def _calculate_activity_ratio(self, volume: float) -> float:
        """
        Calculate relative volume: Volume_t / SMA_20(Volume)
        Identifies anomalous liquidity demand
        """
        if len(self.volume_history) < self.window_size:
            # Not enough history - use current volume as baseline
            return 1.0
        
        volume_sma = np.mean(list(self.volume_history))
        
        if volume_sma == 0:
            return 1.0
        
        activity_ratio = volume / volume_sma
        return activity_ratio
    
    def get_normalized_features(self, features: np.ndarray) -> np.ndarray:
        """
        Normalize features using z-score (StandardScaler equivalent)
        Uses rolling window statistics
        
        Args:
            features: Raw feature vector
        
        Returns:
            Normalized feature vector
        """
        if len(self.feature_history) < 2:
            # Not enough history for normalization
            return features
        
        # Convert to numpy array
        feature_matrix = np.array(list(self.feature_history))
        
        # Calculate mean and std for each feature
        mean = np.mean(feature_matrix, axis=0)
        std = np.std(feature_matrix, axis=0)
        
        # Avoid division by zero
        std = np.where(std == 0, 1.0, std)
        
        # Z-score normalization
        normalized = (features - mean) / std
        
        return normalized
    
    def get_feature_dataframe(self) -> pd.DataFrame:
        """
        Get feature history as a pandas DataFrame
        Useful for model training and visualization
        """
        if len(self.feature_history) == 0:
            return pd.DataFrame(columns=['momentum', 'volatility_proxy', 'activity_ratio'])
        
        feature_matrix = np.array(list(self.feature_history))
        df = pd.DataFrame(
            feature_matrix,
            columns=['momentum', 'volatility_proxy', 'activity_ratio']
        )
        return df
    
    def reset(self):
        """Clear all history"""
        self.price_history.clear()
        self.volume_history.clear()
        self.feature_history.clear()
