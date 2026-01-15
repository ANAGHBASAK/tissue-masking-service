"""
Image I/O utilities for decoding and encoding images.
"""
import numpy as np
import cv2
from PIL import Image
import base64
import io


def decode_image(image_file):
    """
    Decode uploaded image file to numpy array.
    
    Args:
        image_file: Django UploadedFile or file-like object
    
    Returns:
        rgb_image: numpy array (H, W, 3) uint8 RGB [0-255]
    """
    # Read image using PIL (handles various formats)
    pil_image = Image.open(image_file)
    
    # Convert to RGB if needed
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Convert to numpy array
    rgb_array = np.array(pil_image)
    
    return rgb_array


def encode_mask_png(mask):
    """
    Encode binary mask as PNG base64 string.
    
    Args:
        mask: numpy array (H, W) uint8, 0=background, 255=tissue
    
    Returns:
        base64_string: Base64 encoded PNG
    """
    # Ensure mask is uint8
    mask_uint8 = mask.astype(np.uint8)
    
    # Encode as PNG
    success, buffer = cv2.imencode('.png', mask_uint8)
    if not success:
        raise ValueError("Failed to encode mask as PNG")
    
    # Convert to base64
    base64_string = base64.b64encode(buffer).decode('utf-8')
    
    return base64_string


def encode_image_png(image):
    """
    Encode RGB image as PNG base64 string.
    
    Args:
        image: numpy array (H, W, 3) uint8 RGB
    
    Returns:
        base64_string: Base64 encoded PNG
    """
    # Ensure image is uint8
    image_uint8 = image.astype(np.uint8)
    
    # Convert RGB to BGR for OpenCV
    image_bgr = cv2.cvtColor(image_uint8, cv2.COLOR_RGB2BGR)
    
    # Encode as PNG
    success, buffer = cv2.imencode('.png', image_bgr)
    if not success:
        raise ValueError("Failed to encode image as PNG")
    
    # Convert to base64
    base64_string = base64.b64encode(buffer).decode('utf-8')
    
    return base64_string
