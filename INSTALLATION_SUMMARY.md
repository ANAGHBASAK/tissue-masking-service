# Installation Summary

## Quick Reference Card

### Automated Steps (Run Script)

```bash
cd /tmp/tissue-masking-service
export MORPHEUS_ROOT=/etc/morphle/code/morpheus
./scripts/merge_into_morpheus.sh
```

**Time: 2 minutes**

### Manual Steps (Required)

#### 1. Edit `django_server/api/urls.py` - Add Imports

**Location:** Around line 20

```python
from api.views.tissue_views import (
    tissue_mask_view,
    tissue_mask_batch_view,
    get_pipeline_status_view
)
from api.views.health_views import health_check_view
```

#### 2. Edit `django_server/api/urls.py` - Add URL Patterns

**Location:** Around line 327 (before `if os.environ.get('DEPLOYMENT_MODE')`)

```python
    path('tissue/mask/', tissue_mask_view, name='tissue-mask'),
    path('tissue/mask/batch/', tissue_mask_batch_view, name='tissue-mask-batch'),
    path('tissue/status/', get_pipeline_status_view, name='pipeline-status'),
```

#### 3. Verify OpenCV

```bash
python3 -c "import cv2; print('OK')" || pip install opencv-python
```

**Time: 5 minutes**

### Verification Steps

```bash
# Test imports
cd /etc/morphle/code/morpheus/django_server
python manage.py shell
>>> from morpho.commons.tissue_masking.pipeline import TissueMaskingPipeline
>>> exit()

# Test endpoint
curl http://localhost:8000/api/v1/health/
```

**Time: 3 minutes**

---

## Complete Checklist

- [ ] Run merge script: `./scripts/merge_into_morpheus.sh`
- [ ] Add imports to `urls.py` (Step 1 above)
- [ ] Add URL patterns to `urls.py` (Step 2 above)
- [ ] Verify OpenCV: `python3 -c "import cv2"`
- [ ] Test imports in Django shell
- [ ] Test health endpoint: `curl http://localhost:8000/api/v1/health/`
- [ ] Test tissue mask endpoint with test image

---

## File Locations After Merge

```
morpheus/
├── django_server/api/
│   ├── urls.py                    ← Edit this (add imports + URLs)
│   └── views/
│       ├── tissue_views.py        ← Copied automatically
│       └── health_views.py        ← Copied automatically
│
└── src/morpho/commons/
    └── tissue_masking/            ← Copied automatically
        ├── pipeline.py
        ├── od.py
        ├── stain.py
        └── ... (all modules)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Import error | Check Python path includes `src/` |
| OpenCV missing | `pip install opencv-python` |
| URL 404 | Verify URLs added to `urls.py` |
| Django error | Check `api` in `INSTALLED_APPS` |

---

## Documentation Files

- **INSTALLATION_STEPS.md** - Detailed step-by-step guide
- **MERGE_GUIDE.md** - Complete merge guide with troubleshooting
- **QUICKSTART.md** - Standalone usage guide
- **README.md** - Overview and features

---

## Support

For detailed instructions, see:
- `INSTALLATION_STEPS.md` - Quick reference
- `MERGE_GUIDE.md` - Complete guide with troubleshooting
