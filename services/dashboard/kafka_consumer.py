"""
Kafka Consumer for Regime Signals
Consumes market_regime_signals topic for dashboard visualization
"""

import json
import logging
import os
from typing import List, Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class RegimeSignalConsumer:
    """Kafka consumer for regime signals"""
    
    def __init__(self):
        bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.topic = os.getenv('KAFKA_REGIME_SIGNALS_TOPIC', 'market_regime_signals')
        
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=bootstrap_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',  # Start from beginning for dashboard
                enable_auto_commit=True,
                group_id='dashboard_group',
                consumer_timeout_ms=1000  # Timeout for polling
            )
            
            logger.info(f"✓ Kafka consumer initialized for topic: {self.topic}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            self.consumer = None
    
    def get_latest_signals(self, max_count: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch latest signals from Kafka
        
        Args:
            max_count: Maximum number of signals to fetch
        
        Returns:
            List of signal dictionaries
        """
        if self.consumer is None:
            return []
        
        signals = []
        
        try:
            # Poll for messages
            messages = self.consumer.poll(timeout_ms=1000, max_records=max_count)
            
            for topic_partition, records in messages.items():
                for record in records:
                    signals.append(record.value)
            
        except KafkaError as e:
            logger.error(f"Error consuming messages: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        return signals
    
    def close(self):
        """Close the consumer"""
        if self.consumer:
            self.consumer.close()
