import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

def image_to_base64(image):
    """
    Convert an image to a base64 string
    
    Args:
        image: PIL Image or numpy array
        
    Returns:
        str: Base64 encoded string
    """
    if isinstance(image, np.ndarray):
        # Convert OpenCV image to PIL Image
        if len(image.shape) == 2:  # Grayscale
            image = Image.fromarray(image)
        else:  # Color
            image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def base64_to_image(base64_str):
    """
    Convert a base64 string to an image
    
    Args:
        base64_str (str): Base64 encoded string
        
    Returns:
        numpy.ndarray: Image as a numpy array
    """
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

def resize_image(image, max_size=800):
    """
    Resize an image while maintaining aspect ratio
    
    Args:
        image (numpy.ndarray): Image to resize
        max_size (int): Maximum dimension (width or height)
        
    Returns:
        numpy.ndarray: Resized image
    """
    height, width = image.shape[:2]
    
    # Calculate new dimensions
    if height > width:
        new_height = max_size
        new_width = int(width * (max_size / height))
    else:
        new_width = max_size
        new_height = int(height * (max_size / width))
    
    # Resize image
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

def apply_adaptive_threshold(image, block_size=11, c=2):
    """
    Apply adaptive thresholding to an image
    
    Args:
        image (numpy.ndarray): Grayscale image
        block_size (int): Block size for adaptive thresholding
        c (int): Constant subtracted from the mean
        
    Returns:
        numpy.ndarray: Thresholded image
    """
    # Ensure image is grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding
    return cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, block_size, c
    )

def get_timeframe_multiplier(timeframe):
    """
    Get a multiplier based on the timeframe for adjusting confidence levels
    
    Args:
        timeframe (str): Chart timeframe
        
    Returns:
        float: Multiplier value
    """
    # Lower timeframes generally have more noise
    if timeframe == "1m":
        return 0.8
    elif timeframe == "5m":
        return 0.85
    elif timeframe == "15m":
        return 0.9
    elif timeframe == "30m":
        return 0.95
    elif timeframe == "1h":
        return 1.0
    elif timeframe == "4h":
        return 1.05
    elif timeframe == "1D":
        return 1.1
    elif timeframe == "1W":
        return 1.15
    else:
        return 1.0
