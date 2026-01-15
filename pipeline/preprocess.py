"""
Optional preprocessing: flat-field/illumination correction.
"""
import numpy as np


def flat_field_correction(rgb_image, flat_field_image):
    """
    Correct for non-uniform illumination using blank slide reference.
    
    Args:
        rgb_image: (H, W, 3) input image uint8
        flat_field_image: (H, W, 3) blank slide reference uint8
    
    Returns:
        corrected_image: (H, W, 3) corrected RGB uint8
    """
    # Normalize flat field to [0, 1]
    flat_field_norm = flat_field_image.astype(np.float32) / 255.0
    
    # Avoid division by zero
    flat_field_norm = np.clip(flat_field_norm, 0.01, 1.0)
    
    # Correct: I_corrected = I_raw / I_flat_field
    corrected = (rgb_image.astype(np.float32) / flat_field_norm)
    
    # Renormalize to [0, 255]
    corrected = np.clip(corrected, 0, 255).astype(np.uint8)
    
    return corrected
