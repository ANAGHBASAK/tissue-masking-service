"""
Morphological cleanup operations for binary masks.
"""
import numpy as np
import cv2
from scipy import ndimage


def morphological_cleanup(mask, min_area=100, kernel_size=3):
    """
    Clean up binary mask using morphological operations.
    
    Steps:
    1. Remove small objects (noise)
    2. Fill holes
    3. Smooth boundaries
    
    Args:
        mask: (H, W) uint8 binary mask, 0=background, 255=tissue
        min_area: minimum area for connected components
        kernel_size: size of morphological kernel
    
    Returns:
        cleaned_mask: (H, W) uint8 cleaned binary mask
    """
    # Step 1: Remove small connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    
    # Filter by area
    cleaned_mask = np.zeros_like(mask)
    for i in range(1, num_labels):  # Skip background (label 0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            cleaned_mask[labels == i] = 255
    
    # Step 2: Fill holes
    cleaned_mask = ndimage.binary_fill_holes(cleaned_mask).astype(np.uint8) * 255
    
    # Step 3: Morphological operations to smooth
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # Opening: remove small protrusions
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Closing: fill small gaps
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    return cleaned_mask
