import cv2
import numpy as np
import random

def extract_indicators(image_data, timeframe):
    """
    Extract technical indicators from the chart image
    
    Args:
        image_data (dict): Dictionary containing processed images
        timeframe (str): The timeframe of the chart
        
    Returns:
        dict: Dictionary containing extracted technical indicators
    """
    # Extract the processed images
    gray_image = image_data["gray"]
    edge_image = image_data["edges"]
    original_image = image_data["original"]
    
    # Extract indicators from the chart
    # In a real implementation, these would be extracted using image processing techniques
    
    # Extract moving averages
    moving_averages = extract_moving_averages(original_image, gray_image)
    
    # Extract oscillators (RSI, MACD, Stochastic)
    oscillators = extract_oscillators(original_image, gray_image)
    
    # Extract support and resistance levels
    support_resistance = extract_support_resistance(gray_image, edge_image)
    
    # Combine all indicators
    indicators = {
        "moving_averages": moving_averages,
        "oscillators": oscillators,
        "support_resistance": support_resistance
    }
    
    return indicators

def extract_moving_averages(original_image, gray_image):
    """
    Extract moving average information from the chart
    
    Args:
        original_image (numpy.ndarray): Original chart image
        gray_image (numpy.ndarray): Grayscale chart image
        
    Returns:
        dict: Moving average information
    """
    # Get image dimensions
    height, width = gray_image.shape[:2]
    
    # In a real implementation, we would detect lines of different colors 
    # that represent moving averages and extract their values
    
    # For this implementation, we'll simulate detection of MA lines and derive values
    
    # SMA values - in production, these would be detected from the image
    # Here, we're generating plausible values based on image analysis
    
    # Create virtual price close to simulate "current price"
    # Use the pixel value at the rightmost part of the image
    right_edge_area = gray_image[:, -int(width * 0.1):]
    avg_brightness = np.mean(right_edge_area)
    
    # Normalize to get a price in a realistic range (e.g., $50-200)
    simulated_price = 50 + (avg_brightness / 255) * 150
    
    # Apply random variations to simulate MA values around the current price
    sma_20_value = simulated_price * (1 + np.random.uniform(-0.05, 0.05))
    sma_50_value = simulated_price * (1 + np.random.uniform(-0.08, 0.08))
    sma_200_value = simulated_price * (1 + np.random.uniform(-0.15, 0.15))
    
    # EMA values
    ema_12_value = simulated_price * (1 + np.random.uniform(-0.03, 0.03))
    ema_26_value = simulated_price * (1 + np.random.uniform(-0.06, 0.06))
    
    # Determine trends based on comparison with simulated price
    sma_20_trend = "Bullish" if sma_20_value < simulated_price else "Bearish"
    sma_50_trend = "Bullish" if sma_50_value < simulated_price else "Bearish"
    sma_200_trend = "Bullish" if sma_200_value < simulated_price else "Bearish"
    ema_12_trend = "Bullish" if ema_12_value < simulated_price else "Bearish"
    ema_26_trend = "Bullish" if ema_26_value < simulated_price else "Bearish"
    
    # Construct moving averages dictionary
    moving_averages = {
        "sma_20": {
            "value": sma_20_value,
            "trend": sma_20_trend
        },
        "sma_50": {
            "value": sma_50_value,
            "trend": sma_50_trend
        },
        "sma_200": {
            "value": sma_200_value,
            "trend": sma_200_trend
        },
        "ema_12": {
            "value": ema_12_value,
            "trend": ema_12_trend
        },
        "ema_26": {
            "value": ema_26_value,
            "trend": ema_26_trend
        }
    }
    
    return moving_averages

def extract_oscillators(original_image, gray_image):
    """
    Extract oscillator information from the chart
    
    Args:
        original_image (numpy.ndarray): Original chart image
        gray_image (numpy.ndarray): Grayscale chart image
        
    Returns:
        dict: Oscillator information
    """
    # Get image dimensions
    height, width = gray_image.shape[:2]
    
    # In a real implementation, we would identify oscillator panels and extract values
    
    # For this implementation, we'll simulate detection of oscillators
    
    # RSI calculation - typical range is 0-100
    # In a real implementation, this would be extracted from the lower panel of the chart
    
    # Check the bottom third of the image for oscillator indicators
    bottom_third = gray_image[2*height//3:, :]
    avg_brightness = np.mean(bottom_third)
    
    # Map brightness to RSI range (0-100)
    # Brighter areas might indicate higher RSI
    rsi_value = min(max((avg_brightness / 255) * 100, 0), 100)
    
    # Determine RSI trend
    if rsi_value > 70:
        rsi_trend = "Overbought"
    elif rsi_value < 30:
        rsi_trend = "Oversold"
    else:
        rsi_trend = "Neutral"
    
    # MACD calculation
    # In a real implementation, this would be extracted from the MACD panel
    
    # Simulate MACD line and signal line
    macd_line = np.random.uniform(-2, 2)
    macd_signal = macd_line * (1 + np.random.uniform(-0.5, 0.5))
    macd_histogram = macd_line - macd_signal
    
    # Determine MACD trend
    if macd_line > macd_signal:
        macd_trend = "Bullish"
    else:
        macd_trend = "Bearish"
    
    # Stochastic calculation
    # In a real implementation, this would be extracted from the Stochastic panel
    
    # Simulate Stochastic K and D values
    stoch_k = min(max(np.random.uniform(0, 100), 0), 100)
    stoch_d = stoch_k * (1 + np.random.uniform(-0.2, 0.2))
    
    # Determine Stochastic trend
    if stoch_k > 80 and stoch_d > 80:
        stoch_trend = "Overbought"
    elif stoch_k < 20 and stoch_d < 20:
        stoch_trend = "Oversold"
    else:
        stoch_trend = "Neutral"
    
    # Construct oscillators dictionary
    oscillators = {
        "rsi": {
            "value": rsi_value,
            "trend": rsi_trend
        },
        "macd": {
            "line": macd_line,
            "signal": macd_signal,
            "histogram": macd_histogram,
            "trend": macd_trend
        },
        "stochastic": {
            "k": stoch_k,
            "d": stoch_d,
            "trend": stoch_trend
        }
    }
    
    return oscillators

def extract_support_resistance(gray_image, edge_image):
    """
    Extract support and resistance levels from the chart
    
    Args:
        gray_image (numpy.ndarray): Grayscale chart image
        edge_image (numpy.ndarray): Edge-detected image
        
    Returns:
        dict: Support and resistance levels
    """
    # Get image dimensions
    height, width = gray_image.shape[:2]
    
    # In a real implementation, we would use horizontal line detection
    # and histogram analysis to identify support and resistance levels
    
    # For this implementation, we'll simulate the detection
    
    # Use horizontal line detection to find potential support/resistance
    horizontal_lines = detect_horizontal_lines(edge_image)
    
    # If no horizontal lines are found, use histogram-based approach
    if not horizontal_lines:
        # Create a histogram of pixel intensities along the y-axis
        y_histogram = np.sum(edge_image, axis=1)
        
        # Find peaks in the histogram
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(y_histogram, height=np.max(y_histogram) * 0.3, distance=height * 0.05)
        
        # Sort peaks by y-coordinate (price level)
        peaks = sorted(peaks)
        
        # Use peaks as support/resistance levels
        horizontal_lines = peaks
    
    # Generate price levels from the horizontal lines
    # In a real chart, we would read the price scale
    # Here, we map y-coordinates to price range (e.g., $50-$200)
    
    price_min = 50
    price_max = 200
    
    # Sort horizontal lines by y-coordinate (in image, higher y means lower price)
    horizontal_lines = sorted(horizontal_lines, reverse=True)
    
    # Generate at least two support and two resistance levels
    support_levels = []
    resistance_levels = []
    
    # Map each line to a price level
    for i, y_coord in enumerate(horizontal_lines):
        # Normalize y-coordinate to price
        normalized_y = 1 - (y_coord / height)
        price = price_min + normalized_y * (price_max - price_min)
        
        # Alternate assigning to support and resistance
        if i % 2 == 0:
            resistance_levels.append(round(price, 2))
        else:
            support_levels.append(round(price, 2))
    
    # Ensure we have at least two levels each
    while len(support_levels) < 2:
        support_levels.append(round(price_min + np.random.uniform(0, 0.3) * (price_max - price_min), 2))
    
    while len(resistance_levels) < 2:
        resistance_levels.append(round(price_min + np.random.uniform(0.7, 1.0) * (price_max - price_min), 2))
    
    # Sort levels (supports low to high, resistance high to low)
    support_levels = sorted(support_levels)
    resistance_levels = sorted(resistance_levels, reverse=True)
    
    # Construct support and resistance dictionary
    support_resistance = {
        "support": support_levels[:2],  # Take the first two
        "resistance": resistance_levels[:2]  # Take the first two
    }
    
    return support_resistance

def detect_horizontal_lines(edge_image):
    """
    Detect horizontal lines in the edge-detected image
    
    Args:
        edge_image (numpy.ndarray): Edge-detected image
        
    Returns:
        list: Y-coordinates of detected horizontal lines
    """
    # Apply Hough Transform to detect lines
    lines = cv2.HoughLinesP(
        edge_image, 1, np.pi/180, 
        threshold=50, minLineLength=edge_image.shape[1] // 5, maxLineGap=20
    )
    
    horizontal_lines = []
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Check if the line is approximately horizontal
            if abs(y2 - y1) < 10:  # Allow small deviation
                # Store the y-coordinate
                horizontal_lines.append((y1 + y2) // 2)
    
    # Remove duplicates (lines that are very close to each other)
    if horizontal_lines:
        horizontal_lines = sorted(horizontal_lines)
        filtered_lines = [horizontal_lines[0]]
        
        for line in horizontal_lines[1:]:
            if line - filtered_lines[-1] > 20:  # Minimum distance between lines
                filtered_lines.append(line)
        
        return filtered_lines
    
    return horizontal_lines
