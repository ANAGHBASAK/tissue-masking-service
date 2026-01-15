# Quick Start Guide

## Installation

```bash
# Clone or download the repository
cd tissue-masking-service

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Service

### Development Mode

```bash
cd tissue_service
python manage.py migrate  # Create database (optional)
python manage.py runserver
```

The service will be available at `http://localhost:8000`

### Using Docker

```bash
docker-compose up
```

## Testing the API

### Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

### Tissue Masking

```bash
curl -X POST http://localhost:8000/api/v1/tissue/mask/ \
  -F "image=@path/to/your/image.jpg" \
  -F "normalize=false" \
  -F "threshold_method=auto"
```

### With Python

```python
import requests

url = "http://localhost:8000/api/v1/tissue/mask/"
files = {'image': open('test_image.jpg', 'rb')}
data = {
    'normalize': 'false',
    'threshold_method': 'auto'
}

response = requests.post(url, files=files, data=data)
result = response.json()

if result['success']:
    # Decode mask
    import base64
    mask_data = base64.b64decode(result['mask_png_base64'])
    with open('mask.png', 'wb') as f:
        f.write(mask_data)
    
    print(f"Tissue area: {result['metrics']['tissue_area_fraction']:.2%}")
    print(f"QC flags: {result['metrics']['qc_flags']}")
```

## Configuration

### Pipeline Parameters

Edit `configs/pipeline_defaults.yaml` to adjust:
- OD transformation parameters
- Stain estimation settings
- Thresholding methods
- Morphology cleanup parameters
- QC thresholds

### Reference Profiles

Generate reference profiles for stain normalization:

```bash
python scripts/setup_reference_profiles.py \
  --stain_type HE \
  --image_dir /path/to/good/he/images
```

## Running Tests

```bash
cd tissue_service
python manage.py test tests
```

## API Endpoints

- `GET /api/v1/health/` - Health check
- `POST /api/v1/tissue/mask/` - Single image tissue masking
- `POST /api/v1/tissue/mask/batch/` - Batch processing (not implemented yet)
- `GET /api/v1/tissue/status/` - Pipeline status

## Response Format

```json
{
  "success": true,
  "mask_png_base64": "iVBORw0KGgoAAAANS...",
  "metrics": {
    "tissue_area_fraction": 0.45,
    "mean_total_od": 0.23,
    "qc_flags": []
  },
  "normalized_rgb_png_base64": "..."  // Optional
}
```

## Troubleshooting

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Django Settings

If running standalone, ensure `DJANGO_SETTINGS_MODULE` is set:
```bash
export DJANGO_SETTINGS_MODULE=tissue_service.settings
```

### Port Already in Use

Change port:
```bash
python manage.py runserver 8001
```
