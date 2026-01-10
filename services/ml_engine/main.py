"""
ML Intelligence Engine - Main Service
Tier 2: Consumes OHLCV bars, performs dual-model inference, publishes regime signals
"""

import json
import logging
import os
import numpy as np
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from dotenv import load_dotenv
from datetime import datetime

from feature_engineering import FeatureEngineer
from anomaly_detector import AnomalyDetector
from regime_classifier import RegimeClassifier

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLInferenceEngine:
    """
    Stateful ML inference engine
    Maintains sliding windows and executes dual-model inference
    """
    
    def __init__(self):
        # Kafka configuration
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.input_topic = os.getenv('KAFKA_RAW_BARS_TOPIC', 'market_raw_bars')
        self.output_topic = os.getenv('KAFKA_REGIME_SIGNALS_TOPIC', 'market_regime_signals')
        
        # ML components
        window_size = int(os.getenv('FEATURE_WINDOW_SIZE', 20))
        self.feature_engineer = FeatureEngineer(window_size=window_size)
        
        # Initialize models
        contamination = float(os.getenv('ISOLATION_FOREST_CONTAMINATION', 0.05))
        n_components = int(os.getenv('HMM_N_COMPONENTS', 3))
        
        self.anomaly_detector = AnomalyDetector(
            contamination=contamination,
            model_path='models/isolation_forest.pkl'
        )
        
        self.regime_classifier = RegimeClassifier(
            n_components=n_components,
            model_path='models/hmm_regime.pkl'
        )
        
        # Initialize Kafka clients
        self.consumer = None
        self.producer = None
        self._initialize_kafka()
    
    def _initialize_kafka(self):
        """Initialize Kafka consumer and producer"""
        logger.info(f"Initializing Kafka clients: {self.bootstrap_servers}")
        
        try:
            # Consumer for raw bars
            self.consumer = KafkaConsumer(
                self.input_topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',  # Start from latest for real-time
                enable_auto_commit=True,
                group_id='ml_engine_group'
            )
            
            # Producer for regime signals
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all'
            )
            
            logger.info("✓ Kafka clients initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka: {e}", exc_info=True)
            raise
    
    def run(self):
        """Main processing loop"""
        logger.info("=" * 60)
        logger.info("ML Intelligence Engine Starting")
        logger.info(f"Consuming from: {self.input_topic}")
        logger.info(f"Publishing to: {self.output_topic}")
        logger.info("=" * 60)
        
        try:
            for message in self.consumer:
                bar = message.value
                self._process_bar(bar)
                
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"Fatal error in processing loop: {e}", exc_info=True)
        finally:
            self._shutdown()
    
    def _process_bar(self, bar: dict):
        """
        Process a single OHLCV bar through the inference pipeline
        
        Pipeline:
        1. Feature Engineering: Calculate X_t
        2. Anomaly Detection: Isolation Forest score
        3. Regime Classification: HMM state inference
        4. Signal Generation: Publish composite signal
        """
        try:
            timestamp = bar['timestamp']
            
            # Step 1: Feature Engineering
            features = self.feature_engineer.add_bar(bar)
            
            if features is None:
                # Insufficient history
                return
            
            # Normalize features
            normalized_features = self.feature_engineer.get_normalized_features(features)
            
            # Step 2: Anomaly Detection
            anomaly_score = self.anomaly_detector.predict_anomaly_score(normalized_features)
            is_anomaly = self.anomaly_detector.is_anomaly(normalized_features)
            
            # Step 3: Regime Classification
            regime_state, regime_probs = self.regime_classifier.predict_regime(normalized_features)
            regime_name = self.regime_classifier.get_regime_name(regime_state)
            
            # Step 4: Generate composite signal
            signal = {
                'timestamp': timestamp,
                'datetime': datetime.fromtimestamp(timestamp / 1000).isoformat(),
                
                # Price data
                'open': bar['open'],
                'high': bar['high'],
                'low': bar['low'],
                'close': bar['close'],
                'volume': bar['volume'],
                
                # Features
                'features': {
                    'momentum': float(features[0]),
                    'volatility_proxy': float(features[1]),
                    'activity_ratio': float(features[2])
                },
                
                # Anomaly detection
                'anomaly_score': float(anomaly_score),
                'is_anomaly': bool(is_anomaly),
                
                # Regime classification
                'regime_state': int(regime_state),
                'regime_name': regime_name,
                'regime_probabilities': {
                    'stable': float(regime_probs[0]),
                    'volatile': float(regime_probs[1]),
                    'crisis': float(regime_probs[2])
                }
            }
            
            # Publish to Kafka
            self._publish_signal(signal)
            
            # Log periodically
            if timestamp % 600000 == 0:  # Every 10 minutes
                logger.info(
                    f"Signal: {signal['datetime']} | "
                    f"Regime: {regime_name} ({regime_probs[regime_state]:.2%}) | "
                    f"Anomaly: {anomaly_score:.3f} | "
                    f"Price: ${bar['close']:.2f}"
                )
            
        except Exception as e:
            logger.error(f"Error processing bar: {e}", exc_info=True)
    
    def _publish_signal(self, signal: dict):
        """Publish regime signal to Kafka"""
        try:
            key = str(signal['timestamp'])
            self.producer.send(self.output_topic, key=key.encode('utf-8'), value=signal)
            
        except KafkaError as e:
            logger.error(f"Failed to publish signal: {e}", exc_info=True)
    
    def _shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down ML engine...")
        
        if self.consumer:
            self.consumer.close()
        
        if self.producer:
            self.producer.flush()
            self.producer.close()
        
        logger.info("✓ ML engine shutdown complete")


def main():
    """Entry point"""
    engine = MLInferenceEngine()
    engine.run()


if __name__ == "__main__":
    main()
