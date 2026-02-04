# Venezuela Super Lawyer - Installation Guide

## Quick Start

### 1. Clone/Download

```bash
# The skill is located at:
~/.claude/skills/venezuela-super-lawyer/
```

### 2. Verify Python Version

```bash
python3 --version
# Required: Python 3.8+
```

### 3. Install Dependencies (Optional)

```bash
cd ~/.claude/skills/venezuela-super-lawyer

# Minimal (recommended)
pip install pydantic requests

# Full installation
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python3 -m pytest tests/ -q
# Expected: 281 passed, 4 skipped
```

---

## Installation Profiles

### Profile 1: Minimal (No External Dependencies)

**Best for:** Quick testing, basic usage

```bash
# No installation needed - uses Python standard library only
python3 scripts/run_case_analysis.py "Test_Case" --workflow CASE_ANALYSIS
```

**Available features:**
- Constitutional analysis
- TSJ search (local database)
- Gaceta verification (local database)
- Voting map generation
- Law generation
- Contract review
- Hydrocarbons analysis
- Report generation

---

### Profile 2: Standard (Recommended)

**Best for:** Regular usage with enhanced features

```bash
pip install pydantic requests
```

**Additional features:**
- Validated data models
- Live data from external sources
- Better error messages

---

### Profile 3: Full (All Features)

**Best for:** Production deployment, API access

```bash
pip install -r requirements.txt
```

**Additional features:**
- REST API server
- ML-based TSJ predictions
- PDF/DOCX export
- Async data fetching

---

### Profile 4: Development

**Best for:** Contributing, testing

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio
python3 -m pytest tests/ -v
```

---

## Platform-Specific Instructions

### macOS

```bash
# Install Python 3.10+ if needed
brew install python@3.10

# Install dependencies
pip3 install -r requirements.txt

# WeasyPrint requires additional libraries
brew install pango gdk-pixbuf libffi
```

### Ubuntu/Debian

```bash
# Install Python 3.10+ if needed
sudo apt update
sudo apt install python3.10 python3-pip

# Install dependencies
pip3 install -r requirements.txt

# WeasyPrint requires additional libraries
sudo apt install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

### Windows

```bash
# Install Python from python.org
# Ensure "Add to PATH" is checked during installation

# Install dependencies
pip install -r requirements.txt
```

---

## Starting the REST API

### Development Mode

```bash
cd ~/.claude/skills/venezuela-super-lawyer
python3 scripts/api.py --port 8000 --reload

# Access:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Production Mode

```bash
# Using gunicorn
pip install gunicorn
cd scripts
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

```bash
# Set API key for authentication
export VSL_API_KEY="your-secure-api-key"

# Set access key for protected operations
export VSL_ACCESS_KEY="your-access-key"
```

---

## Troubleshooting

### Import Errors

```bash
# If you see "ModuleNotFoundError"
cd ~/.claude/skills/venezuela-super-lawyer
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"
```

### WeasyPrint Issues (macOS)

```bash
# If PDF export fails
brew install pango gdk-pixbuf libffi cairo
pip install --force-reinstall weasyprint
```

### Permission Errors

```bash
# Ensure write access to cases/ and reportes_legales/
chmod 755 cases reportes_legales
```

### SSL Warnings

```bash
# If you see LibreSSL warnings, they can be safely ignored
# Or upgrade OpenSSL:
brew install openssl
```

---

## Verification Commands

### Check All Modules

```bash
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from run_case_analysis import MODULES_AVAILABLE
available = sum(1 for v in MODULES_AVAILABLE.values() if v)
print(f'Modules: {available}/{len(MODULES_AVAILABLE)}')
for mod, avail in MODULES_AVAILABLE.items():
    print(f'  {mod}: {\"OK\" if avail else \"MISSING\"}')"
```

### Run Tests

```bash
python3 -m pytest tests/ -v --tb=short
```

### Test API

```bash
# Start API in one terminal
python3 scripts/api.py

# Test in another terminal
curl http://localhost:8000/health
curl http://localhost:8000/status -H "Authorization: Bearer your-api-key"
```

### Test TSJ Predictor

```bash
python3 scripts/tsj_predictor.py --predict "Despido injustificado" --area laboral
```

### Test Live Data

```bash
python3 scripts/live_data.py --search "hidrocarburos" --stats
```
