# Merge Guide: Integrating Tissue Masking Service into Morpheus

Complete step-by-step guide for merging tissue-masking-service into morpheus.

## Prerequisites

- Access to morpheus repository at `/etc/morphle/code/morpheus`
- Python 3.9+ environment
- Django installed
- Write permissions to morpheus directory

## Quick Merge (Recommended)

### Automated Steps (Run Script)

```bash
# 1. Navigate to tissue-masking-service
cd /tmp/tissue-masking-service

# 2. Set morpheus root (if different from default)
export MORPHEUS_ROOT=/etc/morphle/code/morpheus

# 3. Run merge script
./scripts/merge_into_morpheus.sh
```

The script will:
- ✅ Copy pipeline library to `src/morpho/commons/tissue_masking/`
- ✅ Copy API views to `django_server/api/views/`
- ✅ Update imports in `tissue_views.py` automatically
- ✅ Copy configuration files
- ✅ Update `requirements.txt` (avoid duplicates)

### Manual Steps (Required)

After running the script, complete these manual steps:

#### Step 1: Add Imports to `django_server/api/urls.py`

**Location:** `/etc/morphle/code/morpheus/django_server/api/urls.py`

**Action:** Add these import lines near the top (around line 20, with other view imports):

```python
from api.views.tissue_views import (
    tissue_mask_view,
    tissue_mask_batch_view,
    get_pipeline_status_view
)
from api.views.health_views import health_check_view
```

**Exact location:** After line 20 (after other `from api.views.*` imports)

#### Step 2: Add URL Patterns to `django_server/api/urls.py`

**Location:** `/etc/morphle/code/morpheus/django_server/api/urls.py`

**Action:** Add these URL patterns before the closing bracket of `urlpatterns` (around line 327, before the `if os.environ.get('DEPLOYMENT_MODE')` block):

```python
    path('tissue/mask/', tissue_mask_view, name='tissue-mask'),
    path('tissue/mask/batch/', tissue_mask_batch_view, name='tissue-mask-batch'),
    path('tissue/status/', get_pipeline_status_view, name='pipeline-status'),
```

**Exact location:** Add after line 327 (after `path('dicom/dicom_preview/', dicom_preview),`)

#### Step 3: Verify OpenCV Installation

```bash
# Check if cv2 is available
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

**If it fails:**
```bash
pip install opencv-python
# Or add to requirements.txt:
echo "opencv-python>=4.5.0" >> /etc/morphle/code/morpheus/requirements.txt
pip install -r requirements.txt
```

#### Step 4: Run Django Migrations (Optional)

Only needed if you want to use the database models for job tracking:

```bash
cd /etc/morphle/code/morpheus/django_server
python manage.py makemigrations api
python manage.py migrate
```

**Note:** The pipeline works without database models. Migrations are optional.

#### Step 5: Verify Installation

```bash
# Check Django can import the modules
cd /etc/morphle/code/morpheus/django_server
python manage.py shell
```

In the shell:
```python
# Test imports
from morpho.commons.tissue_masking.pipeline import TissueMaskingPipeline
from api.views.tissue_views import tissue_mask_view
print("✓ All imports successful!")
exit()
```

## Manual Merge (Alternative)

If you prefer to merge manually:

### Step 1: Copy Pipeline Library

```bash
# Create directory
mkdir -p /etc/morphle/code/morpheus/src/morpho/commons/tissue_masking

# Copy files
cp -r /tmp/tissue-masking-service/pipeline/* \
      /etc/morphle/code/morpheus/src/morpho/commons/tissue_masking/
```

### Step 2: Copy API Views

```bash
cp /tmp/tissue-masking-service/api/views/tissue_views.py \
   /etc/morphle/code/morpheus/django_server/api/views/

cp /tmp/tissue-masking-service/api/views/health_views.py \
   /etc/morphle/code/morpheus/django_server/api/views/
```

### Step 3: Update Imports in `tissue_views.py`

**File:** `/etc/morphle/code/morpheus/django_server/api/views/tissue_views.py`

**Change these lines:**

```python
# FROM:
from pipeline.pipeline import TissueMaskingPipeline
from pipeline.io import decode_image, encode_mask_png, encode_image_png
from pipeline.metrics import compute_qc_metrics

# TO:
from morpho.commons.tissue_masking.pipeline import TissueMaskingPipeline
from morpho.commons.tissue_masking.io import decode_image, encode_mask_png, encode_image_png
from morpho.commons.tissue_masking.metrics import compute_qc_metrics
```

**Or use sed:**
```bash
sed -i 's|from pipeline\.|from morpho.commons.tissue_masking.|g' \
    /etc/morphle/code/morpheus/django_server/api/views/tissue_views.py
```

### Step 4: Copy Configuration Files

```bash
mkdir -p /etc/morphle/code/morpheus/configs/tissue_masking
cp -r /tmp/tissue-masking-service/configs/* \
      /etc/morphle/code/morpheus/configs/tissue_masking/
```

### Step 5: Update Requirements

```bash
# Check what's missing
cd /etc/morphle/code/morpheus
grep -v "^#" /tmp/tissue-masking-service/requirements.txt | while read line; do
    pkg=$(echo "$line" | sed 's/[<>=].*//')
    if ! grep -qi "^${pkg}" requirements.txt 2>/dev/null; then
        echo "Missing: $line"
    fi
done

# Add missing packages (if any)
# Most should already be in morpheus requirements.txt
```

### Step 6: Add URL Routes

Follow **Step 1** and **Step 2** from the "Manual Steps" section above.

## Testing After Merge

### 1. Test Health Endpoint

```bash
curl http://localhost:8000/api/v1/health/
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "tissue-masking-service",
  "version": "1.0.0"
}
```

### 2. Test Tissue Masking Endpoint

```bash
# With a test image
curl -X POST http://localhost:8000/api/v1/tissue/mask/ \
  -F "image=@/path/to/test_image.jpg" \
  -F "normalize=false" \
  -F "threshold_method=auto"
```

**Expected response:**
```json
{
  "success": true,
  "mask_png_base64": "iVBORw0KGgoAAAANS...",
  "metrics": {
    "tissue_area_fraction": 0.45,
    "mean_total_od": 0.23,
    "qc_flags": []
  }
}
```

### 3. Test with Python

```python
import requests
import base64

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
    mask_data = base64.b64decode(result['mask_png_base64'])
    with open('mask.png', 'wb') as f:
        f.write(mask_data)
    
    print(f"Tissue area: {result['metrics']['tissue_area_fraction']:.2%}")
    print(f"QC flags: {result['metrics']['qc_flags']}")
else:
    print(f"Error: {result.get('error')}")
```

### 4. Check Django Logs

```bash
# Django error logs
tail -f /var/log/django.log

# Or supervisor logs
tail -f /var/log/morpheus.err.log
tail -f /var/log/morpheus.out.log
```

## File Structure After Merge

```
morpheus/
├── django_server/
│   └── api/
│       ├── urls.py                    # Updated with new routes
│       └── views/
│           ├── tissue_views.py        # Copied from service
│           └── health_views.py        # Copied from service
│
└── src/
    └── morpho/
        └── commons/
            └── tissue_masking/        # Copied from service
                ├── __init__.py
                ├── pipeline.py
                ├── od.py
                ├── stain.py
                ├── threshold.py
                ├── morphology.py
                ├── metrics.py
                ├── io.py
                ├── preprocess.py
                └── normalize.py
```

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'morpho.commons.tissue_masking'`

**Solution:**
```bash
# Ensure Python path includes src/
export PYTHONPATH=/etc/morphle/code/morpheus/src:$PYTHONPATH

# Or check Django settings
python manage.py shell
>>> import sys
>>> sys.path
```

### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'skimage'`

**Solution:**
```bash
pip install scikit-image scipy PyYAML
# Or
pip install -r requirements.txt
```

### OpenCV Not Found

**Error:** `ModuleNotFoundError: No module named 'cv2'`

**Solution:**
```bash
pip install opencv-python
# Or on Ubuntu/Debian:
sudo apt-get install python3-opencv
```

### URL Not Found (404)

**Error:** `Page not found (404)`

**Solution:**
1. Verify URLs were added to `urls.py`
2. Check Django server is running
3. Verify URL pattern matches: `/api/v1/tissue/mask/`
4. Check for typos in URL patterns

### Django Settings

**Error:** `django.core.exceptions.AppRegistryNotReady`

**Solution:**
Ensure `api` is in `INSTALLED_APPS` in Django settings:
```python
INSTALLED_APPS = [
    # ... other apps ...
    'api',
    # ...
]
```

## Rollback

If something goes wrong, you can rollback:

```bash
# Remove copied files
rm -rf /etc/morphle/code/morpheus/src/morpho/commons/tissue_masking
rm /etc/morphle/code/morpheus/django_server/api/views/tissue_views.py
rm /etc/morphle/code/morpheus/django_server/api/views/health_views.py

# Revert URL changes in urls.py
git checkout django_server/api/urls.py

# Revert requirements.txt (if changed)
git checkout requirements.txt
```

## Verification Checklist

After merge, verify:

- [ ] Pipeline modules copied to `src/morpho/commons/tissue_masking/`
- [ ] API views copied to `django_server/api/views/`
- [ ] Imports updated in `tissue_views.py`
- [ ] URL routes added to `urls.py`
- [ ] OpenCV available (`import cv2` works)
- [ ] Health endpoint responds: `/api/v1/health/`
- [ ] Tissue mask endpoint works: `/api/v1/tissue/mask/`
- [ ] No import errors in Django logs

## Next Steps

1. Test with real microscope images
2. Generate reference profiles for your stains (see `scripts/setup_reference_profiles.py`)
3. Tune morphology parameters if needed (edit `configs/pipeline_defaults.yaml`)
4. Monitor QC flags in production
5. Consider adding authentication/authorization if needed

## Support

For issues or questions:
- Check Django logs for detailed error messages
- Verify all dependencies are installed
- Ensure Python path includes `src/` directory
- Test imports in Django shell: `python manage.py shell`
