"""
Trade Aggregator
Converts raw trades into 1-minute OHLCV bars using tumbling window aggregation
"""

import logging
from typing import Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class TradeAggregator:
    """
    Aggregates raw trades into 1-minute OHLCV candles
    Uses event-time alignment (not processing-time)
    """
    
    def __init__(self, window_size_ms: int = 60000):
        """
        Args:
            window_size_ms: Window size in milliseconds (default: 60000 = 1 minute)
        """
        self.window_size_ms = window_size_ms
        self.current_window = None
        self.current_bar = None
        
    def add_trade(self, trade: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a trade to the aggregator
        
        Args:
            trade: {
                'timestamp': int (milliseconds),
                'price': float,
                'quantity': float,
                'is_buyer_maker': bool
            }
        
        Returns:
            Completed OHLCV bar if window closed, None otherwise
        """
        timestamp = trade['timestamp']
        price = trade['price']
        quantity = trade['quantity']
        
        # Calculate window boundaries (tumbling window)
        window_start = (timestamp // self.window_size_ms) * self.window_size_ms
        window_end = window_start + self.window_size_ms
        
        # Check if we've moved to a new window
        if self.current_window is None:
            # First trade - initialize window
            self._initialize_window(window_start, trade)
            return None
            
        elif window_start > self.current_window:
            # New window - emit completed bar and start new one
            completed_bar = self._finalize_bar()
            self._initialize_window(window_start, trade)
            return completed_bar
            
        else:
            # Same window - update current bar
            self._update_bar(trade)
            return None
    
    def _initialize_window(self, window_start: int, trade: Dict[str, Any]):
        """Initialize a new aggregation window"""
        self.current_window = window_start
        
        self.current_bar = {
            'timestamp': window_start,
            'open': trade['price'],
            'high': trade['price'],
            'low': trade['price'],
            'close': trade['price'],
            'volume': trade['quantity'],
            'num_trades': 1,
            'taker_buy_volume': trade['quantity'] if not trade['is_buyer_maker'] else 0.0,
            'taker_sell_volume': trade['quantity'] if trade['is_buyer_maker'] else 0.0
        }
    
    def _update_bar(self, trade: Dict[str, Any]):
        """Update the current bar with a new trade"""
        if self.current_bar is None:
            return
        
        price = trade['price']
        quantity = trade['quantity']
        
        # Update OHLC
        self.current_bar['high'] = max(self.current_bar['high'], price)
        self.current_bar['low'] = min(self.current_bar['low'], price)
        self.current_bar['close'] = price  # Last trade becomes close
        
        # Update volume
        self.current_bar['volume'] += quantity
        self.current_bar['num_trades'] += 1
        
        # Update taker volumes
        if trade['is_buyer_maker']:
            self.current_bar['taker_sell_volume'] += quantity
        else:
            self.current_bar['taker_buy_volume'] += quantity
    
    def _finalize_bar(self) -> Dict[str, Any]:
        """Finalize and return the completed bar"""
        if self.current_bar is None:
            return None
        
        bar = self.current_bar.copy()
        
        # Add derived metrics
        bar['close_time'] = self.current_window + self.window_size_ms - 1
        bar['quote_volume'] = bar['volume'] * bar['close']  # Approximate
        
        logger.debug(f"Completed bar at {bar['timestamp']}: "
                    f"O={bar['open']:.2f} H={bar['high']:.2f} "
                    f"L={bar['low']:.2f} C={bar['close']:.2f} V={bar['volume']:.4f}")
        
        return bar
    
    def get_current_bar(self) -> Optional[Dict[str, Any]]:
        """Get the current incomplete bar (for monitoring)"""
        return self.current_bar.copy() if self.current_bar else None
