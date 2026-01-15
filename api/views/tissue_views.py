"""
Main tissue masking API endpoints.
"""
import base64
import io
import numpy as np
from PIL import Image
from rest_framework.decorators import api_view
from rest_framework.response import JsonResponse
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from pipeline.pipeline import TissueMaskingPipeline
from pipeline.io import decode_image, encode_mask_png, encode_image_png
from pipeline.metrics import compute_qc_metrics


def create_overlay(image, mask):
    """Create overlay visualization: green mask on original image"""
    overlay = image.copy().astype(np.float32)
    mask_bool = mask > 0
    overlay[mask_bool] = overlay[mask_bool] * 0.7 + np.array([0, 255, 0]) * 0.3
    return overlay.astype(np.uint8)


@api_view(['POST'])
@csrf_exempt
def tissue_mask_view(request):
    """
    POST /api/v1/tissue/mask/
    
    Request (multipart/form-data):
    - image: JPG/PNG file
    - normalize: bool (default: false) - Enable stain normalization
    - stain_method: str (default: 'macenko') - 'macenko' or 'none'
    - threshold_method: str (default: 'auto') - 'otsu', 'sauvola', or 'auto'
    - return_overlay: bool (default: false) - Return overlay visualization
    
    Response (JSON):
    {
        "success": true,
        "mask_png_base64": "...",  # Base64 encoded PNG mask
        "metrics": {
            "tissue_area_fraction": 0.45,
            "mean_total_od": 0.23,
            "qc_flags": []
        },
        "normalized_rgb_png_base64": "..."  # Optional, if normalize=true
    }
    """
    try:
        # 1. Extract uploaded image
        if 'image' not in request.FILES:
            return JsonResponse(
                {"success": False, "error": "No image file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        image_array = decode_image(image_file)  # Returns numpy array (H, W, 3) RGB
        
        # 2. Extract optional parameters
        normalize = request.POST.get('normalize', 'false').lower() == 'true'
        stain_method = request.POST.get('stain_method', 'macenko')
        threshold_method = request.POST.get('threshold_method', 'auto')
        return_overlay = request.POST.get('return_overlay', 'false').lower() == 'true'
        
        # 3. Initialize pipeline
        pipeline = TissueMaskingPipeline(
            normalize=normalize,
            stain_method=stain_method,
            threshold_method=threshold_method
        )
        
        # 4. Process image
        result = pipeline.process(image_array)
        
        # 5. Compute metrics
        metrics = compute_qc_metrics(image_array, result['mask'], result.get('od_image'))
        
        # 6. Prepare response
        mask_png_base64 = encode_mask_png(result['mask'])
        
        response_data = {
            "success": True,
            "mask_png_base64": mask_png_base64,
            "metrics": metrics
        }
        
        # Optional: Add normalized RGB if requested
        if normalize and 'normalized_rgb' in result:
            normalized_png_base64 = encode_image_png(result['normalized_rgb'])
            response_data["normalized_rgb_png_base64"] = normalized_png_base64
        
        # Optional: Add overlay visualization
        if return_overlay:
            overlay = create_overlay(image_array, result['mask'])
            overlay_png_base64 = encode_image_png(overlay)
            response_data["overlay_png_base64"] = overlay_png_base64
        
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return JsonResponse(
            {"success": False, "error": str(e), "traceback": error_trace},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@csrf_exempt
def tissue_mask_batch_view(request):
    """
    POST /api/v1/tissue/mask/batch/
    
    Batch processing endpoint (for multiple images).
    """
    # TODO: Implement batch processing
    return JsonResponse(
        {"success": False, "error": "Batch processing not yet implemented"},
        status=status.HTTP_501_NOT_IMPLEMENTED
    )


@api_view(['GET'])
def get_pipeline_status_view(request):
    """
    GET /api/v1/tissue/status/
    
    Get pipeline status and configuration.
    """
    return JsonResponse({
        "status": "operational",
        "pipeline_version": "1.0.0",
        "supported_stains": ["HE", "IHC", "PAP"],
        "supported_methods": {
            "stain_estimation": ["macenko", "none"],
            "thresholding": ["otsu", "sauvola", "auto"]
        }
    })
