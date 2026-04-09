import streamlit as st
import pandas as pd
import json
import time
from kafka import KafkaConsumer
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="DARWIN | Kernel Intelligence", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. Modern Cyber-Security CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'JetBrains Mono', monospace;
        background-color: #050505;
        color: #00ff41; 
    }
    .stMetric {
        background: rgba(15, 15, 15, 0.9);
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
    }
    [data-testid="stMetricValue"] > div { color: #ff4b4b !important; }
    .status-online { color: #00ff41; font-weight: bold; border: 1px solid #00ff41; padding: 5px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Kafka Consumer Setup (Cached)
@st.cache_resource
def get_consumer():
    try:
        return KafkaConsumer(
            'syscalls-proto',
            bootstrap_servers=['localhost:19092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True,
            request_timeout_ms=31000, 
            session_timeout_ms=30000
        )
    except Exception as e:
        return None

# 4. State Management
if 'events' not in st.session_state:
    st.session_state.events = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center; color: white;'>🛡️ DARWIN SYSTEM</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 0.8rem;'>REAL-TIME eBPF KERNEL TELEMETRY</p>", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🛠️ CORE CONFIG")
    consumer = get_consumer()
    if consumer:
        st.markdown('<p class="status-online">🟢 KAFKA CONNECTED</p>', unsafe_allow_html=True)
    else:
        st.error("🔴 KAFKA DISCONNECTED")
    
    st.metric("MODEL", "Isolation Forest")
    total_placeholder = st.empty()
    st.divider()
    st.caption("v2.4.0-stable | 2026")

# --- MAIN LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### ⚡ LIVE INTERCEPT")
    table_placeholder = st.empty()

with col2:
    st.markdown("### 📊 FREQUENCY")
    chart_placeholder = st.empty()
    st.markdown("### 🧪 THREAT INDEX")
    gauge_placeholder = st.empty()

# 5. THE DATA REFRESH FUNCTION (The Fix)
# We use a controlled loop that clears the placeholder instead of re-registering
def run_dashboard_loop():
    while True:
        records = consumer.poll(timeout_ms=100)
        
        if records:
            for tp, messages in records.items():
                for msg in messages:
                    event = msg.value
                    event['time'] = time.strftime('%H:%M:%S')
                    st.session_state.events.append(event)
            
            # Keep buffer small
            if len(st.session_state.events) > 50:
                st.session_state.events = st.session_state.events[-50:]

        if st.session_state.events:
            df = pd.DataFrame(st.session_state.events)
            
            # 1. Update Sidebar Metric
            total_placeholder.metric("TOTAL EVENTS", len(df))

            # 2. Update Table
            table_placeholder.dataframe(
                df.iloc[::-1][['time', 'comm', 'pid']], 
                width=2000, # Maximize width
                hide_index=True
            )

            # 3. Update Bar Chart
            counts = df['comm'].value_counts().reset_index()
            counts.columns = ['Process', 'Count']
            fig = px.bar(
                counts, x='Process', y='Count', 
                color='Count', color_continuous_scale='Turbo',
                template="plotly_dark"
            )
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10))
            chart_placeholder.plotly_chart(fig, use_container_width=True)

            # 4. Update Gauge
            unique_procs = len(df['comm'].unique())
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = unique_procs,
                title = {'text': "Entropy Score", 'font': {'size': 14}},
                gauge = {'axis': {'range': [None, 10]}, 'bar': {'color': "#ff4b4b"}}
            ))
            fig_gauge.update_layout(height=200, margin=dict(t=30, b=0), template="plotly_dark")
            gauge_placeholder.plotly_chart(fig_gauge, use_container_width=True)

        time.sleep(0.2) # Throttled to 5 FPS for stability

# Launch the loop
if consumer:
    try:
        run_dashboard_loop()
    except Exception as e:
        # If the app tries to rerun, this catches it and keeps the loop primary
        st.warning("Re-syncing with Kernel...")
        time.sleep(1)
        st.rerun()
