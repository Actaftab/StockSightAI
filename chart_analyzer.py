import numpy as np
import cv2
from pattern_recognition import identify_patterns
from technical_indicators import extract_indicators

def analyze_chart(image, timeframe):
    """
    Main function to analyze a stock chart image and extract patterns and indicators
    
    Args:
        image (numpy.ndarray): The uploaded chart image in OpenCV format
        timeframe (str): The timeframe of the chart (e.g., '1m', '5m', '15m', '1h', etc.)
        
    Returns:
        dict: The analysis results containing patterns and technical indicators
    """
    # Preprocess the image
    processed_image = preprocess_image(image)
    
    # Identify patterns in the image
    patterns = identify_patterns(processed_image, timeframe)
    
    # Extract technical indicators
    indicators = extract_indicators(processed_image, timeframe)
    
    # Combine results
    results = {
        "patterns": patterns,
        "indicators": indicators
    }
    
    return results

def preprocess_image(image):
    """
    Preprocess the chart image for analysis
    
    Args:
        image (numpy.ndarray): The uploaded chart image
        
    Returns:
        numpy.ndarray: The preprocessed image
    """
    # Convert to grayscale if the image is in color
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding to enhance chart features
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Apply edge detection
    edges = cv2.Canny(thresh, 50, 150)
    
    # Dilate edges to make them more prominent
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # Return both the grayscale and processed edge image
    return {
        "gray": gray,
        "edges": dilated,
        "original": image
    }
