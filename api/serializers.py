"""
Request/response serializers for API validation.
"""
from rest_framework import serializers


class TissueMaskRequestSerializer(serializers.Serializer):
    """Validate tissue masking request"""
    image = serializers.ImageField(required=True)
    normalize = serializers.BooleanField(default=False, required=False)
    stain_method = serializers.ChoiceField(
        choices=['macenko', 'none'],
        default='macenko',
        required=False
    )
    threshold_method = serializers.ChoiceField(
        choices=['otsu', 'sauvola', 'auto'],
        default='auto',
        required=False
    )
    return_overlay = serializers.BooleanField(default=False, required=False)


class TissueMaskResponseSerializer(serializers.Serializer):
    """Structure for tissue masking response"""
    success = serializers.BooleanField()
    mask_png_base64 = serializers.CharField()
    metrics = serializers.DictField()
    normalized_rgb_png_base64 = serializers.CharField(required=False, allow_null=True)
    overlay_png_base64 = serializers.CharField(required=False, allow_null=True)
    error = serializers.CharField(required=False, allow_null=True)
