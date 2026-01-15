# Repository Structure

Complete tissue-masking-service repository structure.

## Directory Tree

```
tissue-masking-service/
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Quick start guide
├── MERGE_GUIDE.md                     # Guide for merging into morpheus
├── STRUCTURE.md                       # This file
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── Dockerfile                         # Docker container definition
├── compose.yaml                       # Docker Compose configuration
│
├── tissue_service/                    # Django project root
│   ├── __init__.py
│   ├── manage.py                      # Django management script
│   ├── wsgi.py                        # WSGI application
│   └── tissue_service/                # Django settings package
│       ├── __init__.py
│       ├── settings.py                # Django settings (env-driven)
│       ├── urls.py                     # Root URL configuration
│       └── wsgi.py                     # WSGI config
│
├── api/                               # Django API app
│   ├── __init__.py
│   ├── apps.py                        # App configuration
│   ├── admin.py                       # Django admin
│   ├── models.py                      # Database models (optional)
│   ├── serializers.py                 # Request/response serializers
│   ├── urls.py                        # API URL routing
│   └── views/                         # View layer (Controllers)
│       ├── __init__.py
│       ├── tissue_views.py            # Main tissue masking endpoints
│       └── health_views.py             # Health check endpoint
│
├── pipeline/                          # Core processing library
│   ├── __init__.py
│   ├── io.py                          # Image I/O utilities
│   ├── preprocess.py                  # Flat-field correction
│   ├── od.py                          # Optical Density transformation
│   ├── stain.py                       # Macenko stain estimation
│   ├── normalize.py                   # Stain normalization
│   ├── threshold.py                   # Adaptive thresholding
│   ├── morphology.py                  # Morphological cleanup
│   ├── metrics.py                     # QC metrics computation
│   └── pipeline.py                   # Main orchestrator
│
├── configs/                           # Configuration files
│   ├── pipeline_defaults.yaml        # Default pipeline parameters
│   └── reference_stain_profiles/     # Reference stain profiles
│       ├── he_reference.json         # H&E reference (placeholder)
│       ├── ihc_reference.json        # IHC reference (placeholder)
│       └── pap_reference.json        # PAP reference (placeholder)
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_pipeline.py              # Pipeline unit tests
│   ├── test_api.py                   # API contract tests
│   ├── test_integration.py           # End-to-end tests
│   └── fixtures/                     # Test images
│       └── .gitkeep
│
└── scripts/                           # Utility scripts
    ├── merge_into_morpheus.sh        # Merge script for morpheus
    └── setup_reference_profiles.py   # Generate reference profiles
```

## File Count

- **Total files**: 44
- **Python files**: ~30
- **Configuration files**: 4
- **Documentation files**: 4
- **Scripts**: 2

## Key Components

### 1. Pipeline Modules (`pipeline/`)

- **od.py**: Optical Density transformation (RGB → OD)
- **stain.py**: Macenko stain vector estimation
- **normalize.py**: Stain concentration normalization
- **threshold.py**: Adaptive thresholding (Otsu/Sauvola/Auto)
- **morphology.py**: Morphological cleanup
- **metrics.py**: QC metrics and statistics
- **pipeline.py**: Main orchestrator class

### 2. API Layer (`api/`)

- **views/tissue_views.py**: Main endpoint handlers
- **views/health_views.py**: Health check endpoint
- **serializers.py**: Request/response validation
- **models.py**: Optional database models
- **urls.py**: URL routing

### 3. Configuration (`configs/`)

- **pipeline_defaults.yaml**: Default parameters
- **reference_stain_profiles/**: Reference distributions for normalization

### 4. Tests (`tests/`)

- Unit tests for each pipeline module
- API contract tests
- Integration tests

## Usage

See `QUICKSTART.md` for usage instructions.

## Merging into Morpheus

See `MERGE_GUIDE.md` for detailed merge instructions.

## Dependencies

See `requirements.txt` for complete list. Key dependencies:
- Django 3.2+
- NumPy
- OpenCV
- scikit-image
- SciPy
