"""
Market Observer - Ingestion Service
Tier 1: Connects to Binance WebSocket and streams aggregated OHLCV bars to Kafka
"""

import asyncio
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
import websockets
from dotenv import load_dotenv

from aggregator import TradeAggregator
from kafka_producer import KafkaProducerClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BinanceWebSocketClient:
    """
    WebSocket client for Binance aggTrade stream
    Handles connection stability, reconnection, and trade normalization
    """
    
    def __init__(self, symbol: str = "btcusdt"):
        self.symbol = symbol.lower()
        self.ws_url = os.getenv('BINANCE_WS_URL', f'wss://stream.binance.com:9443/ws/{self.symbol}@aggTrade')
        self.aggregator = TradeAggregator()
        self.kafka_producer = KafkaProducerClient()
        self.reconnect_delay = 1  # Start with 1 second
        self.max_reconnect_delay = 60  # Max 60 seconds
        self.is_running = False
        
    async def connect(self):
        """Main connection loop with exponential backoff"""
        self.is_running = True
        
        while self.is_running:
            try:
                logger.info(f"Connecting to Binance WebSocket: {self.ws_url}")
                async with websockets.connect(self.ws_url) as websocket:
                    logger.info("✓ Connected to Binance WebSocket")
                    self.reconnect_delay = 1  # Reset delay on successful connection
                    
                    await self._handle_messages(websocket)
                    
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"WebSocket connection closed: {e}")
                await self._reconnect()
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                await self._reconnect()
    
    async def _handle_messages(self, websocket):
        """Process incoming trade messages"""
        async for message in websocket:
            try:
                trade_data = json.loads(message)
                await self._process_trade(trade_data)
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {e}")
            except Exception as e:
                logger.error(f"Error processing trade: {e}", exc_info=True)
    
    async def _process_trade(self, trade: Dict[str, Any]):
        """
        Normalize and aggregate trade data
        
        Trade format from Binance:
        {
            "e": "aggTrade",
            "E": 1714521600000,  # Event time
            "s": "BTCUSDT",
            "a": 12345,          # Aggregate trade ID
            "p": "60672.01",     # Price
            "q": "0.5",          # Quantity
            "f": 100,            # First trade ID
            "l": 105,            # Last trade ID
            "T": 1714521600000,  # Trade time
            "m": true            # Is buyer maker
        }
        """
        
        normalized_trade = {
            'timestamp': trade['T'],  # Trade time in milliseconds
            'price': float(trade['p']),
            'quantity': float(trade['q']),
            'is_buyer_maker': trade['m']
        }
        
        # Aggregate trades into OHLCV bars
        completed_bar = self.aggregator.add_trade(normalized_trade)
        
        # If a 1-minute bar is complete, send to Kafka
        if completed_bar:
            await self._publish_bar(completed_bar)
    
    async def _publish_bar(self, bar: Dict[str, Any]):
        """Publish completed OHLCV bar to Kafka"""
        try:
            self.kafka_producer.send_bar(bar)
            
            # Log every 10th bar to avoid spam
            if bar['timestamp'] % 600000 == 0:  # Every 10 minutes
                logger.info(f"Published bar: {datetime.fromtimestamp(bar['timestamp']/1000)} | "
                          f"Close: {bar['close']:.2f} | Volume: {bar['volume']:.4f}")
                
        except Exception as e:
            logger.error(f"Failed to publish bar to Kafka: {e}", exc_info=True)
    
    async def _reconnect(self):
        """Exponential backoff reconnection strategy"""
        logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)
        
        # Exponential backoff
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
    
    async def stop(self):
        """Graceful shutdown"""
        logger.info("Stopping WebSocket client...")
        self.is_running = False
        self.kafka_producer.close()


async def main():
    """Entry point for the ingestion service"""
    logger.info("=" * 60)
    logger.info("Market Observer - Ingestion Service Starting")
    logger.info("=" * 60)
    
    symbol = os.getenv('SYMBOL', 'BTCUSDT')
    client = BinanceWebSocketClient(symbol=symbol)
    
    try:
        await client.connect()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await client.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
