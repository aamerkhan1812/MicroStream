"""
Regime Classifier - Hidden Markov Model
Estimates latent liquidity regimes from market microstructure features
"""

import numpy as np
import logging
import joblib
from pathlib import Path
from hmmlearn.hmm import GaussianHMM
from typing import Optional, Tuple
from collections import deque

logger = logging.getLogger(__name__)


class RegimeClassifier:
    """
    Hidden Markov Model for liquidity regime classification
    
    Hidden States:
    - State 0 (Stable Liquidity): Low volatility, consistent volume
    - State 1 (High Volatility): Directional flow, widening ranges  
    - State 2 (Liquidity Crisis): Extreme variance, volume spikes
    
    Uses Viterbi algorithm for Maximum Likelihood Estimate of current state
    """
    
    REGIME_NAMES = {
        0: "Stable Liquidity",
        1: "High Volatility",
        2: "Liquidity Crisis"
    }
    
    def __init__(self, n_components: int = 3, model_path: Optional[str] = None):
        """
        Args:
            n_components: Number of hidden states (default: 3)
            model_path: Path to pre-trained model (optional)
        """
        self.n_components = n_components
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        self.observation_history = deque(maxlen=100)  # Keep recent observations
        
        # Load or initialize model
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize a new Gaussian HMM"""
        logger.info(f"Initializing Gaussian HMM (n_components={self.n_components})")
        
        self.model = GaussianHMM(
            n_components=self.n_components,
            covariance_type="full",  # Full covariance matrix
            n_iter=100,
            random_state=42,
            verbose=False
        )
        
        logger.info("✓ Gaussian HMM initialized")
    
    def fit(self, X: np.ndarray):
        """
        Train the HMM on historical feature data
        
        Args:
            X: Feature matrix of shape (n_samples, n_features)
        """
        if X.shape[0] < self.n_components * 10:
            logger.warning(f"Insufficient data for training. Need at least {self.n_components * 10} samples.")
            return
        
        logger.info(f"Training Gaussian HMM on {X.shape[0]} samples...")
        
        try:
            self.model.fit(X)
            self.is_trained = True
            logger.info("✓ HMM training complete")
            
            # Log learned parameters
            self._log_model_parameters()
            
        except Exception as e:
            logger.error(f"HMM training failed: {e}", exc_info=True)
    
    def predict_regime(self, features: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Predict the current regime given a feature vector
        
        Args:
            features: Feature vector of shape (n_features,)
        
        Returns:
            Tuple of (regime_state, regime_probabilities)
            - regime_state: Most likely state (0, 1, or 2)
            - regime_probabilities: Probability distribution over states
        """
        if not self.is_trained:
            logger.warning("Model not trained yet. Returning default regime.")
            return 0, np.array([1.0, 0.0, 0.0])
        
        # Add to observation history
        self.observation_history.append(features)
        
        # Use recent history for better inference (sliding window)
        if len(self.observation_history) >= 10:
            X = np.array(list(self.observation_history)[-10:])
        else:
            X = features.reshape(1, -1)
        
        try:
            # Predict state sequence using Viterbi algorithm
            states = self.model.predict(X)
            current_state = states[-1]
            
            # Calculate state probabilities
            log_prob, posteriors = self.model.score_samples(X)
            regime_probs = posteriors[-1]  # Probabilities for current observation
            
            return int(current_state), regime_probs
            
        except Exception as e:
            logger.error(f"Regime prediction failed: {e}", exc_info=True)
            return 0, np.array([1.0, 0.0, 0.0])
    
    def get_regime_name(self, state: int) -> str:
        """Get human-readable regime name"""
        return self.REGIME_NAMES.get(state, f"Unknown State {state}")
    
    def get_transition_matrix(self) -> np.ndarray:
        """
        Get the learned transition matrix
        
        Returns:
            Matrix A where A[i,j] = P(state_t = j | state_{t-1} = i)
        """
        if not self.is_trained:
            return None
        
        return self.model.transmat_
    
    def get_emission_parameters(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the learned emission parameters (means and covariances)
        
        Returns:
            Tuple of (means, covariances)
        """
        if not self.is_trained:
            return None, None
        
        return self.model.means_, self.model.covars_
    
    def _log_model_parameters(self):
        """Log learned model parameters for debugging"""
        if not self.is_trained:
            return
        
        logger.info("=" * 60)
        logger.info("HMM Model Parameters")
        logger.info("=" * 60)
        
        # Transition matrix
        logger.info("\nTransition Matrix:")
        transmat = self.get_transition_matrix()
        for i in range(self.n_components):
            logger.info(f"  State {i} ({self.get_regime_name(i)}): {transmat[i]}")
        
        # Emission parameters
        means, covars = self.get_emission_parameters()
        logger.info("\nEmission Means (Feature Centroids):")
        for i in range(self.n_components):
            logger.info(f"  State {i} ({self.get_regime_name(i)}): {means[i]}")
        
        logger.info("=" * 60)
    
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
            self._log_model_parameters()
        except Exception as e:
            logger.error(f"Failed to load model from {path}: {e}")
            self._initialize_model()
    
    def reset_history(self):
        """Clear observation history"""
        self.observation_history.clear()
