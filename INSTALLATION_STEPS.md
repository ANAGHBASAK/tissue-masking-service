# Installation Steps - Quick Reference

## Complete Installation Process

### Time Estimate: 10-15 minutes

---

## Phase 1: Automated Steps (2 minutes)

### Step 1: Run Merge Script

```bash
cd /tmp/tissue-masking-service
export MORPHEUS_ROOT=/etc/morphle/code/morpheus
./scripts/merge_into_morpheus.sh
```

**What it does:**
- Copies pipeline modules → `src/morpho/commons/tissue_masking/`
- Copies API views → `django_server/api/views/`
- Updates imports automatically
- Copies configs → `configs/tissue_masking/`
- Updates requirements.txt

**Expected output:**
```
[1/5] Copying pipeline library...
  ✓ Copied pipeline modules
[2/5] Copying API views...
  ✓ Copied tissue_views.py and health_views.py
[3/5] Updating imports...
  ✓ Updated imports
[4/5] Copying configuration files...
  ✓ Copied configuration files
[5/5] Updating requirements.txt...
  ✓ Updated requirements
```

---

## Phase 2: Manual Steps (5 minutes)

### Step 2: Add Imports to `django_server/api/urls.py`

**File:** `/etc/morphle/code/morpheus/django_server/api/urls.py`

**Find:** Line ~20 (after other `from api.views.*` imports)

**Add:**
```python
from api.views.tissue_views import (
    tissue_mask_view,
    tissue_mask_batch_view,
    get_pipeline_status_view
)
from api.views.health_views import health_check_view
```

**Quick command:**
```bash
# Backup first
cp /etc/morphle/code/morpheus/django_server/api/urls.py \
   /etc/morphle/code/morpheus/django_server/api/urls.py.backup

# Add imports (after line 20)
sed -i '20a from api.views.tissue_views import tissue_mask_view, tissue_mask_batch_view, get_pipeline_status_view\nfrom api.views.health_views import health_check_view' \
    /etc/morphle/code/morpheus/django_server/api/urls.py
```

### Step 3: Add URL Patterns to `django_server/api/urls.py`

**File:** `/etc/morphle/code/morpheus/django_server/api/urls.py`

**Find:** Line ~327 (before `if os.environ.get('DEPLOYMENT_MODE')`)

**Add before closing bracket:**
```python
    path('tissue/mask/', tissue_mask_view, name='tissue-mask'),
    path('tissue/mask/batch/', tissue_mask_batch_view, name='tissue-mask-batch'),
    path('tissue/status/', get_pipeline_status_view, name='pipeline-status'),
```

**Quick command:**
```bash
# Add URLs before line 329
sed -i '329i     path('\''tissue/mask/'\'', tissue_mask_view, name='\''tissue-mask'\''),\n    path('\''tissue/mask/batch/'\'', tissue_mask_batch_view, name='\''tissue-mask-batch'\''),\n    path('\''tissue/status/'\'', get_pipeline_status_view, name='\''pipeline-status'\''),' \
    /etc/morphle/code/morpheus/django_server/api/urls.py
```

**Or edit manually** (recommended for clarity)

### Step 4: Verify OpenCV

```bash
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
```

**If fails:**
```bash
pip install opencv-python
# Or add to requirements.txt and install
echo "opencv-python>=4.5.0" >> /etc/morphle/code/morpheus/requirements.txt
pip install opencv-python
```

---

## Phase 3: Verification (3 minutes)

### Step 5: Test Imports

```bash
cd /etc/morphle/code/morpheus/django_server
python manage.py shell
```

In shell:
```python
from morpho.commons.tissue_masking.pipeline import TissueMaskingPipeline
from api.views.tissue_views import tissue_mask_view
print("✓ All imports successful!")
exit()
```

### Step 6: Test Health Endpoint

```bash
curl http://localhost:8000/api/v1/health/
```

**Expected:**
```json
{"status": "healthy", "service": "tissue-masking-service", "version": "1.0.0"}
```

### Step 7: Test Tissue Masking

```bash
curl -X POST http://localhost:8000/api/v1/tissue/mask/ \
  -F "image=@test_image.jpg" \
  -F "normalize=false" \
  -F "threshold_method=auto"
```

**Expected:** JSON response with `success: true` and `mask_png_base64`

---

## Complete Command Sequence

Copy-paste this entire sequence:

```bash
# 1. Run automated merge
cd /tmp/tissue-masking-service
export MORPHEUS_ROOT=/etc/morphle/code/morpheus
./scripts/merge_into_morpheus.sh

# 2. Verify OpenCV
python3 -c "import cv2; print('OpenCV OK')" || pip install opencv-python

# 3. Test imports
cd /etc/morphle/code/morpheus/django_server
python manage.py shell <<EOF
from morpho.commons.tissue_masking.pipeline import TissueMaskingPipeline
print("✓ Imports OK")
exit()
EOF

# 4. Test health endpoint (if server is running)
curl http://localhost:8000/api/v1/health/ 2>/dev/null || echo "Server not running - start Django server first"
```

**Then manually edit `urls.py`** (Steps 2-3 above)

---

## Troubleshooting Quick Fixes

### Import Error
```bash
export PYTHONPATH=/etc/morphle/code/morpheus/src:$PYTHONPATH
```

### Missing Dependencies
```bash
pip install scikit-image scipy PyYAML opencv-python
```

### URL 404 Error
- Check `urls.py` was edited correctly
- Verify Django server is running
- Check URL path: `/api/v1/tissue/mask/`

### Django Settings Error
- Ensure `api` is in `INSTALLED_APPS`
- Check Django version compatibility

---

## Success Indicators

✅ Script completes without errors  
✅ No import errors in Django shell  
✅ Health endpoint returns JSON  
✅ Tissue mask endpoint accepts images  
✅ No errors in Django logs  

---

## Next Steps After Installation

1. **Generate reference profiles** (optional):
   ```bash
   python scripts/setup_reference_profiles.py \
     --stain_type HE \
     --image_dir /path/to/good/he/images
   ```

2. **Tune parameters** (if needed):
   - Edit `configs/tissue_masking/pipeline_defaults.yaml`

3. **Monitor production**:
   - Check QC flags in responses
   - Monitor tissue area fractions
   - Review Django logs

---

## Rollback Instructions

If something goes wrong:

```bash
# Remove all changes
rm -rf /etc/morphle/code/morpheus/src/morpho/commons/tissue_masking
rm /etc/morphle/code/morpheus/django_server/api/views/tissue_views.py
rm /etc/morphle/code/morpheus/django_server/api/views/health_views.py

# Restore urls.py from backup
cp /etc/morphle/code/morpheus/django_server/api/urls.py.backup \
   /etc/morphle/code/morpheus/django_server/api/urls.py
```
