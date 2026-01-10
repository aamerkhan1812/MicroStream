"""
Redis adapter for Railway deployment
Replaces Kafka with Redis for lower resource usage
"""
import redis
import json
import os
from typing import Optional, Dict, Any

class RedisProducer:
    """Redis-based message producer (replaces Kafka producer)"""
    
    def __init__(self, topic: str):
        self.topic = topic
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
    
    def send(self, value: Dict[Any, Any]):
        """Send message to Redis list"""
        self.redis_client.rpush(
            self.topic,
            json.dumps(value)
        )

class RedisConsumer:
    """Redis-based message consumer (replaces Kafka consumer)"""
    
    def __init__(self, topic: str):
        self.topic = topic
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
    
    def poll(self, timeout: float = 1.0) -> Optional[Dict[Any, Any]]:
        """Poll for messages from Redis list"""
        result = self.redis_client.blpop(self.topic, timeout=int(timeout))
        if result:
            _, message = result
            return json.loads(message)
        return None
    
    def get_latest_signals(self, max_count: int = 100):
        """Get latest N signals"""
        messages = self.redis_client.lrange(self.topic, -max_count, -1)
        return [json.loads(msg) for msg in messages]
