"""
Stain concentration normalization.
Normalizes stain concentrations to match reference distribution.
"""
import numpy as np
import json
import os
from django.conf import settings


def normalize_stain_concentrations(concentrations, reference_stats):
    """
    Normalize concentrations to match reference distribution.
    
    Uses histogram matching: (x - μ_current) * (σ_ref / σ_current) + μ_ref
    
    Args:
        concentrations: (H, W, 2) concentration maps
        reference_stats: dict with 'mean' and 'std' for each stain
    
    Returns:
        normalized_concentrations: (H, W, 2)
    """
    normalized = np.zeros_like(concentrations)
    
    for i in range(2):  # For each stain
        conc_channel = concentrations[:, :, i]
        
        # Current statistics
        current_mean = np.mean(conc_channel)
        current_std = np.std(conc_channel)
        
        # Reference statistics
        ref_mean = reference_stats.get(f'stain_{i}_mean', current_mean)
        ref_std = reference_stats.get(f'stain_{i}_std', current_std)
        
        # Normalize: (x - μ_current) * (σ_ref / σ_current) + μ_ref
        if current_std > 1e-6:
            normalized[:, :, i] = (conc_channel - current_mean) * (ref_std / current_std) + ref_mean
        else:
            normalized[:, :, i] = conc_channel
        
        # Clamp to non-negative
        normalized[:, :, i] = np.maximum(normalized[:, :, i], 0)
    
    return normalized


def load_reference_profile(stain_type):
    """
    Load reference profile from JSON file.
    
    Args:
        stain_type: 'HE', 'IHC', or 'PAP'
    
    Returns:
        reference_stats: dict with mean/std for each stain
    """
    try:
        profile_path = os.path.join(
            settings.REFERENCE_PROFILES_DIR,
            f'{stain_type.lower()}_reference.json'
        )
        
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                return json.load(f)
        else:
            # Return None if no reference profile exists
            return None
    except Exception:
        return None


def generate_reference_profile(concentrations_list):
    """
    Generate reference statistics from a set of "good" images.
    
    Args:
        concentrations_list: list of (H, W, 2) concentration arrays
    
    Returns:
        reference_stats: dict with mean/std for each stain
    """
    all_concentrations = np.concatenate([c.reshape(-1, 2) for c in concentrations_list], axis=0)
    
    reference_stats = {
        'stain_0_mean': float(np.mean(all_concentrations[:, 0])),
        'stain_0_std': float(np.std(all_concentrations[:, 0])),
        'stain_1_mean': float(np.mean(all_concentrations[:, 1])),
        'stain_1_std': float(np.std(all_concentrations[:, 1])),
    }
    
    return reference_stats
