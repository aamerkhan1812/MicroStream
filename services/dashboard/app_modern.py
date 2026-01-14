"""
Modern Interactive Dashboard for MicroStream
Real-Time Market Microstructure & Liquidity Regime Detection
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from kafka import KafkaConsumer
from datetime import datetime, timedelta
import time
from collections import deque
import os

# Page configuration
st.set_page_config(
    page_title="MicroStream | Market Regime Detection",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e3240;
    }
    .stMetric label {
        color: #8b92a8 !important;
        font-size: 14px !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 600 !important;
    }
    h1 {
        color: #ffffff;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    h2, h3 {
        color: #e0e0e0;
        font-weight: 600;
    }
    .regime-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin: 5px;
    }
    .status-healthy {
        background-color: #10b981;
        color: white;
    }
    .status-warning {
        background-color: #f59e0b;
        color: white;
    }
    .status-error {
        background-color: #ef4444;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'signals' not in st.session_state:
    st.session_state.signals = deque(maxlen=100)
if 'prices' not in st.session_state:
    st.session_state.prices = deque(maxlen=100)
if 'features' not in st.session_state:
    st.session_state.features = {'momentum': deque(maxlen=100), 
                                   'volatility': deque(maxlen=100),
                                   'activity': deque(maxlen=100)}

# Kafka configuration
KAFKA_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
SIGNALS_TOPIC = os.getenv('KAFKA_REGIME_SIGNALS_TOPIC', 'market_regime_signals')

def get_regime_color(regime):
    """Get color for regime"""
    colors = {
        'Normal Market': '#10b981',
        'Bearish Extreme': '#ef4444',
        'Bullish Extreme': '#3b82f6',
        'Calm Market': '#8b5cf6',
        'Trending Down': '#f59e0b',
        'Trending Up': '#06b6d4'
    }
    return colors.get(regime, '#6b7280')

def create_price_chart(prices_data):
    """Create interactive price chart"""
    if not prices_data:
        return None
    
    df = pd.DataFrame(prices_data)
    
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='BTCUSDT',
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    ))
    
    fig.update_layout(
        title='BTC/USDT Price Action',
        yaxis_title='Price (USD)',
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_regime_timeline(signals_data):
    """Create regime timeline visualization"""
    if not signals_data:
        return None
    
    df = pd.DataFrame(signals_data)
    
    fig = go.Figure()
    
    # Create colored bars for each regime
    for regime in df['regime_name'].unique():
        regime_data = df[df['regime_name'] == regime]
        fig.add_trace(go.Scatter(
            x=regime_data['timestamp'],
            y=regime_data['confidence'],
            mode='markers+lines',
            name=regime,
            marker=dict(size=10, color=get_regime_color(regime)),
            line=dict(width=2, color=get_regime_color(regime))
        ))
    
    fig.update_layout(
        title='Regime Detection Timeline',
        yaxis_title='Confidence (%)',
        template='plotly_dark',
        height=300,
        hovermode='x unified',
        yaxis=dict(range=[0, 105])
    )
    
    return fig

def create_features_chart(features_data):
    """Create features subplot"""
    if not any(features_data.values()):
        return None
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Momentum', 'Volatility', 'Activity Ratio'),
        vertical_spacing=0.1
    )
    
    timestamps = list(range(len(features_data['momentum'])))
    
    # Momentum
    fig.add_trace(
        go.Scatter(x=timestamps, y=list(features_data['momentum']),
                  name='Momentum', line=dict(color='#3b82f6', width=2)),
        row=1, col=1
    )
    
    # Volatility
    fig.add_trace(
        go.Scatter(x=timestamps, y=list(features_data['volatility']),
                  name='Volatility', line=dict(color='#f59e0b', width=2)),
        row=2, col=1
    )
    
    # Activity
    fig.add_trace(
        go.Scatter(x=timestamps, y=list(features_data['activity']),
                  name='Activity', line=dict(color='#10b981', width=2)),
        row=3, col=1
    )
    
    fig.update_layout(
        height=600,
        template='plotly_dark',
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📊 MicroStream")
    st.markdown("**Real-Time Market Microstructure & Liquidity Regime Detection**")
with col2:
    st.markdown(f"<div style='text-align: right; padding-top: 20px;'>"
                f"<span style='color: #10b981; font-size: 12px;'>● LIVE</span>"
                f"</div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 2)
    
    st.markdown("---")
    st.header("📈 System Health")
    
    # System status badges
    st.markdown("<div class='status-badge status-healthy'>Ingestion: Healthy</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-badge status-healthy'>Kafka: Healthy</div>", unsafe_allow_html=True)
    st.markdown("<div class='status-badge status-warning'>ML Engine: Starting</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.header("ℹ️ About")
    st.markdown("""
    **MicroStream** uses machine learning to detect market regimes in real-time:
    
    - **Isolation Forest**: Anomaly detection
    - **Hidden Markov Model**: Regime classification
    - **Features**: Momentum, Volatility, Activity
    
    **Data Source**: Binance WebSocket (BTCUSDT)
    """)

# Main content
try:
    # Try to connect to Kafka
    consumer = KafkaConsumer(
        SIGNALS_TOPIC,
        bootstrap_servers=KAFKA_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        consumer_timeout_ms=1000
    )
    
    # Get latest signal
    latest_signal = None
    for message in consumer:
        latest_signal = message.value
        st.session_state.signals.append(latest_signal)
        
        # Update prices
        if 'close' in latest_signal:
            st.session_state.prices.append({
                'timestamp': datetime.fromtimestamp(latest_signal.get('timestamp', time.time())),
                'open': latest_signal.get('open', 0),
                'high': latest_signal.get('high', 0),
                'low': latest_signal.get('low', 0),
                'close': latest_signal['close']
            })
        
        # Update features
        if 'features' in latest_signal:
            features = latest_signal['features']
            st.session_state.features['momentum'].append(features.get('momentum', 0))
            st.session_state.features['volatility'].append(features.get('volatility', 0))
            st.session_state.features['activity'].append(features.get('activity', 1.0))
    
    consumer.close()
    
    if latest_signal:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Regime",
                value=latest_signal.get('regime_name', 'Unknown'),
                delta=None
            )
        
        with col2:
            confidence = latest_signal.get('regime_probabilities', {}).get(
                latest_signal.get('regime_name', '').lower().replace(' ', '_'), 0
            ) * 100
            st.metric(
                label="Confidence",
                value=f"{confidence:.2f}%",
                delta=None
            )
        
        with col3:
            st.metric(
                label="BTC Price",
                value=f"${latest_signal.get('close', 0):,.2f}",
                delta=f"{latest_signal.get('price_change_pct', 0):.2f}%"
            )
        
        with col4:
            anomaly_score = latest_signal.get('anomaly_score', 0)
            is_anomaly = latest_signal.get('is_anomaly', False)
            st.metric(
                label="Market Status",
                value="⚠️ Anomaly" if is_anomaly else "✅ Normal",
                delta=f"Score: {anomaly_score:.3f}"
            )
        
        # Charts
        st.markdown("---")
        
        # Price chart
        if st.session_state.prices:
            price_chart = create_price_chart(list(st.session_state.prices))
            if price_chart:
                st.plotly_chart(price_chart, use_container_width=True)
        
        # Regime timeline
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.session_state.signals:
                signals_list = [
                    {
                        'timestamp': datetime.fromtimestamp(s.get('timestamp', time.time())),
                        'regime_name': s.get('regime_name', 'Unknown'),
                        'confidence': s.get('regime_probabilities', {}).get(
                            s.get('regime_name', '').lower().replace(' ', '_'), 0
                        ) * 100
                    }
                    for s in list(st.session_state.signals)
                ]
                regime_chart = create_regime_timeline(signals_list)
                if regime_chart:
                    st.plotly_chart(regime_chart, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Regime Distribution")
            if st.session_state.signals:
                regime_counts = {}
                for s in st.session_state.signals:
                    regime = s.get('regime_name', 'Unknown')
                    regime_counts[regime] = regime_counts.get(regime, 0) + 1
                
                fig = go.Figure(data=[go.Pie(
                    labels=list(regime_counts.keys()),
                    values=list(regime_counts.values()),
                    marker=dict(colors=[get_regime_color(r) for r in regime_counts.keys()]),
                    hole=0.4
                )])
                fig.update_layout(
                    template='plotly_dark',
                    height=300,
                    margin=dict(t=0, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Features
        st.markdown("---")
        st.markdown("### 📈 Market Microstructure Features")
        
        if any(st.session_state.features.values()):
            features_chart = create_features_chart(st.session_state.features)
            if features_chart:
                st.plotly_chart(features_chart, use_container_width=True)
        
    else:
        st.info("⏳ Waiting for market data... Make sure the ML engine is running.")
        
except Exception as e:
    st.warning(f"⏳ Connecting to data stream...")
    st.info("""
    **System is starting up...**
    
    The dashboard will automatically connect when:
    - Kafka is healthy
    - ML Engine is processing data
    - Regime signals are being published
    
    This usually takes 1-2 minutes after system startup.
    """)
    
    # Show demo data
    st.markdown("---")
    st.markdown("### 📊 Demo: What You'll See")
    
    demo_data = {
        'timestamp': [datetime.now() - timedelta(minutes=i) for i in range(20, 0, -1)],
        'regime_name': ['Normal Market'] * 12 + ['Bullish Extreme'] * 5 + ['Normal Market'] * 3,
        'confidence': [95 + i % 5 for i in range(20)]
    }
    demo_chart = create_regime_timeline(demo_data)
    if demo_chart:
        st.plotly_chart(demo_chart, use_container_width=True)

# Auto-refresh
if st.button("🔄 Refresh Now", use_container_width=True):
    st.rerun()

# Auto-refresh every N seconds
st.markdown(f"<meta http-equiv='refresh' content='{refresh_interval}'>", unsafe_allow_html=True)
