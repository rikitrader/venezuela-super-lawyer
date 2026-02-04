# Contributing to Venezuela Super Lawyer

Thank you for your interest in contributing to the Venezuela Super Lawyer skill! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Adding New Features](#adding-new-features)
- [Submitting Changes](#submitting-changes)
- [Legal Database Updates](#legal-database-updates)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Maintain professional discourse
- Prioritize accuracy in legal content
- Respect confidentiality of legal matters

### Unacceptable Behavior

- Harassment or discriminatory language
- Sharing confidential legal information
- Intentionally misleading legal content
- Plagiarism of legal documents

---

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Basic understanding of Venezuelan law (for legal contributions)
- Familiarity with Claude Code skills

### Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/venezuela-super-lawyer.git
cd venezuela-super-lawyer
```

---

## Development Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
export VSL_ACCESS_KEY=your-development-key
```

### 4. Verify Installation

```bash
# Run tests
pytest tests/ -v

# Check syntax
python3 -m py_compile scripts/*.py
```

---

## Project Structure

```
venezuela-super-lawyer/
├── SKILL.md                 # Main skill documentation (17 modules)
├── README.md                # Project overview
├── CONTRIBUTING.md          # This file
├── LICENSE                  # Proprietary license
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
│
├── scripts/                 # Python modules (11 files)
│   ├── constitution_diff.py     # Constitutional conflict analysis
│   ├── constitutional_test.py   # Automated compliance tests
│   ├── gaceta_verify.py         # Gaceta Oficial verification
│   ├── gaceta_scraper.py        # Web scraper for Gaceta
│   ├── tsj_search.py            # TSJ jurisprudence search
│   ├── tsj_scraper.py           # Web scraper for TSJ
│   ├── voting_map.py            # Legislative voting analysis
│   ├── report_manager.py        # Report generation
│   ├── init_case.py             # Case initialization
│   ├── security.py              # Authentication module
│   ├── exceptions.py            # Custom exception classes
│   └── export_documents.py      # PDF/DOCX export
│
├── references/              # Reference documentation (7 files)
│   ├── crbv_articles.md         # Constitutional articles
│   ├── tsj_salas.md             # TSJ chambers guide
│   ├── hydrocarbons_framework.md
│   ├── legal_terminology.md
│   ├── gaceta_guide.md
│   ├── legislative_avenues.md
│   └── cli_guide.md
│
├── assets/
│   └── templates/           # Legal document templates (8 files)
│
├── tests/                   # Unit tests (7 files)
│
├── reportes_legales/        # Generated reports
├── cases/                   # Case files
├── logs/                    # Audit logs
└── cache/                   # Scraper cache
```

---

## Coding Standards

### Python Style Guide

We follow PEP 8 with these specifics:

```python
# Maximum line length: 120 characters
# Use 4 spaces for indentation (no tabs)
# Use docstrings for all public functions

def my_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of the function.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
    """
    pass
```

### Type Hints

All functions should have type hints:

```python
from typing import List, Optional, Dict, Any

def search_norms(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    ...
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `gaceta_verify.py` |
| Classes | PascalCase | `ConstitutionalArticle` |
| Functions | snake_case | `search_articles()` |
| Constants | UPPER_SNAKE | `MAX_RESULTS` |
| Enums | PascalCase + UPPER | `SalaTSJ.CONSTITUCIONAL` |

### Code Comments

```python
# Spanish for legal content
# Artículo 49 - Debido Proceso

# English for technical comments
# This function implements caching for performance

# TODO format
# TODO(username): Description of task

# FIXME format
# FIXME: This needs error handling for edge case X
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_gaceta_verify.py -v

# Run with coverage
pytest tests/ --cov=scripts --cov-report=term-missing

# Run only fast tests
pytest tests/ -v -m "not slow"
```

### Writing Tests

```python
# tests/test_my_module.py

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from my_module import my_function


class TestMyFunction(unittest.TestCase):
    """Test cases for my_function."""

    def test_basic_case(self):
        """Test basic functionality."""
        result = my_function("input")
        self.assertEqual(result, "expected")

    def test_edge_case(self):
        """Test edge case handling."""
        result = my_function("")
        self.assertIsNone(result)

    def test_error_handling(self):
        """Test exception is raised for invalid input."""
        with self.assertRaises(ValueError):
            my_function(None)


if __name__ == '__main__':
    unittest.main()
```

### Test Requirements

- All new features must have tests
- Minimum 80% code coverage for new code
- Tests must pass before merging
- Use mocks for external dependencies (HTTP, file system)

---

## Adding New Features

### 1. Create a Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Implement the Feature

1. Add code to appropriate script in `scripts/`
2. Add version tracking: `__version__ = "1.0.0"`
3. Add type hints and docstrings
4. Handle errors with custom exceptions from `exceptions.py`

### 3. Add Tests

Create `tests/test_my_feature.py` with comprehensive tests.

### 4. Update Documentation

- Update `SKILL.md` if adding a new module
- Update `references/cli_guide.md` if adding CLI commands
- Add docstrings to all public functions

### 5. Run Quality Checks

```bash
# Lint
flake8 scripts/ --max-line-length=120

# Format
black scripts/ --line-length=120

# Type check
mypy scripts/

# Tests
pytest tests/ -v
```

---

## Submitting Changes

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Example:**

```
feat(voting_map): add referendum requirement detection

Implemented detection of referendum requirements for constitutional
amendments and reforms based on CRBV Articles 340-350.

Closes #123
```

### Pull Request Process

1. Update CHANGELOG if applicable
2. Ensure all tests pass
3. Update documentation
4. Request review from maintainers
5. Address feedback
6. Squash commits if requested

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Database update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

---

## Legal Database Updates

### Adding Constitutional Articles

Edit `scripts/constitution_diff.py`:

```python
CONSTITUTIONAL_ARTICLES[NEW_NUMBER] = ConstitutionalArticle(
    numero=NEW_NUMBER,
    titulo="Título del Artículo",
    capitulo="Capítulo correspondiente",
    contenido="Texto completo del artículo...",
    area=ConstitutionalArea.APPROPRIATE_AREA,
    keywords=["palabra1", "palabra2"],
    is_eternity_clause=False,  # True if cláusula pétrea
    requires_organic_law=False
)
```

### Adding TSJ Cases

Edit `scripts/tsj_search.py`:

```python
JURISPRUDENCIA_DATABASE.append(CasoTSJ(
    sala=SalaTSJ.APPROPRIATE_SALA,
    numero_expediente="XX-XXXX",
    numero_sentencia="XXXX",
    fecha="DD-MM-YYYY",
    tipo=TipoDecision.SENTENCIA,
    ponente="Nombre del Magistrado",
    partes="Parte A vs Parte B",
    materia="Materia del caso",
    resumen="Resumen del caso...",
    ratio_decidendi="Ratio decidendi...",
    articulos_crbv=["49", "26"],
    precedentes_citados=[],
    vinculante=False,  # True if binding precedent
    url="http://...",
    keywords=["keyword1", "keyword2"]
))
```

### Adding Gaceta Norms

Edit `scripts/gaceta_verify.py`:

```python
KNOWN_NORMS["ACRONYM"] = KnownNorm(
    key="ACRONYM",
    name="Nombre Completo de la Ley",
    norm_type=NormType.LEY_ORGANICA,
    gaceta_number="X.XXX",
    gaceta_type=GacetaType.EXTRAORDINARIA,
    publication_date="DD-MM-YYYY",
    status=NormStatus.VIGENTE,
    description="Descripción breve...",
    keywords=["keyword1", "keyword2"],
    related_norms=["OTHER_ACRONYM"]
)
```

### Verification Requirements

All legal database updates must:

1. Cite official sources (Gaceta Oficial, TSJ website)
2. Include accurate publication dates
3. Use correct legal terminology
4. Be reviewed for accuracy before merging

---

## Questions?

- Open an issue for bug reports
- Start a discussion for feature requests
- Contact maintainers for sensitive legal matters

---

## License

By contributing, you agree that your contributions will be licensed under the project's proprietary license.

---

*Thank you for contributing to Venezuela Super Lawyer!*
