"""API URL Configuration"""
from django.urls import path
from api.views.tissue_views import (
    tissue_mask_view,
    tissue_mask_batch_view,
    get_pipeline_status_view
)
from api.views.health_views import health_check_view

urlpatterns = [
    # Main endpoint: single image tissue masking
    path('tissue/mask/', tissue_mask_view, name='tissue-mask'),
    
    # Batch processing (optional, for multiple images)
    path('tissue/mask/batch/', tissue_mask_batch_view, name='tissue-mask-batch'),
    
    # Pipeline status/health
    path('tissue/status/', get_pipeline_status_view, name='pipeline-status'),
    
    # Health check
    path('health/', health_check_view, name='health-check'),
]
