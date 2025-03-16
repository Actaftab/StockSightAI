import os
from openai import OpenAI
import json

# Get API key from environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
openai = OpenAI(api_key=OPENAI_API_KEY)

def get_trading_suggestion(analysis_results, timeframe):
    """
    Generate a trading suggestion based on the analysis results
    
    Args:
        analysis_results (dict): The results of the chart analysis
        timeframe (str): The timeframe of the chart
        
    Returns:
        dict: A trading suggestion including action, rationale, and key levels
    """
    # Fall back to rule-based suggestions if OpenAI API key is not available
    if not OPENAI_API_KEY:
        return generate_rule_based_suggestion(analysis_results, timeframe)
    
    # Otherwise, use OpenAI to generate a more intelligent suggestion
    try:
        return generate_ai_suggestion(analysis_results, timeframe)
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return generate_rule_based_suggestion(analysis_results, timeframe)

def generate_ai_suggestion(analysis_results, timeframe):
    """
    Generate a trading suggestion using OpenAI
    
    Args:
        analysis_results (dict): The results of the chart analysis
        timeframe (str): The timeframe of the chart
        
    Returns:
        dict: A trading suggestion including action, rationale, and key levels
    """
    # Format the analysis results for the prompt
    patterns_text = ""
    for pattern in analysis_results["patterns"]:
        patterns_text += f"- {pattern['name']} (Confidence: {pattern['confidence']:.2f}): {pattern['description']}\n"
    
    indicators = analysis_results["indicators"]
    
    # Format moving averages
    ma_text = "Moving Averages:\n"
    for ma_name, ma_data in indicators["moving_averages"].items():
        ma_text += f"- {ma_name.upper()}: {ma_data['value']:.2f} ({ma_data['trend']})\n"
    
    # Format oscillators
    osc_text = "Oscillators:\n"
    osc_text += f"- RSI: {indicators['oscillators']['rsi']['value']:.2f} ({indicators['oscillators']['rsi']['trend']})\n"
    osc_text += f"- MACD Line: {indicators['oscillators']['macd']['line']:.2f}, Signal: {indicators['oscillators']['macd']['signal']:.2f} ({indicators['oscillators']['macd']['trend']})\n"
    osc_text += f"- Stochastic K: {indicators['oscillators']['stochastic']['k']:.2f} ({indicators['oscillators']['stochastic']['trend']})\n"
    
    # Format support/resistance
    sr_text = "Support and Resistance:\n"
    sr_text += f"- Support: {indicators['support_resistance']['support']}\n"
    sr_text += f"- Resistance: {indicators['support_resistance']['resistance']}\n"
    
    # Create the prompt for OpenAI
    prompt = f"""
    Analyze the following stock chart data and provide a trading suggestion for the {timeframe} timeframe:
    
    Detected Patterns:
    {patterns_text}
    
    Technical Indicators:
    {ma_text}
    {osc_text}
    {sr_text}
    
    Based on this analysis, provide a trading suggestion in JSON format with the following fields:
    1. action: A clear buy/sell/hold recommendation (e.g., "Strong Buy", "Weak Sell", "Hold", etc.)
    2. rationale: A brief explanation of the recommendation (2-3 sentences)
    3. entry_point: A suggested entry price
    4. stop_loss: A suggested stop loss price
    5. take_profit: A suggested take profit price
    
    Your suggestion should be fair, unbiased, and based solely on the technical analysis provided.
    """
    
    # Call the OpenAI API
    # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
    # do not change this unless explicitly requested by the user
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert technical analyst who provides unbiased trading suggestions based on chart analysis."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        max_tokens=500
    )
    
    try:
        suggestion = json.loads(response.choices[0].message.content)
        
        # Ensure all required fields are present
        required_fields = ["action", "rationale", "entry_point", "stop_loss", "take_profit"]
        for field in required_fields:
            if field not in suggestion:
                raise ValueError(f"Missing required field: {field}")
        
        return suggestion
    except Exception as e:
        print(f"Error parsing OpenAI response: {e}")
        # Fall back to rule-based suggestion if we can't parse the response
        return generate_rule_based_suggestion(analysis_results, timeframe)

def generate_rule_based_suggestion(analysis_results, timeframe):
    """
    Generate a trading suggestion based on simple rules
    
    Args:
        analysis_results (dict): The results of the chart analysis
        timeframe (str): The timeframe of the chart
        
    Returns:
        dict: A trading suggestion including action, rationale, and key levels
    """
    # Extract key indicators
    indicators = analysis_results["indicators"]
    patterns = analysis_results["patterns"]
    
    # Count bullish and bearish signals
    bullish_signals = 0
    bearish_signals = 0
    
    # Check moving averages
    for ma_name, ma_data in indicators["moving_averages"].items():
        if ma_data["trend"] == "Bullish":
            bullish_signals += 1
        elif ma_data["trend"] == "Bearish":
            bearish_signals += 1
    
    # Check oscillators
    rsi = indicators["oscillators"]["rsi"]
    macd = indicators["oscillators"]["macd"]
    stoch = indicators["oscillators"]["stochastic"]
    
    # RSI
    if rsi["trend"] == "Oversold":
        bullish_signals += 2
    elif rsi["trend"] == "Overbought":
        bearish_signals += 2
    
    # MACD
    if macd["trend"] == "Bullish":
        bullish_signals += 2
    elif macd["trend"] == "Bearish":
        bearish_signals += 2
    
    # Stochastic
    if stoch["trend"] == "Oversold":
        bullish_signals += 1
    elif stoch["trend"] == "Overbought":
        bearish_signals += 1
    
    # Check patterns
    for pattern in patterns:
        if "Uptrend" in pattern["name"] or "Bullish" in pattern["name"] or "Double Bottom" in pattern["name"]:
            bullish_signals += 2 * pattern["confidence"]
        elif "Downtrend" in pattern["name"] or "Bearish" in pattern["name"] or "Double Top" in pattern["name"]:
            bearish_signals += 2 * pattern["confidence"]
        elif "Head and Shoulders" in pattern["name"]:
            bearish_signals += 2 * pattern["confidence"]
        elif "Triangle" in pattern["name"]:
            if "Ascending" in pattern["name"]:
                bullish_signals += pattern["confidence"]
            elif "Descending" in pattern["name"]:
                bearish_signals += pattern["confidence"]
    
    # Determine action based on signals
    signal_diff = bullish_signals - bearish_signals
    
    if signal_diff > 4:
        action = "Strong Buy"
        rationale = f"Multiple bullish indicators and patterns suggest upward momentum on the {timeframe} timeframe. Moving averages are aligned bullishly with positive oscillator readings."
    elif signal_diff > 2:
        action = "Buy"
        rationale = f"Bullish signals outweigh bearish ones on the {timeframe} timeframe. Technical indicators suggest potential upward movement with moderate strength."
    elif signal_diff > 0:
        action = "Weak Buy"
        rationale = f"Slightly bullish signals on the {timeframe} timeframe, but caution is advised. Some indicators show positive momentum, but conviction is not strong."
    elif signal_diff == 0:
        action = "Neutral / Hold"
        rationale = f"Mixed signals on the {timeframe} timeframe suggest a sideways market. Equal bullish and bearish pressure indicates no clear direction at this time."
    elif signal_diff > -2:
        action = "Weak Sell"
        rationale = f"Slightly bearish signals on the {timeframe} timeframe. Some indicators show negative momentum, but conviction is not strong."
    elif signal_diff > -4:
        action = "Sell"
        rationale = f"Bearish signals outweigh bullish ones on the {timeframe} timeframe. Technical indicators suggest potential downward movement with moderate strength."
    else:
        action = "Strong Sell"
        rationale = f"Multiple bearish indicators and patterns suggest downward momentum on the {timeframe} timeframe. Moving averages are aligned bearishly with negative oscillator readings."
    
    # Determine entry, stop loss, and take profit levels
    support_levels = indicators["support_resistance"]["support"]
    resistance_levels = indicators["support_resistance"]["resistance"]
    
    # Simple calculation for a "current price" based on support and resistance
    current_price = (support_levels[0] + resistance_levels[-1]) / 2
    
    # Set entry, stop loss, and take profit based on action
    if "Buy" in action:
        entry_point = current_price
        stop_loss = support_levels[0] * 0.99  # Just below nearest support
        take_profit = resistance_levels[0] * 1.01  # Just above nearest resistance
    elif "Sell" in action:
        entry_point = current_price
        stop_loss = resistance_levels[0] * 1.01  # Just above nearest resistance
        take_profit = support_levels[0] * 0.99  # Just below nearest support
    else:  # Hold/Neutral
        entry_point = current_price
        stop_loss = support_levels[0] * 0.98  # Further below support for neutral stance
        take_profit = resistance_levels[0] * 1.02  # Further above resistance for neutral stance
    
    # Format to 2 decimal places
    entry_point = round(entry_point, 2)
    stop_loss = round(stop_loss, 2)
    take_profit = round(take_profit, 2)
    
    return {
        "action": action,
        "rationale": rationale,
        "entry_point": entry_point,
        "stop_loss": stop_loss,
        "take_profit": take_profit
    }
