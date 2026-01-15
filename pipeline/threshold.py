"""
Adaptive thresholding in OD space.
Supports Otsu, Sauvola, and auto method selection.
"""
import numpy as np
from skimage.filters import threshold_otsu, threshold_sauvola
from scipy import signal


def otsu_threshold(od_channel):
    """
    Apply Otsu's method for automatic threshold selection.
    Works best when histogram is bimodal (background vs tissue).
    
    Args:
        od_channel: (H, W) float32 OD channel
    
    Returns:
        threshold: float, threshold value
    """
    # Flatten to 1D
    flat = od_channel.flatten()
    
    # Remove outliers (saturated pixels)
    flat = flat[flat < np.percentile(flat, 99.9)]
    
    if len(flat) == 0:
        return 0.0
    
    threshold = threshold_otsu(flat)
    return threshold


def sauvola_threshold(od_channel, window_size=15, k=0.2, R=128):
    """
    Sauvola's method: adaptive threshold based on local mean and std.
    Better for non-uniform illumination.
    
    Args:
        od_channel: (H, W) OD channel
        window_size: local window size
        k: parameter (typically 0.2)
        R: dynamic range (typically 128 for OD)
    
    Returns:
        threshold: float, mean threshold value
    """
    threshold_map = threshold_sauvola(
        od_channel,
        window_size=window_size,
        k=k,
        r=R
    )
    
    # Use mean of threshold map as global threshold
    threshold = np.mean(threshold_map)
    return threshold


def auto_threshold(od_channel):
    """
    Automatically choose between Otsu and Sauvola.
    Use Otsu if histogram is bimodal, else Sauvola.
    
    Args:
        od_channel: (H, W) OD channel
    
    Returns:
        threshold: float, threshold value
    """
    flat = od_channel.flatten()
    flat = flat[flat < np.percentile(flat, 99.9)]
    
    if len(flat) == 0:
        return 0.0
    
    # Check if histogram is bimodal
    hist, bins = np.histogram(flat, bins=50)
    peaks, _ = signal.find_peaks(hist, height=np.max(hist) * 0.1)
    
    if len(peaks) >= 2:
        # Bimodal: use Otsu
        return otsu_threshold(od_channel)
    else:
        # Unimodal: use Sauvola (more robust)
        return sauvola_threshold(od_channel)


def apply_threshold(od_channel, method='auto'):
    """
    Apply threshold and create binary mask.
    
    Args:
        od_channel: (H, W) float32 OD channel
        method: 'otsu', 'sauvola', or 'auto'
    
    Returns:
        mask: (H, W) uint8, 0=background, 255=tissue
    """
    if method == 'otsu':
        threshold = otsu_threshold(od_channel)
    elif method == 'sauvola':
        threshold = sauvola_threshold(od_channel)
    else:  # 'auto'
        threshold = auto_threshold(od_channel)
    
    mask = (od_channel > threshold).astype(np.uint8) * 255
    return mask
