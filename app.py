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
    page_title="Crypto Sant AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner, more modern UI
st.markdown("""
<style>
    /* Global styles */
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    body {
        background-color: #0a1929;
        color: #ffffff;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #8b9eff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Main header */
    .main-header {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #8b9eff, #c49bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
        line-height: 1.2;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #ffffff;
        opacity: 0.8;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        color: #8b9eff;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2d3747;
    }
    
    /* Cards and containers */
    .modern-card {
        background-color: #121f33;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
        border: 1px solid #2d3747;
    }
    .upload-section {
        border: 2px dashed #6c79ff;
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        margin: 1rem 0 2rem 0;
        background-color: rgba(108, 121, 255, 0.05);
        transition: all 0.3s ease;
    }
    .upload-section:hover {
        background-color: rgba(108, 121, 255, 0.08);
        transform: translateY(-5px);
    }
    
    /* Button styling */
    .modern-button {
        background: linear-gradient(90deg, #6c79ff, #9b5de5);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        text-align: center;
        transition: all 0.3s;
        box-shadow: 0 4px 10px rgba(108, 121, 255, 0.3);
        display: inline-block;
        margin: 1rem auto;
        width: auto;
    }
    .modern-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 7px 15px rgba(108, 121, 255, 0.4);
    }
    
    /* Analysis result styles */
    .tab-content {
        padding: 1.5rem;
        background-color: #121f33;
        border-radius: 0 0 15px 15px;
        margin-top: -16px;
        border: 1px solid #2d3747;
        border-top: none;
    }
    .pattern-card {
        background-color: #1a2942;
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: 1px solid #2d3747;
        transition: transform 0.2s;
    }
    .pattern-card:hover {
        transform: translateY(-3px);
    }
    .metric-card {
        background-color: #1a2942;
        padding: 1.2rem;
        border-radius: 15px;
        border: 1px solid #2d3747;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* Indicator badges */
    .time-badge {
        background-color: rgba(108, 121, 255, 0.2);
        color: #8b9eff;
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin-left: 1rem;
    }
    
    /* Disclaimer */
    .disclaimer {
        background-color: rgba(108, 121, 255, 0.07);
        padding: 1rem;
        border-radius: 12px;
        margin-top: 2rem;
        text-align: center;
        font-style: italic;
        color: #ffffff;
        opacity: 0.7;
        border: 1px solid rgba(108, 121, 255, 0.2);
        font-size: 0.9rem;
    }
    
    /* Footer section */
    .footer-section {
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #2d3747;
        text-align: center;
        font-size: 0.9rem;
        opacity: 0.7;
    }
    .how-it-works {
        display: flex;
        justify-content: center;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    .step-item {
        display: flex;
        align-items: center;
        margin: 0 1rem;
        padding: 0.5rem 1rem;
        background-color: rgba(108, 121, 255, 0.07);
        border-radius: 50px;
        margin-bottom: 0.5rem;
    }
    .step-number {
        background: linear-gradient(90deg, #6c79ff, #9b5de5);
        color: white;
        width: 25px;
        height: 25px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        margin-right: 0.8rem;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    /* Streamlit element modifications */
    .css-1kyxreq {
        justify-content: center !important;
    }
    [data-testid="stSidebar"] {
        background-color: #0a1929;
        border-right: 1px solid #2d3747;
    }
    [data-testid="stSidebar"] .css-1d391kg {
        background-color: #121f33;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6c79ff, #9b5de5);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #121f33;
        border-radius: 15px 15px 0 0;
        border: 1px solid #2d3747;
        border-bottom: none;
        color: #ffffff;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #1a2942, #121f33);
        color: #8b9eff;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar 
with st.sidebar:
    st.markdown("<h3 style='text-align: center; color: #8b9eff;'>Chart Settings</h3>", unsafe_allow_html=True)
    
    # Check if OpenAI API key is already set
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        st.markdown("<p style='font-weight: 500; margin-top: 1rem;'>OpenAI API Key</p>", unsafe_allow_html=True)
        api_key_input = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key for AI-powered suggestions", key="openai_api_key")
        
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            st.success("✅ API key set! AI-powered suggestions are now enabled.")
    else:
        st.markdown("<p style='color: #03DAC6; font-weight: 500; margin-top: 1rem;'>✅ OpenAI API key is set</p>", unsafe_allow_html=True)
        if st.button("Clear API Key"):
            os.environ["OPENAI_API_KEY"] = ""
            st.rerun()
    
    st.markdown("<hr style='margin: 1.5rem 0; border-color: #2d3747;'>", unsafe_allow_html=True)
    
    # Timeframe selection with improved UI
    st.markdown("<p style='font-weight: 500;'>Select Timeframe</p>", unsafe_allow_html=True)
    timeframe = st.selectbox(
        "Timeframe",
        options=["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W"],
        index=2,
        label_visibility="collapsed"
    )
    
    # Explanation of timeframes
    with st.expander("About Timeframes"):
        st.markdown("""
        - **1m/5m/15m/30m**: Short-term trading
        - **1h/4h**: Intraday trading
        - **1D/1W**: Swing/position trading
        
        The AI adjusts its analysis based on the selected timeframe.
        """)
    
    # Additional info
    st.markdown("<hr style='margin: 1.5rem 0; border-color: #2d3747;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-weight: 500;'>Analysis Features</p>", unsafe_allow_html=True)
    
    with st.expander("Pattern Recognition"):
        st.markdown("""
        Detects common patterns like:
        - Head and Shoulders
        - Double Top/Bottom
        - Triangle patterns
        - Trend lines
        """)
    
    with st.expander("Technical Indicators"):
        st.markdown("""
        Analyzes multiple indicators:
        - Moving Averages (SMA, EMA)
        - Oscillators (RSI, MACD, Stochastic)
        - Support/Resistance levels
        """)

# Initialize session state if not exist
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
    
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Main container for centered content
with st.container():
    # Main header
    st.markdown("<h1 class='main-header'>Crypto Sant AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Stock Chart Analyzer</p>", unsafe_allow_html=True)
    
    # Upload section with improved styling - at the top
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Chart Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded_file is None:
        st.markdown("""
        <p style="color: #ffffff; opacity: 0.7;">Drag and drop your chart image here, or click to browse</p>
        <p style="color: #ffffff; opacity: 0.5; font-size: 0.9rem;">Supported formats: JPG, JPEG, PNG</p>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Process uploaded image with enhanced UI
if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)
    
    # Analyze button with improved styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.markdown("<button class='modern-button'>Analyze Chart</button>", unsafe_allow_html=True)
        # Fixed: Removed label_visibility parameter from button
        analyze_clicked = st.button("Analyze Chart", key="analyze_button", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    if analyze_clicked:
        with st.spinner("Analyzing chart... This may take a moment."):
            # Check for OpenAI API key and show a friendly message if not available
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if not api_key:
                st.info("**Note:** OpenAI API key not found. Using rule-based analysis instead of AI-powered suggestions. For enhanced results, please provide an OpenAI API key.")
            
            # Perform analysis
            try:
                analysis_results = analyze_chart(np.array(image), timeframe)
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

# Display results if analysis is complete with enhanced styling
if st.session_state.analysis_complete and st.session_state.analysis_results is not None:
    results = st.session_state.analysis_results
    
    st.markdown("<div class='section-header'>Analysis Results</div>", unsafe_allow_html=True)
    
    # Display timeframe with badge
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <h3 style="margin: 0; padding: 0;">Chart Analysis</h3>
        <div class="time-badge">{timeframe} Timeframe</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different result sections with enhanced styling
    tab1, tab2, tab3 = st.tabs(["📊 Patterns", "📈 Indicators", "💡 Trading Suggestion"])
    
    with tab1:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.markdown("<h4>Detected Patterns</h4>", unsafe_allow_html=True)
        
        if results["patterns"]:
            for pattern in results["patterns"]:
                st.markdown(f"""
                <div class="pattern-card">
                    <h5 style="color: #8b9eff;">{pattern['name']}</h5>
                    <p>{pattern['description']}</p>
                    <div style="margin: 0.5rem 0;">
                """, unsafe_allow_html=True)
                
                # Progress bar for confidence
                st.progress(pattern['confidence'])
                
                # Color coding for confidence
                conf_color = "#03DAC6" if pattern['confidence'] > 0.7 else "#FFB740" if pattern['confidence'] > 0.5 else "#FF4F5E"
                
                st.markdown(f"""
                    <p style="text-align: right; color: {conf_color}; font-weight: 500;">
                        Confidence: {pattern['confidence']:.2f}
                    </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant patterns detected in this chart.")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        indicators = results["indicators"]
        
        # Moving Averages section
        st.markdown("<h4>Moving Averages</h4>", unsafe_allow_html=True)
        
        # Create a cleaner display for moving averages
        ma_cols = st.columns(5)
        mas = [
            {"name": "SMA 20", "value": indicators['moving_averages']['sma_20']['value'], "trend": indicators['moving_averages']['sma_20']['trend']},
            {"name": "SMA 50", "value": indicators['moving_averages']['sma_50']['value'], "trend": indicators['moving_averages']['sma_50']['trend']},
            {"name": "SMA 200", "value": indicators['moving_averages']['sma_200']['value'], "trend": indicators['moving_averages']['sma_200']['trend']},
            {"name": "EMA 12", "value": indicators['moving_averages']['ema_12']['value'], "trend": indicators['moving_averages']['ema_12']['trend']},
            {"name": "EMA 26", "value": indicators['moving_averages']['ema_26']['value'], "trend": indicators['moving_averages']['ema_26']['trend']}
        ]
        
        for i, col in enumerate(ma_cols):
            with col:
                trend_color = "#03DAC6" if mas[i]["trend"] == "Bullish" else "#FF4F5E" if mas[i]["trend"] == "Bearish" else "#ffffff"
                st.markdown(f"""
                <div style="text-align: center; padding: 0.8rem; border-radius: 12px; border: 1px solid #2d3747; background-color: #1a2942;">
                    <h5 style="margin: 0; font-size: 1rem;">{mas[i]["name"]}</h5>
                    <p style="font-size: 1.2rem; font-weight: 600; margin: 0.3rem 0;">{mas[i]["value"]:.2f}</p>
                    <p style="margin: 0; color: {trend_color};">{mas[i]["trend"]}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Oscillators section
        st.markdown("<h4 style='margin-top: 1.5rem;'>Oscillators</h4>", unsafe_allow_html=True)
        
        # Create three columns for oscillators
        osc_cols = st.columns(3)
        
        # RSI
        with osc_cols[0]:
            rsi_color = "#FF4F5E" if indicators['oscillators']['rsi']['trend'] == "Overbought" else "#03DAC6" if indicators['oscillators']['rsi']['trend'] == "Oversold" else "#ffffff"
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: #8b9eff;">RSI (14)</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">{indicators['oscillators']['rsi']['value']:.2f}</p>
                <p style="margin: 0; color: {rsi_color};">{indicators['oscillators']['rsi']['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # MACD
        with osc_cols[1]:
            macd_color = "#03DAC6" if indicators['oscillators']['macd']['trend'] == "Bullish" else "#FF4F5E" if indicators['oscillators']['macd']['trend'] == "Bearish" else "#ffffff"
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: #8b9eff;">MACD</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">{indicators['oscillators']['macd']['line']:.2f}</p>
                <p style="margin: 0; color: {macd_color};">{indicators['oscillators']['macd']['trend']}</p>
                <p style="margin: 0; font-size: 0.8rem; opacity: 0.7;">Signal: {indicators['oscillators']['macd']['signal']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Stochastic
        with osc_cols[2]:
            stoch_color = "#FF4F5E" if indicators['oscillators']['stochastic']['trend'] == "Overbought" else "#03DAC6" if indicators['oscillators']['stochastic']['trend'] == "Oversold" else "#ffffff"
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: #8b9eff;">Stochastic</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">{indicators['oscillators']['stochastic']['k']:.2f}</p>
                <p style="margin: 0; color: {stoch_color};">{indicators['oscillators']['stochastic']['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Support and Resistance levels
        st.markdown("<h4 style='margin-top: 1.5rem;'>Support & Resistance</h4>", unsafe_allow_html=True)
        
        # Create two columns for support and resistance
        sr_cols = st.columns(2)
        
        # Support levels
        with sr_cols[0]:
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 12px; border: 1px solid rgba(3, 218, 198, 0.3); background-color: rgba(3, 218, 198, 0.05);">
                <h5 style="margin: 0; color: #03DAC6;">Support Levels</h5>
                <p style="font-size: 1.2rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">S1: {indicators['support_resistance']['support'][0]}</p>
                <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #ffffff; opacity: 0.8;">S2: {indicators['support_resistance']['support'][1]}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Resistance levels
        with sr_cols[1]:
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 12px; border: 1px solid rgba(255, 79, 94, 0.3); background-color: rgba(255, 79, 94, 0.05);">
                <h5 style="margin: 0; color: #FF4F5E;">Resistance Levels</h5>
                <p style="font-size: 1.2rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">R1: {indicators['support_resistance']['resistance'][0]}</p>
                <p style="font-size: 1.1rem; margin: 0.5rem 0; color: #ffffff; opacity: 0.8;">R2: {indicators['support_resistance']['resistance'][1]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        trading_suggestion = results["trading_suggestion"]
        
        # Determine color based on action
        if "buy" in trading_suggestion["action"].lower() or "bullish" in trading_suggestion["action"].lower():
            suggestion_color = "#03DAC6"  # Green
            icon = "📈"
        elif "sell" in trading_suggestion["action"].lower() or "bearish" in trading_suggestion["action"].lower():
            suggestion_color = "#FF4F5E"  # Red
            icon = "📉"
        else:
            suggestion_color = "#8b9eff"  # Blue
            icon = "📊"
        
        # Get strength value if available, or default to 75
        signal_strength = trading_suggestion.get('strength', 75)
        
        # Display suggestion with enhanced styling and strength meter
        st.markdown(f"""
        <div style="background-color: {suggestion_color}; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: white; margin: 0; display: flex; align-items: center;">
                    <span style="font-size: 2rem; margin-right: 1rem;">{icon}</span>
                    {trading_suggestion['action']}
                </h3>
                <div style="background-color: rgba(255,255,255,0.2); border-radius: 50px; padding: 0.5rem 1rem; display: flex; align-items: center;">
                    <div style="width: 10px; height: 10px; background-color: white; border-radius: 50%; margin-right: 8px;"></div>
                    <span style="color: white; font-weight: bold;">{signal_strength}% Strength</span>
                </div>
            </div>
        </div>
        <div style="background-color: #1a2942; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem; border: 1px solid #2d3747;">
            <p style="font-size: 1.1rem; line-height: 1.6; color: #ffffff;">{trading_suggestion['rationale']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key levels with enhanced styling
        st.markdown("<h4>Key Trading Levels</h4>", unsafe_allow_html=True)
        
        # Create three columns for key levels
        key_cols = st.columns(3)
        
        with key_cols[0]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #8b9eff;">
                <h5 style="margin: 0; color: #8b9eff;">Entry Point</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">{trading_suggestion['entry_point']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with key_cols[1]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #FF4F5E;">
                <h5 style="margin: 0; color: #FF4F5E;">Stop Loss</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">{trading_suggestion['stop_loss']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with key_cols[2]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #03DAC6;">
                <h5 style="margin: 0; color: #03DAC6;">Take Profit</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: #ffffff;">{trading_suggestion['take_profit']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Calculate and display risk-reward ratio
        risk = abs(float(trading_suggestion['entry_point']) - float(trading_suggestion['stop_loss']))
        reward = abs(float(trading_suggestion['take_profit']) - float(trading_suggestion['entry_point']))
        risk_reward = reward / risk if risk > 0 else 0
        
        # Color coding for risk-reward
        rr_color = "#03DAC6" if risk_reward >= 2 else "#FFB740" if risk_reward >= 1 else "#FF4F5E"
        
        st.markdown(f"""
        <div style="margin-top: 1.5rem; background-color: #1a2942; padding: 1.2rem; border-radius: 12px; border: 1px solid #2d3747;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: #8b9eff;">Risk-Reward Ratio</h5>
                <p style="font-size: 1.2rem; font-weight: 600; color: {rr_color}; margin: 0;">1:{risk_reward:.2f}</p>
            </div>
            <div style="height: 6px; background-color: #2d3747; margin-top: 0.8rem; border-radius: 3px;">
                <div style="height: 100%; width: {min(risk_reward * 50, 100)}%; background-color: {rr_color}; border-radius: 3px;"></div>
            </div>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #ffffff; opacity: 0.8;">
                {
                "Excellent risk-reward ratio. The potential reward significantly outweighs the risk." if risk_reward >= 2 else
                "Acceptable risk-reward ratio. The potential reward outweighs the risk." if risk_reward >= 1 else
                "Poor risk-reward ratio. Consider adjusting your entry, stop loss, or take profit levels."
                }
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# MOVED: "How it Works" section to the bottom as a much smaller section
st.markdown("<div class='footer-section'>", unsafe_allow_html=True)

# How it Works - simplified and smaller
st.markdown("<h5 style='text-align: center; margin-bottom: 0.5rem;'>How it Works</h5>", unsafe_allow_html=True)
st.markdown("""
<div class="how-it-works">
    <div class="step-item"><div class="step-number">1</div>Upload chart</div>
    <div class="step-item"><div class="step-number">2</div>Select timeframe</div>
    <div class="step-item"><div class="step-number">3</div>Analyze</div>
    <div class="step-item"><div class="step-number">4</div>Review patterns</div>
    <div class="step-item"><div class="step-number">5</div>Get suggestions</div>
</div>
""", unsafe_allow_html=True)

# Financial disclaimer with enhanced styling
st.markdown("<div class='disclaimer'>", unsafe_allow_html=True)
st.markdown("""
<strong>Disclaimer:</strong> This is not financial advice. Always do your own research before making any trading decisions.
The AI analysis is based on technical indicators and pattern recognition only.
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
