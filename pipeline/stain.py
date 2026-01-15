"""
Unsupervised stain estimation using Macenko method.
Estimates dominant stain vectors using SVD on OD pixels.
"""
import numpy as np


def estimate_stain_vectors_macenko(od_image, alpha=1.0, beta=0.15):
    """
    Estimate stain vectors using Macenko method.
    
    Algorithm:
    1. Remove background pixels (low OD)
    2. Normalize to unit vectors (project onto plane)
    3. SVD to find principal directions
    4. Extract stain vectors (first two principal components)
    
    Args:
        od_image: (H, W, 3) float32 OD image
        alpha: percentile for stain vector selection (default 1.0 = 99th)
        beta: OD threshold to exclude background (default 0.15)
    
    Returns:
        stain_vectors: (2, 3) array, normalized stain vectors
    """
    # Step 1: Remove background pixels (low OD)
    pixels = od_image.reshape(-1, 3)
    total_od = np.sum(pixels, axis=1)
    tissue_mask = total_od > beta
    tissue_pixels = pixels[tissue_mask]
    
    if len(tissue_pixels) < 100:
        # Fallback: use all pixels
        tissue_pixels = pixels
    
    # Step 2: Normalize to unit vectors (project onto plane)
    # This removes intensity variation, keeping only color direction
    norms = np.linalg.norm(tissue_pixels, axis=1, keepdims=True)
    norms[norms == 0] = 1.0  # Avoid division by zero
    normalized_pixels = tissue_pixels / norms
    
    # Step 3: SVD to find principal directions
    # The two dominant directions correspond to stain vectors
    U, S, Vt = np.linalg.svd(normalized_pixels.T, full_matrices=False)
    
    # Step 4: Extract stain vectors (first two principal components)
    stain_vectors = Vt[:2, :]  # (2, 3)
    
    # Step 5: Ensure vectors point in correct direction
    # (Hematoxylin should be bluer, Eosin redder)
    # This is stain-specific and may need adjustment
    
    # Step 6: Normalize stain vectors
    stain_vectors = stain_vectors / np.linalg.norm(stain_vectors, axis=1, keepdims=True)
    
    return stain_vectors


def extract_stain_concentrations(od_image, stain_vectors):
    """
    Extract stain concentrations using least squares.
    
    Solve: OD = C @ stain_vectors^T
    where C is concentration matrix.
    
    Args:
        od_image: (H, W, 3) OD image
        stain_vectors: (2, 3) stain vectors
    
    Returns:
        concentrations: (H, W, 2) concentration maps
    """
    pixels = od_image.reshape(-1, 3)  # (N, 3)
    
    # Solve: OD = C @ stain_vectors^T
    # C = OD @ stain_vectors @ (stain_vectors^T @ stain_vectors)^(-1)
    stain_matrix = stain_vectors.T  # (3, 2)
    gram_matrix = stain_matrix.T @ stain_matrix  # (2, 2)
    
    # Avoid singular matrix
    if np.linalg.cond(gram_matrix) > 1e10:
        # Fallback: use pseudo-inverse
        concentrations = pixels @ stain_matrix @ np.linalg.pinv(gram_matrix)
    else:
        concentrations = pixels @ stain_matrix @ np.linalg.inv(gram_matrix)
    
    # Reshape back to image
    concentrations = concentrations.reshape(od_image.shape[0], od_image.shape[1], 2)
    
    # Clamp negative values (non-physical)
    concentrations = np.maximum(concentrations, 0)
    
    return concentrations
