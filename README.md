# Crypto Sant AI - Stock Chart Analyzer

An AI-powered stock chart analysis tool leveraging machine learning to provide intelligent trading insights and technical indicator visualizations.

## Features

- **Pattern Recognition**: Automatically detects common chart patterns like head and shoulders, double tops/bottoms, triangles, and trend lines
- **Technical Indicators**: Analyzes multiple indicators including moving averages, oscillators (RSI, MACD, Stochastic), and support/resistance levels
- **AI-Powered Suggestions**: Generates trading suggestions with OpenAI integration (optional)
- **Fallback Mechanism**: Uses rule-based analysis when OpenAI API key is not available
- **Multi-Timeframe Analysis**: Adjusts analysis based on selected timeframe
- **Visual Presentation**: Clean, modern UI with intuitive visualization of analysis results
- **Direct Trading Recommendations**: Provides clear LONG/SHORT signals with strength indicators

## How to Use

1. Upload a stock chart image (JPG, JPEG, PNG)
2. Select the timeframe of the chart
3. Click "Analyze Chart" to process the image
4. Review the detected patterns, technical indicators, and trading suggestion
5. Optional: Add your OpenAI API key in the sidebar for enhanced AI-powered suggestions

## Tech Stack

- Streamlit for the web interface
- OpenCV and NumPy for image processing
- OpenAI for advanced trading suggestions
- Pandas and Plotly for data visualization

## Requirements

- Python 3.8+
- Streamlit
- OpenCV
- NumPy
- Pandas
- Plotly
- OpenAI (optional)

## Disclaimer

This tool is for educational and informational purposes only. The trading suggestions provided should not be considered as financial advice. Always do your own research before making any trading decisions.