"""
Kafka Producer Client
Publishes aggregated OHLCV bars to Kafka topic
Supports Redis mode for Railway deployment
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
import gzip

# Check if running in Redis mode (Railway)
REDIS_MODE = os.getenv('REDIS_MODE', '0') == '1'
if REDIS_MODE:
    import sys
    sys.path.append('..')
    from redis_adapter import RedisProducer

logger = logging.getLogger(__name__)


class KafkaProducerClient:
    """Kafka producer for streaming OHLCV bars"""
    
    def __init__(self, bootstrap_servers: str, topic: str):
        """
        Initialize Kafka producer (or Redis in Railway mode)
        
        Args:
            bootstrap_servers: Kafka broker addresses (ignored in Redis mode)
            topic: Topic name to publish to
        """
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        
        try:
            if REDIS_MODE:
                # Use Redis for Railway
                self.producer = RedisProducer(topic)
                logger.info(f"Redis producer initialized for topic: {topic}")
            else:
                # Use Kafka for local deployment
                self.producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers.split(','),
                    value_serializer=lambda v: gzip.compress(
                        json.dumps(v).encode('utf-8')
                    ),
                    compression_type='gzip',
                    acks='all',  # Wait for all replicas
                    retries=3,
                    max_in_flight_requests_per_connection=1,  # Ensure ordering
                )
                logger.info(f"Kafka producer initialized for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to initialize producer: {e}", exc_info=True)
            raise
    
    def send_bar(self, bar: Dict[str, Any]) -> bool:
        """
        Send OHLCV bar to Kafka or Redis
        
        Args:
            bar: Dictionary containing bar data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if REDIS_MODE:
                # Send to Redis
                self.producer.send(bar)
                logger.debug(f"Bar sent to Redis topic: {self.topic}")
            else:
                # Send to Kafka
                future = self.producer.send(self.topic, value=bar)
                
                # Wait for confirmation (with timeout)
                record_metadata = future.get(timeout=10)
                
                logger.debug(
                    f"Bar sent to {self.topic} "
                    f"(partition: {record_metadata.partition}, "
                    f"offset: {record_metadata.offset})"
                )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send bar to Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending bar: {e}")
            return False
    
    def flush(self):
        """Flush pending messages"""
        self.producer.flush()
    
    def close(self):
        """Close the producer gracefully"""
        logger.info("Closing Kafka producer...")
        self.producer.flush()
        self.producer.close()
        logger.info("✓ Kafka producer closed")
