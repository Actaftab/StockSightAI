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

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

# Page configuration
st.set_page_config(
    page_title="Crypto Sant AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define dark/light mode colors based on current theme
if st.session_state.theme == "dark":
    bg_color = "#121212"
    text_color = "#E0E0E0"
    card_bg = "#1E1E1E"
    accent_color = "#BB86FC"
    secondary_accent = "#03DAC5"
    header_color = "#BB86FC"
    border_color = "#333333"
else:  # light theme
    bg_color = "#FFFFFF"
    text_color = "#333333"
    card_bg = "#F8F9FA"
    accent_color = "#6200EE"
    secondary_accent = "#03DAC6"
    header_color = "#6200EE"
    border_color = "#E0E0E0"

# Custom CSS with dynamic theme colors
st.markdown(f"""
<style>
    /* Global styles */
    .reportview-container .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {header_color};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .main-header {{
        font-size: 2.8rem;
        font-weight: 700;
        color: {header_color};
        margin-bottom: 0.2rem;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .sub-header {{
        font-size: 1.2rem;
        color: {text_color};
        opacity: 0.8;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }}
    .section-header {{
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 2rem;
        color: {header_color};
        padding-bottom: 0.5rem;
        border-bottom: 1px solid {border_color};
    }}
    
    /* Cards and containers */
    .clean-card {{
        background-color: {card_bg};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid {border_color};
    }}
    .upload-section {{
        border: 2px dashed {accent_color};
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0 2rem 0;
        background-color: {card_bg};
    }}
    
    /* Text styles */
    .info-text {{
        color: {text_color};
        font-size: 1rem;
        line-height: 1.5;
    }}
    .muted-text {{
        color: {text_color};
        opacity: 0.7;
        font-size: 0.9rem;
    }}
    
    /* UI elements */
    .theme-toggle {{
        position: absolute;
        top: 1.2rem;
        right: 1rem;
        z-index: 999;
    }}
    .accent-button {{
        background-color: {accent_color};
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        cursor: pointer;
        text-align: center;
        transition: all 0.3s;
        width: 100%;
        margin-top: 1rem;
    }}
    .accent-button:hover {{
        opacity: 0.9;
        transform: translateY(-2px);
    }}
    .time-badge {{
        background-color: {accent_color}30;
        color: {accent_color};
        padding: 0.3rem 0.7rem;
        border-radius: 1rem;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        margin-left: 1rem;
    }}
    
    /* Analysis result styles */
    .tab-content {{
        padding: 1.5rem;
        background-color: {card_bg};
        border-radius: 0 0 8px 8px;
        margin-top: -16px;
        border: 1px solid {border_color};
        border-top: none;
    }}
    .pattern-card {{
        background-color: {card_bg};
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid {border_color};
    }}
    .metric-card {{
        background-color: {card_bg};
        padding: 1.2rem;
        border-radius: 8px;
        border: 1px solid {border_color};
        transition: transform 0.3s;
    }}
    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }}
    
    /* Disclaimer */
    .disclaimer {{
        background-color: {accent_color}10;
        padding: 1rem;
        border-radius: 8px;
        margin-top: 2rem;
        text-align: center;
        font-style: italic;
        color: {text_color};
        border: 1px solid {accent_color}30;
    }}
    
    /* Table styles */
    .how-it-works-table {{
        width: 100%;
        border-collapse: collapse;
    }}
    .how-it-works-table td {{
        padding: 12px 15px;
        text-align: left;
        border: 1px solid {border_color};
    }}
    .how-it-works-table tr:nth-child(even) {{
        background-color: {card_bg};
    }}
    .how-it-works-table tr:nth-child(odd) {{
        background-color: {bg_color};
    }}
    .how-it-works-table .step-number {{
        font-size: 1.2rem;
        font-weight: bold;
        color: {accent_color};
        width: 40px;
        text-align: center;
    }}
    
    /* Footer section */
    .footer-section {{
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid {border_color};
    }}
    
    /* Fix Streamlit components */
    .css-1kyxreq {{
        justify-content: center !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {card_bg};
    }}
    .stProgress > div > div > div > div {{
        background-color: {accent_color};
    }}
</style>
""", unsafe_allow_html=True)

# Sidebar 
with st.sidebar:
    st.markdown(f"<h3 style='text-align: center; color: {header_color};'>Chart Settings</h3>", unsafe_allow_html=True)
    
    # Theme toggle button in sidebar
    if st.button("🌓 " + ("Light Mode" if st.session_state.theme == "dark" else "Dark Mode")):
        # Toggle theme
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()
    
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
    st.markdown(f"<hr style='margin: 1.5rem 0; border-color: {border_color}'>", unsafe_allow_html=True)
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

# Main header
st.markdown("<h1 class='main-header'>Crypto Sant AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Stock Chart Analyzer</p>", unsafe_allow_html=True)

# Initialize session state if not exist
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
    
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

# Upload section with improved styling - MOVED TO TOP
st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Chart Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

if uploaded_file is None:
    st.markdown(f"""
    <p style="color: {text_color}; opacity: 0.7;">Drag and drop your chart image here, or click to browse</p>
    <p style="color: {text_color}; opacity: 0.5; font-size: 0.9rem;">Supported formats: JPG, JPEG, PNG</p>
    """, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# Process uploaded image with enhanced UI
if uploaded_file is not None:
    # Display uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Chart", use_container_width=True)
    
    # Convert to OpenCV format
    image_array = np.array(image)
    
    # Analyze button with improved styling
    st.markdown("<div class='accent-button'>", unsafe_allow_html=True)
    analyze_clicked = st.button("Analyze Chart", use_container_width=True, key="analyze_button")
    st.markdown("</div>", unsafe_allow_html=True)
    
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
                    <h5 style="color: {header_color};">{pattern['name']}</h5>
                    <p>{pattern['description']}</p>
                    <div style="margin: 0.5rem 0;">
                """, unsafe_allow_html=True)
                
                # Progress bar for confidence
                st.progress(pattern['confidence'])
                
                # Color coding for confidence
                conf_color = secondary_accent if pattern['confidence'] > 0.7 else "#FF9800" if pattern['confidence'] > 0.5 else "#F44336"
                
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
        
        # Moving Averages section with enhanced styling
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
                trend_color = secondary_accent if mas[i]["trend"] == "Bullish" else "#F44336" if mas[i]["trend"] == "Bearish" else text_color
                st.markdown(f"""
                <div style="text-align: center; padding: 0.8rem; border-radius: 8px; border: 1px solid {border_color};">
                    <h5 style="margin: 0; font-size: 1rem;">{mas[i]["name"]}</h5>
                    <p style="font-size: 1.2rem; font-weight: 600; margin: 0.3rem 0;">{mas[i]["value"]:.2f}</p>
                    <p style="margin: 0; color: {trend_color};">{mas[i]["trend"]}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Oscillators section with enhanced styling
        st.markdown("<h4 style='margin-top: 1.5rem;'>Oscillators</h4>", unsafe_allow_html=True)
        
        # Create three columns for oscillators
        osc_cols = st.columns(3)
        
        # RSI
        with osc_cols[0]:
            rsi_color = "#F44336" if indicators['oscillators']['rsi']['trend'] == "Overbought" else secondary_accent if indicators['oscillators']['rsi']['trend'] == "Oversold" else text_color
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: {header_color};">RSI (14)</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0;">{indicators['oscillators']['rsi']['value']:.2f}</p>
                <p style="margin: 0; color: {rsi_color};">{indicators['oscillators']['rsi']['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # MACD
        with osc_cols[1]:
            macd_color = secondary_accent if indicators['oscillators']['macd']['trend'] == "Bullish" else "#F44336" if indicators['oscillators']['macd']['trend'] == "Bearish" else text_color
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: {header_color};">MACD</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0;">{indicators['oscillators']['macd']['line']:.2f}</p>
                <p style="margin: 0; color: {macd_color};">{indicators['oscillators']['macd']['trend']}</p>
                <p style="margin: 0; font-size: 0.8rem;" class="muted-text">Signal: {indicators['oscillators']['macd']['signal']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Stochastic
        with osc_cols[2]:
            stoch_color = "#F44336" if indicators['oscillators']['stochastic']['trend'] == "Overbought" else secondary_accent if indicators['oscillators']['stochastic']['trend'] == "Oversold" else text_color
            st.markdown(f"""
            <div class="metric-card">
                <h5 style="margin: 0; color: {header_color};">Stochastic</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0;">{indicators['oscillators']['stochastic']['k']:.2f}</p>
                <p style="margin: 0; color: {stoch_color};">{indicators['oscillators']['stochastic']['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Support and Resistance levels with enhanced styling
        st.markdown("<h4 style='margin-top: 1.5rem;'>Support & Resistance</h4>", unsafe_allow_html=True)
        
        # Create two columns for support and resistance
        sr_cols = st.columns(2)
        
        # Support levels
        with sr_cols[0]:
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 8px; border: 1px solid {secondary_accent}30; background-color: {secondary_accent}10;">
                <h5 style="margin: 0; color: {secondary_accent};">Support Levels</h5>
                <p style="font-size: 1.2rem; font-weight: 600; margin: 0.5rem 0;">S1: {indicators['support_resistance']['support'][0]}</p>
                <p style="font-size: 1.1rem; margin: 0.5rem 0;">S2: {indicators['support_resistance']['support'][1]}</p>
            </div>
            """, unsafe_allow_html=True)
            
        # Resistance levels
        with sr_cols[1]:
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 8px; border: 1px solid #F4433630; background-color: #F4433610;">
                <h5 style="margin: 0; color: #F44336;">Resistance Levels</h5>
                <p style="font-size: 1.2rem; font-weight: 600; margin: 0.5rem 0;">R1: {indicators['support_resistance']['resistance'][0]}</p>
                <p style="font-size: 1.1rem; margin: 0.5rem 0;">R2: {indicators['support_resistance']['resistance'][1]}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tab3:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        trading_suggestion = results["trading_suggestion"]
        
        # Determine color based on action
        if "buy" in trading_suggestion["action"].lower() or "bullish" in trading_suggestion["action"].lower():
            suggestion_color = secondary_accent  # Green
            icon = "📈"
        elif "sell" in trading_suggestion["action"].lower() or "bearish" in trading_suggestion["action"].lower():
            suggestion_color = "#F44336"  # Red
            icon = "📉"
        else:
            suggestion_color = accent_color  # Primary accent
            icon = "📊"
        
        # Display suggestion with enhanced styling
        st.markdown(f"""
        <div style="background-color: {suggestion_color}; padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4 style="color: white; margin: 0; display: flex; align-items: center;">
                <span style="font-size: 1.5rem; margin-right: 0.8rem;">{icon}</span>
                {trading_suggestion['action']}
            </h4>
        </div>
        <div style="background-color: {card_bg}; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem; border: 1px solid {border_color};">
            <p style="font-size: 1.1rem; line-height: 1.6; color: {text_color};">{trading_suggestion['rationale']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display key levels with enhanced styling
        st.markdown("<h4>Key Trading Levels</h4>", unsafe_allow_html=True)
        
        # Create three columns for key levels
        key_cols = st.columns(3)
        
        with key_cols[0]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid {accent_color};">
                <h5 style="margin: 0; color: {accent_color};">Entry Point</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: {text_color};">{trading_suggestion['entry_point']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with key_cols[1]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid #F44336;">
                <h5 style="margin: 0; color: #F44336;">Stop Loss</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: {text_color};">{trading_suggestion['stop_loss']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with key_cols[2]:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 4px solid {secondary_accent};">
                <h5 style="margin: 0; color: {secondary_accent};">Take Profit</h5>
                <p style="font-size: 1.5rem; font-weight: 600; margin: 0.5rem 0; color: {text_color};">{trading_suggestion['take_profit']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Calculate and display risk-reward ratio
        risk = abs(float(trading_suggestion['entry_point']) - float(trading_suggestion['stop_loss']))
        reward = abs(float(trading_suggestion['take_profit']) - float(trading_suggestion['entry_point']))
        risk_reward = reward / risk if risk > 0 else 0
        
        # Color coding for risk-reward
        rr_color = secondary_accent if risk_reward >= 2 else "#FF9800" if risk_reward >= 1 else "#F44336"
        
        st.markdown(f"""
        <div style="margin-top: 1.5rem; background-color: {card_bg}; padding: 1.2rem; border-radius: 8px; border: 1px solid {border_color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h5 style="margin: 0; color: {header_color};">Risk-Reward Ratio</h5>
                <p style="font-size: 1.2rem; font-weight: 600; color: {rr_color}; margin: 0;">1:{risk_reward:.2f}</p>
            </div>
            <div style="height: 6px; background-color: {border_color}; margin-top: 0.8rem; border-radius: 3px;">
                <div style="height: 100%; width: {min(risk_reward * 50, 100)}%; background-color: {rr_color}; border-radius: 3px;"></div>
            </div>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: {text_color}; opacity: 0.8;">
                {
                "Excellent risk-reward ratio. The potential reward significantly outweighs the risk." if risk_reward >= 2 else
                "Acceptable risk-reward ratio. The potential reward outweighs the risk." if risk_reward >= 1 else
                "Poor risk-reward ratio. Consider adjusting your entry, stop loss, or take profit levels."
                }
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# MOVED: "How it Works" section to the bottom in a footer style
st.markdown("<div class='footer-section'>", unsafe_allow_html=True)

# Introduction info moved to the bottom
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("<h4>About Crypto Sant AI</h4>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Crypto Sant AI is your intelligent assistant for analyzing stock and crypto charts. Simply upload a chart image, and our AI will provide professional analysis and trading suggestions.</p>", unsafe_allow_html=True)

# How it Works table in a smaller format at the bottom
with col2:
    st.markdown("<h4>How it Works</h4>", unsafe_allow_html=True)
    st.markdown("""
    <table class='how-it-works-table'>
        <tr>
            <td class='step-number'>1</td>
            <td>Upload your chart image (from any trading platform)</td>
        </tr>
        <tr>
            <td class='step-number'>2</td>
            <td>Select the timeframe of your chart</td>
        </tr>
        <tr>
            <td class='step-number'>3</td>
            <td>Click "Analyze Chart" and wait a few seconds</td>
        </tr>
        <tr>
            <td class='step-number'>4</td>
            <td>Review detected patterns and technical indicators</td>
        </tr>
        <tr>
            <td class='step-number'>5</td>
            <td>Get AI-powered trading suggestions with entry/exit levels</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Financial disclaimer with enhanced styling
st.markdown("<div class='disclaimer'>", unsafe_allow_html=True)
st.markdown(f"""
<strong>Disclaimer:</strong> This is not financial advice. Always do your own research before making any trading decisions.
The AI analysis is based on technical indicators and pattern recognition only, and does not consider fundamental factors or market news.
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
