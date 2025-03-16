import streamlit as st
import io
import os
from PIL import Image
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from chart_analyzer import analyze_chart
from ai_suggestions import get_trading_suggestion
import utils

# Page configuration
st.set_page_config(
    page_title="AI Stock Chart Analyzer",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title("AI Stock Chart Analyzer")
st.markdown("""
Upload stock chart images for AI-powered analysis. The tool will identify patterns, 
trends, and key technical indicators to provide trading insights.
""")

# Sidebar with timeframe selection
st.sidebar.header("Chart Settings")
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    options=["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W"],
    index=2
)

# Upload section
st.header("Upload Stock Chart")
uploaded_file = st.file_uploader("Choose a chart image...", type=["jpg", "jpeg", "png"])

# Initialize session state if not exist
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
    
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Process uploaded image
if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_column_width=True)
    
    # Convert to OpenCV format
    image_array = np.array(image)
    
    # Analyze button
    if st.button("Analyze Chart"):
        with st.spinner("Analyzing chart... This may take a moment."):
            # Perform analysis
            try:
                analysis_results = analyze_chart(image_array, timeframe)
                trading_suggestion = get_trading_suggestion(analysis_results, timeframe)
                
                # Store results in session state
                st.session_state.analysis_results = {
                    "patterns": analysis_results["patterns"],
                    "indicators": analysis_results["indicators"],
                    "trading_suggestion": trading_suggestion
                }
                st.session_state.analysis_complete = True
                st.rerun()
            except Exception as e:
                st.error(f"Error analyzing chart: {str(e)}")

# Display results if analysis is complete
if st.session_state.analysis_complete and st.session_state.analysis_results is not None:
    results = st.session_state.analysis_results
    
    st.header("Analysis Results")
    
    # Display timeframe
    st.subheader(f"Analysis for {timeframe} Timeframe")
    
    # Create tabs for different result sections
    tab1, tab2, tab3 = st.tabs(["Patterns & Trends", "Technical Indicators", "Trading Suggestion"])
    
    with tab1:
        st.subheader("Detected Patterns")
        if results["patterns"]:
            for pattern in results["patterns"]:
                st.markdown(f"**{pattern['name']}**: {pattern['description']}")
                st.progress(pattern['confidence'])
                st.markdown(f"Confidence: {pattern['confidence']:.2f}")
        else:
            st.info("No significant patterns detected.")
    
    with tab2:
        st.subheader("Technical Indicators")
        indicators = results["indicators"]
        
        # Display Moving Averages
        st.markdown("##### Moving Averages")
        ma_df = pd.DataFrame({
            "Type": ["SMA 20", "SMA 50", "SMA 200", "EMA 12", "EMA 26"],
            "Value": [
                indicators["moving_averages"]["sma_20"]["value"],
                indicators["moving_averages"]["sma_50"]["value"],
                indicators["moving_averages"]["sma_200"]["value"],
                indicators["moving_averages"]["ema_12"]["value"],
                indicators["moving_averages"]["ema_26"]["value"]
            ],
            "Trend": [
                indicators["moving_averages"]["sma_20"]["trend"],
                indicators["moving_averages"]["sma_50"]["trend"],
                indicators["moving_averages"]["sma_200"]["trend"],
                indicators["moving_averages"]["ema_12"]["trend"],
                indicators["moving_averages"]["ema_26"]["trend"]
            ]
        })
        st.dataframe(ma_df)
        
        # Display Oscillators
        st.markdown("##### Oscillators")
        col1, col2 = st.columns(2)
        
        with col1:
            # RSI
            st.metric("RSI (14)", 
                     f"{indicators['oscillators']['rsi']['value']:.2f}", 
                     delta=indicators['oscillators']['rsi']['trend'])
            
            # Stochastic
            st.metric("Stochastic K", 
                     f"{indicators['oscillators']['stochastic']['k']:.2f}", 
                     delta=indicators['oscillators']['stochastic']['trend'])
            
        with col2:
            # MACD
            st.metric("MACD Line", 
                     f"{indicators['oscillators']['macd']['line']:.2f}", 
                     delta=indicators['oscillators']['macd']['trend'])
            
            # MACD Signal
            st.metric("MACD Signal", 
                     f"{indicators['oscillators']['macd']['signal']:.2f}", 
                     delta=indicators['oscillators']['macd']['histogram'])
        
        # Display Support and Resistance
        st.markdown("##### Support & Resistance Levels")
        levels_df = pd.DataFrame({
            "Type": ["Support 1", "Support 2", "Resistance 1", "Resistance 2"],
            "Price Level": [
                indicators["support_resistance"]["support"][0],
                indicators["support_resistance"]["support"][1],
                indicators["support_resistance"]["resistance"][0],
                indicators["support_resistance"]["resistance"][1]
            ],
            "Strength": [
                "Strong", "Moderate", "Strong", "Moderate"
            ]
        })
        st.dataframe(levels_df)
        
    with tab3:
        st.subheader("Trading Suggestion")
        trading_suggestion = results["trading_suggestion"]
        
        # Display suggestion box with appropriate color
        suggestion_color = "green" if "buy" in trading_suggestion["action"].lower() else "red" if "sell" in trading_suggestion["action"].lower() else "blue"
        st.markdown(f"""
        <div style='background-color: rgba(0, 0, 0, 0.1); padding: 20px; border-radius: 10px; border-left: 5px solid {suggestion_color};'>
            <h4>{trading_suggestion['action']}</h4>
            <p>{trading_suggestion['rationale']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key levels
        st.markdown("##### Key Levels to Watch")
        st.markdown(f"**Entry**: {trading_suggestion['entry_point']}")
        st.markdown(f"**Stop Loss**: {trading_suggestion['stop_loss']}")
        st.markdown(f"**Take Profit**: {trading_suggestion['take_profit']}")
        
        # Display risk-reward ratio
        risk = abs(float(trading_suggestion['entry_point']) - float(trading_suggestion['stop_loss']))
        reward = abs(float(trading_suggestion['take_profit']) - float(trading_suggestion['entry_point']))
        risk_reward = reward / risk if risk > 0 else 0
        
        st.markdown(f"**Risk-Reward Ratio**: {risk_reward:.2f}")

# Financial disclaimer (always shown)
st.markdown("---")
st.markdown("""
<div style='background-color: rgba(255, 255, 0, 0.1); padding: 10px; border-radius: 5px;'>
    <strong>Disclaimer:</strong> This is not financial advice. Always do your own research before making any trading decisions.
</div>
""", unsafe_allow_html=True)
