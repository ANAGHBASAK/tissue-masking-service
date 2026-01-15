"""
End-to-end integration tests.
"""
import unittest
import numpy as np
from pipeline.pipeline import TissueMaskingPipeline


class IntegrationTest(unittest.TestCase):
    """End-to-end integration tests"""
    
    def test_full_pipeline_he(self):
        """Test full pipeline for H&E stain"""
        # Create synthetic H&E-like image
        rgb = np.ones((500, 500, 3), dtype=np.uint8) * 255
        
        # Add tissue regions with different colors
        rgb[100:200, 100:200, :] = [180, 150, 120]  # Light tissue
        rgb[300:400, 300:400, :] = [120, 100, 80]   # Darker tissue
        
        pipeline = TissueMaskingPipeline(
            normalize=False,
            stain_method='macenko',
            threshold_method='auto',
            stain_type='HE'
        )
        
        result = pipeline.process(rgb)
        
        # Check results
        self.assertIn('mask', result)
        self.assertIn('metrics', result)
        
        # Should detect tissue regions
        tissue_fraction = result['metrics']['tissue_area_fraction']
        self.assertGreater(tissue_fraction, 0.0)
        self.assertLess(tissue_fraction, 1.0)
    
    def test_pipeline_determinism(self):
        """Test that pipeline produces deterministic results"""
        rgb = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        pipeline = TissueMaskingPipeline(
            normalize=False,
            stain_method='none',
            threshold_method='otsu'
        )
        
        result1 = pipeline.process(rgb)
        result2 = pipeline.process(rgb)
        
        # Results should be identical
        np.testing.assert_array_equal(result1['mask'], result2['mask'])


if __name__ == '__main__':
    unittest.main()
