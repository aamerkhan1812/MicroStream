"""
Kafka Producer Client
Publishes OHLCV bars to the market_raw_bars topic
"""

import json
import logging
import os
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    """Kafka producer for streaming OHLCV bars"""
    
    def __init__(self):
        bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
        self.topic = os.getenv('KAFKA_RAW_BARS_TOPIC', 'market_raw_bars')
        
        logger.info(f"Initializing Kafka producer: {bootstrap_servers}")
        
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=1,  # Ensure ordering
                compression_type='gzip'
            )
            logger.info("✓ Kafka producer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}", exc_info=True)
            raise
    
    def send_bar(self, bar: Dict[str, Any]):
        """
        Send OHLCV bar to Kafka topic
        
        Args:
            bar: OHLCV bar dictionary with keys:
                - timestamp, open, high, low, close, volume, etc.
        """
        try:
            # Use timestamp as key for partitioning
            key = str(bar['timestamp'])
            
            # Send to Kafka
            future = self.producer.send(self.topic, key=key, value=bar)
            
            # Optional: Wait for acknowledgment (blocking)
            # record_metadata = future.get(timeout=10)
            # logger.debug(f"Sent to partition {record_metadata.partition} at offset {record_metadata.offset}")
            
        except KafkaError as e:
            logger.error(f"Kafka error while sending bar: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error while sending bar: {e}", exc_info=True)
            raise
    
    def flush(self):
        """Flush pending messages"""
        self.producer.flush()
    
    def close(self):
        """Close the producer gracefully"""
        logger.info("Closing Kafka producer...")
        self.producer.flush()
        self.producer.close()
        logger.info("✓ Kafka producer closed")
