"""
Main pipeline orchestrator.
Scanner-agnostic tissue masking pipeline.
"""
import numpy as np
from .od import rgb_to_od, compute_total_od
from .stain import estimate_stain_vectors_macenko, extract_stain_concentrations
from .normalize import normalize_stain_concentrations, load_reference_profile
from .threshold import apply_threshold
from .morphology import morphological_cleanup
from .metrics import compute_qc_metrics


class TissueMaskingPipeline:
    """
    Main pipeline orchestrator.
    Scanner-agnostic: no device-specific tuning.
    """
    
    def __init__(self, normalize=False, stain_method='macenko', threshold_method='auto', stain_type='HE'):
        """
        Initialize pipeline.
        
        Args:
            normalize: bool, enable stain normalization
            stain_method: 'macenko' or 'none'
            threshold_method: 'otsu', 'sauvola', or 'auto'
            stain_type: 'HE', 'IHC', or 'PAP' (for reference profile loading)
        """
        self.normalize = normalize
        self.stain_method = stain_method
        self.threshold_method = threshold_method
        self.stain_type = stain_type
    
    def process(self, rgb_image, flat_field=None):
        """
        Process RGB image through full pipeline.
        
        Args:
            rgb_image: numpy array (H, W, 3) uint8 RGB
            flat_field: optional (H, W, 3) uint8 flat field image
        
        Returns:
            dict with keys: 'mask', 'od_image', 'normalized_rgb' (optional), 'metrics'
        """
        # Step 1: Optional flat-field correction
        if flat_field is not None:
            from .preprocess import flat_field_correction
            rgb_image = flat_field_correction(rgb_image, flat_field)
        
        # Step 2: RGB → OD
        od_image = rgb_to_od(rgb_image)
        
        # Step 3: Optional stain estimation
        if self.stain_method == 'macenko':
            stain_vectors = estimate_stain_vectors_macenko(od_image)
            concentrations = extract_stain_concentrations(od_image, stain_vectors)
            
            # Optional normalization
            if self.normalize:
                reference_stats = load_reference_profile(self.stain_type)
                if reference_stats:
                    concentrations = normalize_stain_concentrations(concentrations, reference_stats)
            
            # Threshold on concentrations (use max of both stains)
            threshold_input = np.maximum(concentrations[:, :, 0], concentrations[:, :, 1])
        else:
            # Threshold on total OD (stain-agnostic)
            threshold_input = compute_total_od(od_image)
        
        # Step 4: Adaptive thresholding
        mask = apply_threshold(threshold_input, method=self.threshold_method)
        
        # Step 5: Morphological cleanup
        mask = morphological_cleanup(mask)
        
        # Step 6: Compute metrics
        metrics = compute_qc_metrics(rgb_image, mask, od_image)
        
        result = {
            'mask': mask,
            'od_image': od_image,
            'metrics': metrics
        }
        
        # Optional: Reconstruct normalized RGB for visualization
        if self.normalize and self.stain_method == 'macenko' and 'concentrations' in locals():
            # Reconstruct OD from normalized concentrations
            stain_matrix = stain_vectors.T
            normalized_od = concentrations.reshape(-1, 2) @ stain_matrix.T
            normalized_od = normalized_od.reshape(od_image.shape)
            
            # Convert back to RGB
            normalized_rgb = od_to_rgb(normalized_od)
            result['normalized_rgb'] = normalized_rgb
        
        return result


def od_to_rgb(od_image, white_reference=255.0):
    """
    Convert OD back to RGB.
    
    Args:
        od_image: (H, W, 3) float32 OD image
        white_reference: float, white reference value
    
    Returns:
        rgb_image: (H, W, 3) uint8 RGB
    """
    # Reverse OD: I = I0 * 10^(-OD)
    rgb_normalized = white_reference * np.power(10.0, -od_image)
    
    # Clip and convert to uint8
    rgb_image = np.clip(rgb_normalized, 0, 255).astype(np.uint8)
    
    return rgb_image
