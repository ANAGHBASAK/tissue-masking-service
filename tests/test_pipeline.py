"""
Unit tests for pipeline modules.
"""
import unittest
import numpy as np
from pipeline.od import rgb_to_od, compute_total_od
from pipeline.stain import estimate_stain_vectors_macenko, extract_stain_concentrations
from pipeline.threshold import apply_threshold
from pipeline.morphology import morphological_cleanup
from pipeline.pipeline import TissueMaskingPipeline


class TestOD(unittest.TestCase):
    """Test Optical Density transformation"""
    
    def test_rgb_to_od(self):
        """Test RGB to OD conversion"""
        # Create test image (white background, some colored tissue)
        rgb = np.ones((100, 100, 3), dtype=np.uint8) * 255
        rgb[30:70, 30:70, :] = [200, 150, 100]  # Tissue region
        
        od = rgb_to_od(rgb)
        
        # Background should have low OD
        self.assertLess(np.mean(od[0:20, 0:20]), 0.1)
        
        # Tissue should have higher OD
        self.assertGreater(np.mean(od[30:70, 30:70]), 0.1)
    
    def test_compute_total_od(self):
        """Test total OD computation"""
        od = np.array([[[0.1, 0.2, 0.3], [0.2, 0.3, 0.4]],
                       [[0.3, 0.4, 0.5], [0.4, 0.5, 0.6]]])
        total = compute_total_od(od)
        
        self.assertEqual(total.shape, (2, 2))
        self.assertAlmostEqual(total[0, 0], 0.6, places=5)


class TestStain(unittest.TestCase):
    """Test stain estimation"""
    
    def test_estimate_stain_vectors(self):
        """Test Macenko stain vector estimation"""
        # Create synthetic OD image with two stains
        od = np.random.rand(100, 100, 3).astype(np.float32) * 0.5 + 0.1
        
        stain_vectors = estimate_stain_vectors_macenko(od)
        
        self.assertEqual(stain_vectors.shape, (2, 3))
        # Check normalization
        norms = np.linalg.norm(stain_vectors, axis=1)
        np.testing.assert_allclose(norms, 1.0, rtol=1e-5)


class TestThreshold(unittest.TestCase):
    """Test thresholding"""
    
    def test_apply_threshold(self):
        """Test threshold application"""
        # Create bimodal distribution
        od_channel = np.zeros((100, 100), dtype=np.float32)
        od_channel[0:50, :] = 0.05  # Background
        od_channel[50:, :] = 0.5    # Tissue
        
        mask = apply_threshold(od_channel, method='otsu')
        
        # Should separate background and tissue
        self.assertLess(np.sum(mask[0:50, :] > 0), np.sum(mask[50:, :] > 0))


class TestPipeline(unittest.TestCase):
    """Test complete pipeline"""
    
    def test_pipeline_basic(self):
        """Test basic pipeline execution"""
        # Create synthetic RGB image
        rgb = np.ones((200, 200, 3), dtype=np.uint8) * 255
        rgb[50:150, 50:150, :] = [180, 120, 80]  # Tissue region
        
        pipeline = TissueMaskingPipeline(
            normalize=False,
            stain_method='none',
            threshold_method='auto'
        )
        
        result = pipeline.process(rgb)
        
        self.assertIn('mask', result)
        self.assertIn('od_image', result)
        self.assertIn('metrics', result)
        
        # Mask should be binary
        self.assertTrue(np.all(np.isin(result['mask'], [0, 255])))


if __name__ == '__main__':
    unittest.main()
