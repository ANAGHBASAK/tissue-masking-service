#!/bin/bash
# Script to merge tissue-masking-service into morpheus
# This script handles automated steps. Manual steps are documented in MERGE_GUIDE.md

set -e

MORPHEUS_ROOT="${MORPHEUS_ROOT:-/etc/morphle/code/morpheus}"
TISSUE_SERVICE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================="
echo "Merging tissue-masking-service into morpheus"
echo "=========================================="
echo "Morpheus root: $MORPHEUS_ROOT"
echo "Tissue service root: $TISSUE_SERVICE_ROOT"
echo ""

# Check if morpheus root exists
if [ ! -d "$MORPHEUS_ROOT" ]; then
    echo "ERROR: Morpheus root directory not found: $MORPHEUS_ROOT"
    echo "Set MORPHEUS_ROOT environment variable or edit this script"
    exit 1
fi

# Check if morpheus has Django structure
if [ ! -d "$MORPHEUS_ROOT/django_server" ]; then
    echo "ERROR: Django server directory not found in morpheus"
    echo "Expected: $MORPHEUS_ROOT/django_server"
    exit 1
fi

# ==========================================
# AUTOMATED STEP 1: Copy pipeline library
# ==========================================
echo "[1/5] Copying pipeline library..."
mkdir -p "$MORPHEUS_ROOT/src/morpho/commons/tissue_masking"
cp -r "$TISSUE_SERVICE_ROOT/pipeline"/* "$MORPHEUS_ROOT/src/morpho/commons/tissue_masking/"
echo "  ✓ Copied pipeline modules to src/morpho/commons/tissue_masking/"

# ==========================================
# AUTOMATED STEP 2: Copy API views
# ==========================================
echo "[2/5] Copying API views..."
cp "$TISSUE_SERVICE_ROOT/api/views/tissue_views.py" "$MORPHEUS_ROOT/django_server/api/views/"
cp "$TISSUE_SERVICE_ROOT/api/views/health_views.py" "$MORPHEUS_ROOT/django_server/api/views/"
echo "  ✓ Copied tissue_views.py and health_views.py"

# ==========================================
# AUTOMATED STEP 3: Update imports in tissue_views.py
# ==========================================
echo "[3/5] Updating imports in tissue_views.py..."
TISSUE_VIEWS_FILE="$MORPHEUS_ROOT/django_server/api/views/tissue_views.py"

if [ -f "$TISSUE_VIEWS_FILE" ]; then
    # Update imports to use morpheus paths
    sed -i 's|from pipeline\.|from morpho.commons.tissue_masking.|g' "$TISSUE_VIEWS_FILE"
    echo "  ✓ Updated imports to use morpho.commons.tissue_masking paths"
else
    echo "  ✗ WARNING: tissue_views.py not found, skipping import update"
fi

# ==========================================
# AUTOMATED STEP 4: Copy configs
# ==========================================
echo "[4/5] Copying configuration files..."
mkdir -p "$MORPHEUS_ROOT/configs/tissue_masking"
cp -r "$TISSUE_SERVICE_ROOT/configs"/* "$MORPHEUS_ROOT/configs/tissue_masking/"
echo "  ✓ Copied configuration files"

# ==========================================
# AUTOMATED STEP 5: Update requirements.txt
# ==========================================
echo "[5/5] Updating requirements.txt..."
REQUIREMENTS_FILE="$MORPHEUS_ROOT/requirements.txt"
NEW_REQUIREMENTS="$TISSUE_SERVICE_ROOT/requirements.txt"

# Check if opencv-python is needed
if ! grep -q "opencv-python" "$REQUIREMENTS_FILE" 2>/dev/null; then
    echo "  ⚠ opencv-python not found in morpheus requirements.txt"
    echo "  ⚠ Checking if cv2 is available..."
    if python3 -c "import cv2" 2>/dev/null; then
        echo "  ✓ cv2 is available (likely system-installed)"
    else
        echo "  ✗ WARNING: cv2 not available. You may need to install opencv-python"
        echo "    Run: pip install opencv-python"
    fi
fi

# Append new dependencies (avoid duplicates)
if [ -f "$REQUIREMENTS_FILE" ]; then
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ ! "$line" =~ ^# ]] && [ ! -z "$line" ]; then
            # Extract package name (before == or >= or <=)
            pkg_name=$(echo "$line" | sed 's/[<>=].*//' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
            if [ ! -z "$pkg_name" ]; then
                # Check if package already exists (case-insensitive)
                if ! grep -qi "^${pkg_name}" "$REQUIREMENTS_FILE" 2>/dev/null; then
                    echo "$line" >> "$REQUIREMENTS_FILE"
                    echo "  + Added: $line"
                else
                    echo "  - Skipped (already exists): $pkg_name"
                fi
            fi
        fi
    done < "$NEW_REQUIREMENTS"
else
    echo "  ✗ WARNING: requirements.txt not found in morpheus root"
fi

echo ""
echo "=========================================="
echo "AUTOMATED STEPS COMPLETE!"
echo "=========================================="
echo ""
echo "MANUAL STEPS REQUIRED:"
echo ""
echo "1. Add imports to django_server/api/urls.py"
echo "   Add these lines near the top with other imports:"
echo ""
echo "   from api.views.tissue_views import ("
echo "       tissue_mask_view,"
echo "       tissue_mask_batch_view,"
echo "       get_pipeline_status_view"
echo "   )"
echo "   from api.views.health_views import health_check_view"
echo ""
echo "2. Add URL patterns to django_server/api/urls.py"
echo "   Add these lines before the closing bracket of urlpatterns:"
echo ""
echo "   path('tissue/mask/', tissue_mask_view, name='tissue-mask'),"
echo "   path('tissue/mask/batch/', tissue_mask_batch_view, name='tissue-mask-batch'),"
echo "   path('tissue/status/', get_pipeline_status_view, name='pipeline-status'),"
echo ""
echo "3. Verify OpenCV is installed"
echo "   Run: python3 -c 'import cv2; print(\"OpenCV version:\", cv2.__version__)'"
echo "   If it fails, install: pip install opencv-python"
echo ""
echo "4. Run Django migrations (if using models)"
echo "   cd $MORPHEUS_ROOT/django_server"
echo "   python manage.py makemigrations api"
echo "   python manage.py migrate"
echo ""
echo "5. Test the endpoints"
echo "   See MERGE_GUIDE.md for testing instructions"
echo ""
echo "For detailed instructions, see: MERGE_GUIDE.md"
echo "=========================================="
