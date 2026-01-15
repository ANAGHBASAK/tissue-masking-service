# Tissue Masking Service

Automated, Label-Free Tissue Masking and Stain Normalization for Digital Microscopy (H&E, IHC, PAP)

## Overview

This service provides a **scanner-agnostic, physics-based pipeline** for automatic tissue masking and optional stain normalization. It uses Optical Density (OD) transformation and unsupervised stain estimation to work across different microscopes without manual calibration.

## Key Features

- **Zero labeled data requirement** - Fully unsupervised
- **Scanner-agnostic** - Works across different microscopes without per-device tuning
- **Multi-stain support** - H&E, IHC, and PAP stains
- **Robust to illumination variation** - OD space handles exposure/gain differences
- **Adaptive thresholding** - Automatic per-image threshold selection
- **Optional stain normalization** - Removes batch-to-batch color variation

## Architecture

```
RGB Image → OD Transformation → Stain Estimation → Adaptive Thresholding → Binary Mask
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### API Endpoint

```bash
POST /api/v1/tissue/mask/
Content-Type: multipart/form-data

Parameters:
- image: JPG/PNG file
- normalize: bool (default: false)
- stain_method: 'macenko' or 'none' (default: 'macenko')
- threshold_method: 'otsu', 'sauvola', or 'auto' (default: 'auto')
- return_overlay: bool (default: false)
```

### Response

```json
{
  "success": true,
  "mask_png_base64": "...",
  "metrics": {
    "tissue_area_fraction": 0.45,
    "mean_total_od": 0.23,
    "qc_flags": []
  },
  "normalized_rgb_png_base64": "..."  // Optional
}
```

## Running the Service

### Development

```bash
cd tissue_service
python manage.py runserver
```

### Production (Docker)

```bash
docker-compose up
```

## Pipeline Details

See `docs/autoThresholdin.md` for technical details.

## Merging into Morpheus

### Quick Start

1. **Automated merge** (2 minutes):
   ```bash
   cd /tmp/tissue-masking-service
   export MORPHEUS_ROOT=/etc/morphle/code/morpheus
   ./scripts/merge_into_morpheus.sh
   ```

2. **Manual steps** (5 minutes):
   - Add imports to `django_server/api/urls.py`
   - Add URL patterns to `django_server/api/urls.py`
   - Verify OpenCV installation

3. **Test** (3 minutes):
   - Test imports in Django shell
   - Test health endpoint
   - Test tissue masking endpoint

**Total time: ~10 minutes**

### Detailed Guides

- **INSTALLATION_STEPS.md** - Complete step-by-step installation guide
- **MERGE_GUIDE.md** - Detailed merge instructions with troubleshooting
- **QUICKSTART.md** - Quick start for standalone usage

## License

[Your License Here]
