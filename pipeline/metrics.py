"""
QC metrics and statistics computation.
"""
import numpy as np


def compute_qc_metrics(rgb_image, mask, od_image=None):
    """
    Compute quality control metrics.
    
    Args:
        rgb_image: (H, W, 3) uint8 RGB image
        mask: (H, W) uint8 binary mask, 0=background, 255=tissue
        od_image: (H, W, 3) float32 OD image (optional)
    
    Returns:
        metrics: dict with QC flags and statistics
    """
    tissue_area_fraction = np.sum(mask > 0) / mask.size
    
    # OD statistics (if available)
    if od_image is not None:
        tissue_od = od_image[mask > 0]
        if len(tissue_od) > 0:
            mean_total_od = float(np.mean(np.sum(tissue_od, axis=1)))
        else:
            mean_total_od = 0.0
    else:
        mean_total_od = None
    
    # QC flags
    qc_flags = []
    
    if tissue_area_fraction < 0.01:
        qc_flags.append("LOW_TISSUE_AREA")
    
    if mean_total_od is not None and mean_total_od < 0.1:
        qc_flags.append("LOW_OD_POOR_STAINING")
    
    # Check for saturation
    saturated_pixels = np.sum(np.any(rgb_image >= 250, axis=2))
    if saturated_pixels / rgb_image.size > 0.1:
        qc_flags.append("SATURATION_DETECTED")
    
    metrics = {
        "tissue_area_fraction": float(tissue_area_fraction),
        "qc_flags": qc_flags
    }
    
    if mean_total_od is not None:
        metrics["mean_total_od"] = mean_total_od
    
    return metrics
