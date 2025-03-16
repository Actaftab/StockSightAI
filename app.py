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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        color: #0D47A1;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #f0f0f0;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.7rem;
        background-color: #f9f9f9;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .upload-section {
        border: 2px dashed #1E88E5;
        border-radius: 0.7rem;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .info-text {
        color: #333;
        font-size: 1rem;
        line-height: 1.5;
    }
    .highlight {
        background-color: #E3F2FD;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: 500;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
    }
    .tab-content {
        padding: 1rem;
    }
    .pattern-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .disclaimer {
        background-color: rgba(255, 255, 0, 0.1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 2rem;
        text-align: center;
        font-style: italic;
    }
    .time-badge {
        background-color: #E3F2FD;
        color: #0D47A1;
        padding: 0.3rem 0.7rem;
        border-radius: 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin-left: 1rem;
    }
    .analyze-button {
        background-color: #1E88E5;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 600;
        cursor: pointer;
        text-align: center;
        width: 100%;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">AI Stock Chart Analyzer</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="info-text card">
    <p>Welcome to the AI Stock Chart Analyzer! This tool uses advanced computer vision and artificial intelligence to analyze stock chart images and provide trading insights.</p>
    <p>Simply upload a stock chart image, select the timeframe, and let the AI do the work! The tool will identify patterns, calculate technical indicators, and provide trading suggestions based on the analysis.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown('<h3 style="text-align: center; color: #0D47A1;">Chart Settings</h3>', unsafe_allow_html=True)
    
    # Timeframe selection with improved UI
    st.markdown('<p style="font-weight: 500;">Select Timeframe</p>', unsafe_allow_html=True)
    timeframe = st.selectbox(
        "",
        options=["1m", "5m", "15m", "30m", "1h", "4h", "1D", "1W"],
        index=2
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
    st.markdown('<hr style="margin: 1.5rem 0">', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-weight: 500;">About the Analysis</p>', unsafe_allow_html=True)
    
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

# Main content area
col1, col2 = st.columns([3, 1])

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-weight: 500;">How it Works</p>', unsafe_allow_html=True)
    st.markdown("""
    1. Upload your chart image
    2. Select the timeframe
    3. Click "Analyze Chart"
    4. Review the AI's analysis
    5. Check trading suggestions
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state if not exist
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
    
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Upload section with improved styling
with col1:
    st.markdown('<h2 class="sub-header">Upload Stock Chart</h2>', unsafe_allow_html=True)
    
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is None:
        st.markdown("""
        <p style="color: #666;">Drag and drop your chart image here, or click to browse</p>
        <p style="color: #999; font-size: 0.9rem;">Supported formats: JPG, JPEG, PNG</p>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Process uploaded image with enhanced UI
if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)
    
    # Convert to OpenCV format
    image_array = np.array(image)
    
    # Analyze button with improved styling
    st.markdown(f'<div class="analyze-button">', unsafe_allow_html=True)
    analyze_clicked = st.button("Analyze Chart", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if analyze_clicked:
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

# Display results if analysis is complete with enhanced styling
if st.session_state.analysis_complete and st.session_state.analysis_results is not None:
    results = st.session_state.analysis_results
    
    st.markdown('<h2 class="sub-header">Analysis Results</h2>', unsafe_allow_html=True)
    
    # Display timeframe with badge
    st.markdown(f"""
    <div style="display: flex; align-items: center;">
        <h3>Chart Analysis</h3>
        <div class="time-badge">{timeframe} Timeframe</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different result sections with enhanced styling
    tab1, tab2, tab3 = st.tabs(["📊 Patterns & Trends", "📈 Technical Indicators", "💡 Trading Suggestion"])
    
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown('<h4>Detected Patterns</h4>', unsafe_allow_html=True)
        
        if results["patterns"]:
            for pattern in results["patterns"]:
                st.markdown(f"""
                <div class="pattern-card">
                    <h5>{pattern['name']}</h5>
                    <p>{pattern['description']}</p>
                    <div style="margin: 0.5rem 0;">
                """, unsafe_allow_html=True)
                
                # Progress bar for confidence
                st.progress(pattern['confidence'])
                
                # Color coding for confidence
                conf_color = "#4CAF50" if pattern['confidence'] > 0.7 else "#FF9800" if pattern['confidence'] > 0.5 else "#F44336"
                
                st.markdown(f"""
                    <p style="text-align: right; color: {conf_color}; font-weight: 500;">
                        Confidence: {pattern['confidence']:.2f}
                    </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant patterns detected in this chart.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        indicators = results["indicators"]
        
        # Moving Averages section with enhanced styling
        st.markdown('<h4>Moving Averages</h4>', unsafe_allow_html=True)
        ma_df = pd.DataFrame({
            "Type": ["SMA 20", "SMA 50", "SMA 200", "EMA 12", "EMA 26"],
            "Value": [
                f"{indicators['moving_averages']['sma_20']['value']:.2f}",
                f"{indicators['moving_averages']['sma_50']['value']:.2f}",
                f"{indicators['moving_averages']['sma_200']['value']:.2f}",
                f"{indicators['moving_averages']['ema_12']['value']:.2f}",
                f"{indicators['moving_averages']['ema_26']['value']:.2f}"
            ],
            "Trend": [
                indicators["moving_averages"]["sma_20"]["trend"],
                indicators["moving_averages"]["sma_50"]["trend"],
                indicators["moving_averages"]["sma_200"]["trend"],
                indicators["moving_averages"]["ema_12"]["trend"],
                indicators["moving_averages"]["ema_26"]["trend"]
            ]
        })
        
        # Display styled dataframe (simple version as dataframe styling requires more complex code)
        st.dataframe(ma_df, use_container_width=True)
        
        # Oscillators section with enhanced styling using metrics and cards
        st.markdown('<h4>Oscillators</h4>', unsafe_allow_html=True)
        
        # Create three columns for oscillators
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "RSI (14)", 
                f"{indicators['oscillators']['rsi']['value']:.2f}", 
                delta=indicators['oscillators']['rsi']['trend']
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "MACD Line", 
                f"{indicators['oscillators']['macd']['line']:.2f}", 
                delta=indicators['oscillators']['macd']['trend']
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Stochastic K", 
                f"{indicators['oscillators']['stochastic']['k']:.2f}", 
                delta=indicators['oscillators']['stochastic']['trend']
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Support and Resistance levels with enhanced styling
        st.markdown('<h4>Support & Resistance Levels</h4>', unsafe_allow_html=True)
        
        # Create a visual representation of support/resistance
        levels_df = pd.DataFrame({
            "Type": ["Support 1", "Support 2", "Resistance 1", "Resistance 2"],
            "Price Level": [
                indicators["support_resistance"]["support"][0],
                indicators["support_resistance"]["support"][1],
                indicators["support_resistance"]["resistance"][0],
                indicators["support_resistance"]["resistance"][1]
            ],
            "Strength": ["Strong", "Moderate", "Strong", "Moderate"]
        })
        
        st.dataframe(levels_df, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        trading_suggestion = results["trading_suggestion"]
        
        # Determine color based on action
        if "buy" in trading_suggestion["action"].lower() or "bullish" in trading_suggestion["action"].lower():
            suggestion_color = "#4CAF50"  # Green
            icon = "📈"
        elif "sell" in trading_suggestion["action"].lower() or "bearish" in trading_suggestion["action"].lower():
            suggestion_color = "#F44336"  # Red
            icon = "📉"
        else:
            suggestion_color = "#2196F3"  # Blue
            icon = "📊"
        
        # Display suggestion with enhanced styling
        st.markdown(f"""
        <div style="background-color: {suggestion_color}; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem;">
            <h4 style="color: white; margin: 0; display: flex; align-items: center;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>
                {trading_suggestion['action']}
            </h4>
        </div>
        <div style="background-color: white; padding: 1.5rem; border-radius: 0.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;">
            <p style="font-size: 1.1rem; line-height: 1.6;">{trading_suggestion['rationale']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key levels with enhanced styling
        st.markdown('<h4>Key Trading Levels</h4>', unsafe_allow_html=True)
        
        # Create three columns for key levels
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #2196F3;">
                <h5 style="margin: 0; color: #2196F3;">Entry Point</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0;">{trading_suggestion['entry_point']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #F44336;">
                <h5 style="margin: 0; color: #F44336;">Stop Loss</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0;">{trading_suggestion['stop_loss']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #4CAF50;">
                <h5 style="margin: 0; color: #4CAF50;">Take Profit</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0;">{trading_suggestion['take_profit']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Calculate and display risk-reward ratio
        risk = abs(float(trading_suggestion['entry_point']) - float(trading_suggestion['stop_loss']))
        reward = abs(float(trading_suggestion['take_profit']) - float(trading_suggestion['entry_point']))
        risk_reward = reward / risk if risk > 0 else 0
        
        st.markdown(f"""
        <div style="margin-top: 1.5rem;">
            <h5>Risk-Reward Ratio: {risk_reward:.2f}</h5>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Financial disclaimer with enhanced styling
st.markdown('<div class="disclaimer">', unsafe_allow_html=True)
st.markdown("""
<strong>Disclaimer:</strong> This is not financial advice. Always do your own research before making any trading decisions.
The AI analysis is based on technical indicators and pattern recognition only, and does not consider fundamental factors or market news.
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
