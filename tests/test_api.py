"""
API contract tests.
"""
import unittest
from django.test import TestCase, Client
from django.urls import reverse
import json
import numpy as np
from PIL import Image
import io
import base64


class TissueMaskAPITest(TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def create_test_image(self, size=(200, 200)):
        """Create a test RGB image"""
        # Create image with white background and colored tissue
        img = np.ones((size[1], size[0], 3), dtype=np.uint8) * 255
        img[50:150, 50:150, :] = [180, 120, 80]  # Tissue region
        
        # Convert to PIL Image
        pil_img = Image.fromarray(img)
        
        # Save to BytesIO
        img_io = io.BytesIO()
        pil_img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return img_io
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
    
    def test_tissue_mask_endpoint(self):
        """Test tissue masking endpoint"""
        img_io = self.create_test_image()
        
        response = self.client.post(
            '/api/v1/tissue/mask/',
            {'image': img_io},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('mask_png_base64', data)
        self.assertIn('metrics', data)
    
    def test_tissue_mask_missing_image(self):
        """Test endpoint with missing image"""
        response = self.client.post('/api/v1/tissue/mask/')
        self.assertEqual(response.status_code, 200)  # Returns JSON error
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('error', data)


if __name__ == '__main__':
    unittest.main()
