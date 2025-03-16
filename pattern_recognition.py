import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import os

def identify_patterns(image_data, timeframe):
    """
    Identify common chart patterns in the processed image
    
    Args:
        image_data (dict): Dictionary containing processed images
        timeframe (str): The timeframe of the chart
        
    Returns:
        list: List of detected patterns with confidence scores
    """
    # Extract the processed images
    gray_image = image_data["gray"]
    edge_image = image_data["edges"]
    original_image = image_data["original"]
    
    # List to store detected patterns
    detected_patterns = []
    
    # Detect trend lines
    trend_lines = detect_trend_lines(edge_image)
    
    # Detect candlestick patterns
    candlestick_patterns = detect_candlestick_patterns(original_image)
    
    # Detect chart patterns
    head_and_shoulders = detect_head_and_shoulders(edge_image)
    double_top_bottom = detect_double_top_bottom(edge_image)
    triangle_patterns = detect_triangle_patterns(edge_image)
    
    # Add detected patterns to the list if they have sufficient confidence
    if trend_lines["uptrend"]["confidence"] > 0.6:
        detected_patterns.append({
            "name": "Uptrend",
            "description": "Price is making higher highs and higher lows, indicating bullish momentum.",
            "confidence": trend_lines["uptrend"]["confidence"]
        })
    
    if trend_lines["downtrend"]["confidence"] > 0.6:
        detected_patterns.append({
            "name": "Downtrend",
            "description": "Price is making lower highs and lower lows, indicating bearish momentum.",
            "confidence": trend_lines["downtrend"]["confidence"]
        })
        
    if trend_lines["sideways"]["confidence"] > 0.6:
        detected_patterns.append({
            "name": "Sideways/Consolidation",
            "description": "Price is moving within a range, indicating potential accumulation or distribution.",
            "confidence": trend_lines["sideways"]["confidence"]
        })
    
    # Add head and shoulders pattern if detected
    if head_and_shoulders["confidence"] > 0.7:
        detected_patterns.append({
            "name": "Head and Shoulders",
            "description": "Reversal pattern indicating a potential trend change from bullish to bearish.",
            "confidence": head_and_shoulders["confidence"]
        })
    
    # Add double top/bottom patterns if detected
    if double_top_bottom["double_top"]["confidence"] > 0.7:
        detected_patterns.append({
            "name": "Double Top",
            "description": "Bearish reversal pattern indicating resistance and potential downward movement.",
            "confidence": double_top_bottom["double_top"]["confidence"]
        })
    
    if double_top_bottom["double_bottom"]["confidence"] > 0.7:
        detected_patterns.append({
            "name": "Double Bottom",
            "description": "Bullish reversal pattern indicating support and potential upward movement.",
            "confidence": double_top_bottom["double_bottom"]["confidence"]
        })
    
    # Add triangle patterns if detected
    for pattern_name, pattern_data in triangle_patterns.items():
        if pattern_data["confidence"] > 0.65:
            if pattern_name == "ascending":
                description = "Bullish continuation pattern with higher lows and horizontal resistance."
            elif pattern_name == "descending":
                description = "Bearish continuation pattern with lower highs and horizontal support."
            else:  # symmetric
                description = "Neutral pattern indicating consolidation before a potential breakout."
                
            detected_patterns.append({
                "name": f"{pattern_name.capitalize()} Triangle",
                "description": description,
                "confidence": pattern_data["confidence"]
            })
    
    # Add candlestick patterns if detected
    for pattern in candlestick_patterns:
        detected_patterns.append(pattern)
    
    # If no patterns detected, add a general trend analysis
    if not detected_patterns:
        # Determine overall trend as fallback
        trend_strength = max(
            trend_lines["uptrend"]["confidence"],
            trend_lines["downtrend"]["confidence"],
            trend_lines["sideways"]["confidence"]
        )
        
        if trend_lines["uptrend"]["confidence"] == trend_strength:
            detected_patterns.append({
                "name": "Weak Uptrend",
                "description": "A mild bullish trend is visible but no clear pattern has formed.",
                "confidence": trend_strength
            })
        elif trend_lines["downtrend"]["confidence"] == trend_strength:
            detected_patterns.append({
                "name": "Weak Downtrend",
                "description": "A mild bearish trend is visible but no clear pattern has formed.",
                "confidence": trend_strength
            })
        else:
            detected_patterns.append({
                "name": "Neutral Market",
                "description": "No clear trend or pattern is visible. The market appears to be neutral.",
                "confidence": trend_strength
            })
    
    return detected_patterns

def detect_trend_lines(edge_image):
    """
    Detect trend lines in the chart using Hough Transform
    
    Args:
        edge_image (numpy.ndarray): Edge-detected image
        
    Returns:
        dict: Dictionary containing trend information with confidence scores
    """
    # Apply probabilistic Hough Transform to detect lines
    lines = cv2.HoughLinesP(
        edge_image, 1, np.pi/180, 
        threshold=50, minLineLength=50, maxLineGap=10
    )
    
    uptrend_count = 0
    downtrend_count = 0
    horizontal_count = 0
    
    # If no lines are detected, return default results
    if lines is None:
        return {
            "uptrend": {"confidence": 0.3},
            "downtrend": {"confidence": 0.3},
            "sideways": {"confidence": 0.5}
        }
    
    # Analyze the slopes of detected lines
    for line in lines:
        x1, y1, x2, y2 = line[0]
        
        # Skip if the line is too short
        if abs(x2 - x1) < 20:
            continue
        
        # Calculate slope (y is inverted in image coordinates)
        if x2 != x1:  # Avoid division by zero
            slope = (y2 - y1) / (x2 - x1)
            
            # Classify the slope
            if abs(slope) < 0.1:  # Almost horizontal
                horizontal_count += 1
            elif slope > 0:  # Downtrend (y increases downward in images)
                downtrend_count += 1
            else:  # Uptrend
                uptrend_count += 1
    
    total_lines = uptrend_count + downtrend_count + horizontal_count
    
    # If no significant lines were detected
    if total_lines == 0:
        return {
            "uptrend": {"confidence": 0.3},
            "downtrend": {"confidence": 0.3},
            "sideways": {"confidence": 0.5}
        }
    
    # Calculate confidence based on the proportion of each type of line
    uptrend_confidence = uptrend_count / total_lines
    downtrend_confidence = downtrend_count / total_lines
    sideways_confidence = horizontal_count / total_lines
    
    # Apply a bias based on line strength
    strongest = max(uptrend_confidence, downtrend_confidence, sideways_confidence)
    if strongest == uptrend_confidence:
        uptrend_confidence += 0.1
    elif strongest == downtrend_confidence:
        downtrend_confidence += 0.1
    else:
        sideways_confidence += 0.1
    
    # Cap confidences at 1.0
    uptrend_confidence = min(uptrend_confidence, 1.0)
    downtrend_confidence = min(downtrend_confidence, 1.0)
    sideways_confidence = min(sideways_confidence, 1.0)
    
    return {
        "uptrend": {"confidence": uptrend_confidence},
        "downtrend": {"confidence": downtrend_confidence},
        "sideways": {"confidence": sideways_confidence}
    }

def detect_candlestick_patterns(image):
    """
    Detect common candlestick patterns in the chart
    
    Args:
        image (numpy.ndarray): Original chart image
        
    Returns:
        list: List of detected candlestick patterns with confidence scores
    """
    # This is a simplified implementation for candlestick detection
    # In a production system, this would use more sophisticated image processing
    
    patterns = []
    h, w = image.shape[:2]
    
    # Analyze the bottom portion of the chart where recent candles are likely to be
    bottom_third = image[2*h//3:, :]
    
    # Convert to HSV for color analysis
    if len(image.shape) == 3:  # Color image
        hsv = cv2.cvtColor(bottom_third, cv2.COLOR_BGR2HSV)
        
        # Detect green candles (bullish)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        green_pixels = cv2.countNonZero(green_mask)
        
        # Detect red candles (bearish)
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_pixels = cv2.countNonZero(red_mask)
        
        total_colored_pixels = green_pixels + red_pixels
        if total_colored_pixels > 0:
            green_ratio = green_pixels / total_colored_pixels
            red_ratio = red_pixels / total_colored_pixels
            
            # Check for bullish engulfing
            if green_ratio > 0.6 and green_pixels > 100:
                patterns.append({
                    "name": "Bullish Candle Pattern",
                    "description": "Recent candles show strong buying pressure, suggesting bullish momentum.",
                    "confidence": min(0.5 + green_ratio, 0.9)
                })
            
            # Check for bearish engulfing
            if red_ratio > 0.6 and red_pixels > 100:
                patterns.append({
                    "name": "Bearish Candle Pattern",
                    "description": "Recent candles show strong selling pressure, suggesting bearish momentum.",
                    "confidence": min(0.5 + red_ratio, 0.9)
                })
    
    return patterns

def detect_head_and_shoulders(edge_image):
    """
    Detect head and shoulders pattern
    
    Args:
        edge_image (numpy.ndarray): Edge-detected image
        
    Returns:
        dict: Information about detected head and shoulders pattern
    """
    # Simplified implementation - in production, this would use more advanced algorithms
    
    # Use contour detection to find peak shapes
    contours, _ = cv2.findContours(edge_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) < 3:  # Need at least 3 major contours for head and shoulders
        return {"confidence": 0.0}
    
    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    # Get bounding rectangles for largest contours
    bounding_rects = [cv2.boundingRect(c) for c in contours[:3]]
    
    # Check if the pattern of heights resembles head and shoulders
    if len(bounding_rects) >= 3:
        # Extract heights
        heights = [h for (x, y, w, h) in bounding_rects]
        
        # Simple check: middle peak should be higher than surrounding peaks
        if len(heights) >= 3 and heights[1] > heights[0] and heights[1] > heights[2]:
            confidence = 0.6 + 0.2 * (heights[1] / max(heights[0], heights[2]))
            return {"confidence": min(confidence, 0.9)}
    
    return {"confidence": 0.2}

def detect_double_top_bottom(edge_image):
    """
    Detect double top or double bottom patterns
    
    Args:
        edge_image (numpy.ndarray): Edge-detected image
        
    Returns:
        dict: Information about detected double top/bottom patterns
    """
    # Use contour detection
    contours, _ = cv2.findContours(edge_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) < 2:  # Need at least 2 major contours
        return {
            "double_top": {"confidence": 0.1},
            "double_bottom": {"confidence": 0.1}
        }
    
    # Sort contours by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    
    # Get centroids of the contours
    centroids = []
    for c in contours:
        M = cv2.moments(c)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            centroids.append((cx, cy))
    
    # If we don't have at least 2 centroids, return low confidence
    if len(centroids) < 2:
        return {
            "double_top": {"confidence": 0.1},
            "double_bottom": {"confidence": 0.1}
        }
    
    # Sort centroids by x-coordinate (time axis)
    centroids.sort(key=lambda p: p[0])
    
    # Check for patterns
    double_top_confidence = 0.1
    double_bottom_confidence = 0.1
    
    for i in range(len(centroids) - 1):
        x1, y1 = centroids[i]
        x2, y2 = centroids[i + 1]
        
        # Check if the y-coordinates are close (tops or bottoms at similar levels)
        y_diff = abs(y1 - y2)
        if y_diff < edge_image.shape[0] * 0.05:  # Within 5% of image height
            # Check if the x-coordinates are sufficiently separated
            x_diff = abs(x1 - x2)
            if x_diff > edge_image.shape[1] * 0.15:  # At least 15% of image width apart
                # For a double top, y should be small (top of the image)
                if y1 < edge_image.shape[0] * 0.4:  # In top 40% of image
                    double_top_confidence = 0.7 + 0.2 * (1 - y_diff / (edge_image.shape[0] * 0.05))
                
                # For a double bottom, y should be large (bottom of the image)
                if y1 > edge_image.shape[0] * 0.6:  # In bottom 40% of image
                    double_bottom_confidence = 0.7 + 0.2 * (1 - y_diff / (edge_image.shape[0] * 0.05))
    
    return {
        "double_top": {"confidence": min(double_top_confidence, 0.9)},
        "double_bottom": {"confidence": min(double_bottom_confidence, 0.9)}
    }

def detect_triangle_patterns(edge_image):
    """
    Detect triangle patterns (ascending, descending, symmetric)
    
    Args:
        edge_image (numpy.ndarray): Edge-detected image
        
    Returns:
        dict: Information about detected triangle patterns
    """
    # Apply Hough Transform to detect lines
    lines = cv2.HoughLinesP(
        edge_image, 1, np.pi/180, 
        threshold=50, minLineLength=30, maxLineGap=10
    )
    
    if lines is None or len(lines) < 2:
        return {
            "ascending": {"confidence": 0.1},
            "descending": {"confidence": 0.1},
            "symmetric": {"confidence": 0.1}
        }
    
    # Separate lines by slope
    up_slopes = []
    down_slopes = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 - x1 == 0:  # Avoid division by zero
            continue
            
        slope = (y2 - y1) / (x2 - x1)
        
        if slope > 0:  # Downward slope (image y-axis is inverted)
            down_slopes.append(slope)
        elif slope < 0:  # Upward slope (image y-axis is inverted)
            up_slopes.append(slope)
    
    # Initialize confidences
    ascending_confidence = 0.1
    descending_confidence = 0.1
    symmetric_confidence = 0.1
    
    # Check for enough lines to form patterns
    if len(up_slopes) >= 2 and len(down_slopes) >= 2:
        # Calculate variance of slopes - lower variance means more consistent lines
        up_variance = np.var(up_slopes) if len(up_slopes) > 1 else 1
        down_variance = np.var(down_slopes) if len(down_slopes) > 1 else 1
        
        # Lower variance indicates more parallel lines, which is better for triangle patterns
        variance_factor = 1 / (1 + up_variance + down_variance)
        
        # Check for symmetric triangle (converging trend lines)
        if len(up_slopes) >= 1 and len(down_slopes) >= 1:
            up_avg = np.mean(up_slopes)
            down_avg = np.mean(down_slopes)
            
            # If slopes are of similar magnitude but opposite sign, likely a symmetric triangle
            if abs(abs(up_avg) - abs(down_avg)) < 0.2 * max(abs(up_avg), abs(down_avg)):
                symmetric_confidence = 0.6 + 0.3 * variance_factor
        
        # Check for ascending triangle (horizontal resistance, upward support)
        if any(abs(s) < 0.1 for s in down_slopes) and any(s < -0.1 for s in up_slopes):
            ascending_confidence = 0.6 + 0.3 * variance_factor
        
        # Check for descending triangle (horizontal support, downward resistance)
        if any(abs(s) < 0.1 for s in up_slopes) and any(s > 0.1 for s in down_slopes):
            descending_confidence = 0.6 + 0.3 * variance_factor
    
    return {
        "ascending": {"confidence": min(ascending_confidence, 0.9)},
        "descending": {"confidence": min(descending_confidence, 0.9)},
        "symmetric": {"confidence": min(symmetric_confidence, 0.9)}
    }
