"""
Market Regime Monitor - Streamlit Dashboard
Tier 3: Real-time visualization of market microstructure and liquidity regimes
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import time
from collections import deque

from kafka_consumer import RegimeSignalConsumer

# Page configuration
st.set_page_config(
    page_title="Market Regime Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for regime colors
st.markdown("""
<style>
    .regime-stable { background-color: rgba(0, 255, 0, 0.1); }
    .regime-volatile { background-color: rgba(255, 255, 0, 0.1); }
    .regime-crisis { background-color: rgba(255, 0, 0, 0.1); }
</style>
""", unsafe_allow_html=True)


class DashboardState:
    """Maintains dashboard state across updates"""
    
    def __init__(self, max_history=500):
        self.max_history = max_history
        self.signals = deque(maxlen=max_history)
        self.consumer = RegimeSignalConsumer()
        
    def update(self):
        """Fetch latest signals from Kafka"""
        new_signals = self.consumer.get_latest_signals(max_count=10)
        
        for signal in new_signals:
            self.signals.append(signal)
    
    def get_dataframe(self) -> pd.DataFrame:
        """Convert signals to pandas DataFrame"""
        if not self.signals:
            return pd.DataFrame()
        
        df = pd.DataFrame(list(self.signals))
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df


def create_candlestick_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create candlestick chart with regime background coloring
    """
    if df.empty:
        return go.Figure()
    
    # Create figure with secondary y-axis
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=('Price Action with Regime Background', 'Anomaly Score', 'Volume')
    )
    
    # Add candlestick
    fig.add_trace(
        go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='BTCUSDT',
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        ),
        row=1, col=1
    )
    
    # Add regime background coloring
    regime_colors = {
        0: 'rgba(0, 255, 0, 0.1)',    # Stable - Green
        1: 'rgba(255, 255, 0, 0.1)',  # Volatile - Yellow
        2: 'rgba(255, 0, 0, 0.1)'     # Crisis - Red
    }
    
    # Group consecutive regimes for efficient rendering
    current_regime = None
    regime_start = None
    
    for idx, row in df.iterrows():
        if row['regime_state'] != current_regime:
            # Regime changed - draw previous regime block
            if current_regime is not None and regime_start is not None:
                fig.add_vrect(
                    x0=regime_start,
                    x1=row['datetime'],
                    fillcolor=regime_colors[current_regime],
                    layer="below",
                    line_width=0,
                    row=1, col=1
                )
            
            current_regime = row['regime_state']
            regime_start = row['datetime']
    
    # Draw final regime block
    if current_regime is not None and regime_start is not None:
        fig.add_vrect(
            x0=regime_start,
            x1=df['datetime'].iloc[-1],
            fillcolor=regime_colors[current_regime],
            layer="below",
            line_width=0,
            row=1, col=1
        )
    
    # Add anomaly score
    fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['anomaly_score'],
            mode='lines',
            name='Anomaly Score',
            line=dict(color='purple', width=2),
            fill='tozeroy'
        ),
        row=2, col=1
    )
    
    # Add anomaly threshold line
    fig.add_hline(y=-0.5, line_dash="dash", line_color="red", row=2, col=1)
    
    # Add volume bars
    colors = ['red' if row['close'] < row['open'] else 'green' for _, row in df.iterrows()]
    fig.add_trace(
        go.Bar(
            x=df['datetime'],
            y=df['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=3, col=1
    )
    
    # Update layout
    fig.update_layout(
        title='Real-Time Market Microstructure Monitor',
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True,
        hovermode='x unified'
    )
    
    fig.update_yaxes(title_text="Price (USDT)", row=1, col=1)
    fig.update_yaxes(title_text="Score", row=2, col=1)
    fig.update_yaxes(title_text="Volume (BTC)", row=3, col=1)
    
    return fig


def create_regime_probability_chart(df: pd.DataFrame) -> go.Figure:
    """Create stacked area chart of regime probabilities"""
    if df.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # Extract probabilities
    stable_probs = [s['stable'] for s in df['regime_probabilities']]
    volatile_probs = [s['volatile'] for s in df['regime_probabilities']]
    crisis_probs = [s['crisis'] for s in df['regime_probabilities']]
    
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=stable_probs,
        mode='lines',
        name='Stable Liquidity',
        stackgroup='one',
        fillcolor='rgba(0, 255, 0, 0.3)'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=volatile_probs,
        mode='lines',
        name='High Volatility',
        stackgroup='one',
        fillcolor='rgba(255, 255, 0, 0.3)'
    ))
    
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=crisis_probs,
        mode='lines',
        name='Liquidity Crisis',
        stackgroup='one',
        fillcolor='rgba(255, 0, 0, 0.3)'
    ))
    
    fig.update_layout(
        title='Regime Probability Distribution',
        yaxis=dict(title='Probability', range=[0, 1]),
        xaxis_title='Time',
        height=300,
        hovermode='x unified'
    )
    
    return fig


def main():
    """Main dashboard application"""
    
    # Title
    st.title("🎯 Real-Time Market Microstructure & Liquidity Regime Monitor")
    st.markdown("---")
    
    # Initialize state
    if 'dashboard_state' not in st.session_state:
        st.session_state.dashboard_state = DashboardState()
    
    state = st.session_state.dashboard_state
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        refresh_interval = st.slider("Refresh interval (seconds)", 1, 10, 2)
        
        st.markdown("---")
        st.header("📊 Current Status")
        
        # Fetch latest data
        state.update()
        df = state.get_dataframe()
        
        if not df.empty:
            latest = df.iloc[-1]
            
            # Current regime
            regime_names = {
                0: "🟢 Stable Liquidity",
                1: "🟡 High Volatility",
                2: "🔴 Liquidity Crisis"
            }
            
            st.metric(
                "Current Regime",
                regime_names[latest['regime_state']],
                delta=f"{latest['regime_probabilities'][list(latest['regime_probabilities'].keys())[latest['regime_state']]]:.1%} confidence"
            )
            
            # Current price
            st.metric(
                "BTC Price",
                f"${latest['close']:,.2f}",
                delta=f"{((latest['close'] - latest['open']) / latest['open'] * 100):.2f}%"
            )
            
            # Anomaly status
            anomaly_status = "⚠️ ANOMALY DETECTED" if latest['is_anomaly'] else "✅ Normal"
            st.metric("Microstructure Status", anomaly_status)
            
            st.markdown("---")
            st.caption(f"Last update: {latest['datetime']}")
            st.caption(f"Total signals: {len(df)}")
    
    # Main content
    if df.empty:
        st.info("⏳ Waiting for market data... Make sure the ingestion and ML services are running.")
    else:
        # Main chart
        st.plotly_chart(create_candlestick_chart(df), width="stretch")
        
        # Regime probabilities
        st.plotly_chart(create_regime_probability_chart(df), width="stretch")
        
        # Feature metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📈 Momentum")
            momentum_values = [f['momentum'] for f in df['features']]
            st.line_chart(pd.DataFrame({'Momentum': momentum_values}))
        
        with col2:
            st.subheader("📊 Volatility Proxy")
            volatility_values = [f['volatility_proxy'] for f in df['features']]
            st.line_chart(pd.DataFrame({'Volatility': volatility_values}))
        
        with col3:
            st.subheader("🔄 Activity Ratio")
            activity_values = [f['activity_ratio'] for f in df['features']]
            st.line_chart(pd.DataFrame({'Activity': activity_values}))
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
