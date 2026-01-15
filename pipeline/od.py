"""
Optical Density (OD) transformation.
Converts RGB intensity to absorbance space.
"""
import numpy as np


def rgb_to_od(rgb_image, white_reference=255.0, epsilon=1.0):
    """
    Convert RGB to Optical Density space.
    
    OD = -log₁₀((I + ε) / I₀)
    
    Properties:
    - Background glass ≈ 0 OD
    - Tissue pixels > 0 OD
    - Robust to illumination, exposure, and gain changes
    
    Args:
        rgb_image: numpy array (H, W, 3) uint8 [0-255]
        white_reference: float, typically 255.0 or estimated per-channel
        epsilon: small value to prevent log(0)
    
    Returns:
        od_image: numpy array (H, W, 3) float32, OD values
    """
    # Normalize to [0, 1]
    rgb_normalized = (rgb_image.astype(np.float32) + epsilon) / (white_reference + epsilon)
    
    # Avoid zeros (would cause -inf in log)
    rgb_normalized = np.clip(rgb_normalized, 1e-6, 1.0)
    
    # Compute OD: -log(I/I0)
    od_image = -np.log10(rgb_normalized)
    
    return od_image


def estimate_white_reference(rgb_image, percentile=99.5):
    """
    Estimate white reference from bright pixels (background glass).
    Uses high percentile to avoid outliers.
    
    Args:
        rgb_image: (H, W, 3) uint8 RGB
        percentile: percentile to use for estimation
    
    Returns:
        white_ref: (3,) float32 array, per-channel white reference
    """
    # Flatten image
    pixels = rgb_image.reshape(-1, 3)
    
    # Get bright pixels (likely background)
    bright_threshold = np.percentile(pixels, percentile, axis=0)
    bright_mask = np.all(pixels >= bright_threshold, axis=1)
    bright_pixels = pixels[bright_mask]
    
    if len(bright_pixels) > 0:
        white_ref = np.percentile(bright_pixels, 99.9, axis=0)
    else:
        white_ref = np.array([255.0, 255.0, 255.0])
    
    return white_ref.astype(np.float32)


def compute_total_od(od_image):
    """
    Compute total OD: sum of all channels.
    Background ≈ 0, tissue > 0.
    
    Args:
        od_image: (H, W, 3) float32 OD image
    
    Returns:
        total_od: (H, W) float32, sum of OD channels
    """
    return np.sum(od_image, axis=2)
