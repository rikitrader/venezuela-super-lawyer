# Venezuela Super Lawyer - Requirements

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8+ | 3.10+ |
| RAM | 512 MB | 2 GB |
| Disk Space | 50 MB | 100 MB |
| OS | macOS, Linux, Windows | Any |

---

## Python Dependencies

### Core (Required)

These are part of Python's standard library and require no installation:

| Module | Used For |
|--------|----------|
| `dataclasses` | Data structures |
| `typing` | Type hints |
| `pathlib` | File paths |
| `json` | JSON serialization |
| `re` | Regular expressions |
| `datetime` | Date/time handling |
| `enum` | Enumerations |
| `hashlib` | Hashing |
| `secrets` | Secure tokens |
| `urllib` | HTTP fallback |

---

### Optional Dependencies

Install optional dependencies based on your needs:

#### Data Validation (Recommended)

```bash
pip install pydantic>=2.0.0
```

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| `pydantic` | >=2.0.0 | `models.py` | Data validation, schema generation |

#### REST API

```bash
pip install fastapi uvicorn
```

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| `fastapi` | >=0.100.0 | `api.py` | REST API framework |
| `uvicorn` | >=0.23.0 | `api.py` | ASGI server |

#### Machine Learning (TSJ Prediction)

```bash
pip install scikit-learn numpy
```

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| `scikit-learn` | >=1.3.0 | `tsj_predictor.py` | ML classification |
| `numpy` | >=1.24.0 | `tsj_predictor.py` | Numerical operations |

#### HTTP Requests

```bash
pip install requests
```

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| `requests` | >=2.31.0 | `live_data.py` | HTTP client |
| `aiohttp` | >=3.8.0 | `live_data.py` | Async HTTP (optional) |

#### Document Export

```bash
pip install weasyprint python-docx
```

| Package | Version | Used By | Purpose |
|---------|---------|---------|---------|
| `weasyprint` | >=59.0 | `export_documents.py` | PDF generation |
| `python-docx` | >=0.8.11 | `export_documents.py` | DOCX generation |

#### Testing

```bash
pip install pytest pytest-asyncio
```

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >=7.0.0 | Test framework |
| `pytest-asyncio` | >=0.21.0 | Async test support |

---

## Installation Options

### Minimal Installation (Core Only)

No additional packages needed. Works with Python standard library only.

```bash
# Just clone and run
python3 scripts/run_case_analysis.py --help
```

### Standard Installation (Recommended)

```bash
pip install pydantic requests
```

### Full Installation (All Features)

```bash
pip install -r requirements.txt
```

### Development Installation

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio
```

---

## Module Dependencies Matrix

| Module | pydantic | fastapi | sklearn | requests | weasyprint |
|--------|:--------:|:-------:|:-------:|:--------:|:----------:|
| `models.py` | ✓ | - | - | - | - |
| `api.py` | ✓ | ✓ | - | - | - |
| `tsj_predictor.py` | - | - | ✓ | - | - |
| `live_data.py` | - | - | - | ✓ | - |
| `export_documents.py` | - | - | - | - | ✓ |
| `run_case_analysis.py` | - | - | - | - | - |
| `constitution_diff.py` | - | - | - | - | - |
| `constitutional_test.py` | - | - | - | - | - |
| `gaceta_verify.py` | - | - | - | - | - |
| `tsj_search.py` | - | - | - | - | - |
| `voting_map.py` | - | - | - | - | - |
| `law_generator.py` | - | - | - | - | - |
| `hydrocarbons_playbook.py` | - | - | - | - | - |
| `contract_review.py` | - | - | - | - | - |
| `report_manager.py` | - | - | - | - | - |

**Legend:** ✓ = Required, - = Not needed

---

## Graceful Degradation

All modules are designed with graceful fallbacks:

| Missing Package | Behavior |
|-----------------|----------|
| `pydantic` | Uses dataclasses instead |
| `fastapi` | API module disabled, CLI still works |
| `sklearn` | TSJ prediction uses heuristics only |
| `requests` | Uses urllib fallback |
| `weasyprint` | PDF export disabled |
| `python-docx` | DOCX export disabled |

---

## Verification

Check installed dependencies:

```bash
python3 -c "
import sys
print(f'Python: {sys.version}')

deps = ['pydantic', 'fastapi', 'uvicorn', 'sklearn', 'numpy', 'requests', 'aiohttp', 'weasyprint', 'docx']
for dep in deps:
    try:
        __import__(dep)
        print(f'{dep}: OK')
    except ImportError:
        print(f'{dep}: Not installed')
"
```

Check module availability:

```bash
cd /path/to/venezuela-super-lawyer
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from run_case_analysis import MODULES_AVAILABLE
for mod, avail in MODULES_AVAILABLE.items():
    status = 'OK' if avail else 'MISSING'
    print(f'{mod}: {status}')
"
```
