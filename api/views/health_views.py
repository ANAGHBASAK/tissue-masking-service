"""
Health check endpoints.
"""
from rest_framework.decorators import api_view
from rest_framework.response import JsonResponse
from rest_framework import status


@api_view(['GET'])
def health_check_view(request):
    """
    Health check endpoint.
    
    GET /api/v1/health/
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'tissue-masking-service',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)
