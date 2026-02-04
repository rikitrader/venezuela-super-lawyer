# Venezuela Super Lawyer - Security Stack Profile

## Stack Classification: PYTHON_FASTAPI_FILESYSTEM

**Generated:** 2026-02-04
**Version:** 2.0.0
**Risk Tolerance:** Medium (fail CI on High+)

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Python | 3.8+ |
| Web Framework | FastAPI | >=0.100.0 |
| ASGI Server | Uvicorn | >=0.23.0 |
| Data Validation | Pydantic | >=2.0.0 |
| Storage | File System | JSON/Markdown |
| HTTP Client | requests/urllib | >=2.31.0 |
| ML (optional) | scikit-learn | >=1.3.0 |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL CLIENTS                            │
│         (curl, browsers, API consumers)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS (recommended)
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI APPLICATION                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Auth Layer   │  │ Rate Limiter │  │ CORS Policy  │          │
│  │ (Bearer/Key) │  │ (In-memory)  │  │ (Open *)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    API ENDPOINTS                            │ │
│  │  /health  /status  /analyze  /tsj/*  /gaceta/*  /reports/* │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   17 MODULES  │   │  FILE STORAGE │   │ EXTERNAL APIs │
│ constitutional│   │  cases/*.json │   │ gaceta.gob.ve │
│ tsj_search    │   │  reportes/*.md│   │ tsj.gob.ve    │
│ law_generator │   │  cache/*.json │   │ (rate limited)│
│ etc...        │   │  logs/audit   │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## Authentication & Authorization

### API Authentication

| Method | Status | Notes |
|--------|--------|-------|
| Bearer Token | Implemented | Via `Authorization: Bearer <token>` |
| X-API-Key Header | Implemented | Alternative auth method |
| Environment Variable | Implemented | `VSL_API_KEY` for default |

### Access Control

| Feature | Status | Notes |
|---------|--------|-------|
| File-level protection | Implemented | `security.py` with patterns |
| Password hashing | Implemented | SHA-256 |
| Audit logging | Implemented | `logs/audit.log` |
| RBAC | Partial | tier-based (standard/premium) |

### Current Issues Identified

1. **CORS Policy Too Permissive**: `allow_origins=["*"]`
2. **In-memory API Keys**: Not persistent, lost on restart
3. **In-memory Rate Limits**: Not persistent, lost on restart
4. **Default Dev Hash Hardcoded**: In security.py line 30

---

## Data Flow Security Points

### Input Points (Attack Surface)

1. **API Request Bodies** - JSON payloads to endpoints
2. **Query Parameters** - URL query strings
3. **Path Parameters** - Case names, report filenames
4. **Headers** - API keys, auth tokens

### Output Points

1. **JSON Responses** - Analysis results, reports
2. **File Content** - Markdown reports, JSON data
3. **Error Messages** - Stack traces (potential info leak)

### External Connections

1. **Gaceta Oficial API** - `gaceta.gob.ve`
2. **TSJ API** - `tsj.gob.ve`
3. **Asamblea Nacional** - `asambleanacional.gob.ve`

---

## Critical Flows Identified

| Flow | Risk Level | Auth Required | Notes |
|------|------------|---------------|-------|
| `/analyze` | HIGH | Yes | Full case analysis, file writes |
| `/tsj/predict` | MEDIUM | Yes | ML prediction, data processing |
| `/reports/generate` | HIGH | Yes | File creation in reportes_legales/ |
| `/gaceta/verify` | MEDIUM | Yes | External API calls |
| `/law/generate` | HIGH | Yes | Legal document generation |
| `/health` | LOW | No | Public endpoint |

---

## File System Access Patterns

### Write Operations

```python
# Locations where files are written:
cases/{case_name}/*.json         # Case data
reportes_legales/*.md            # Generated reports
cache/*.json                     # Cached API responses
logs/audit.log                   # Security audit log
```

### Read Operations

```python
# Locations where files are read:
cases/{case_name}/*.json         # Case intake, analysis
references/*.md                  # Legal references
assets/templates/*.md            # Report templates
scripts/*.py                     # Module imports
```

### Path Traversal Risk Points

- `case_name` parameter in multiple endpoints
- `filename` parameter in report endpoints
- Template file loading

---

## Dependencies Security Status

### Core Dependencies

| Package | Version | CVE Status | Notes |
|---------|---------|------------|-------|
| fastapi | >=0.100.0 | Check Required | Web framework |
| uvicorn | >=0.23.0 | Check Required | ASGI server |
| pydantic | >=2.0.0 | Check Required | Validation |
| requests | >=2.31.0 | Check Required | HTTP client |

### Optional Dependencies

| Package | Version | CVE Status | Notes |
|---------|---------|------------|-------|
| scikit-learn | >=1.3.0 | Check Required | ML predictions |
| numpy | >=1.24.0 | Check Required | Numerical ops |
| weasyprint | >=59.0 | Check Required | PDF generation |

---

## Environment Variables

| Variable | Purpose | Sensitive | Required |
|----------|---------|-----------|----------|
| VSL_API_KEY | Default API key | YES | No (dev only) |
| VSL_ACCESS_KEY | Protected file access | YES | Production |
| VSL_PASSWORD_HASH | Auth hash | YES | Production |
| PYTHONPATH | Module resolution | No | Optional |

---

## Threat Model Summary

### High Priority Threats

1. **Path Traversal** - Via case_name/filename parameters
2. **SSRF** - Via external API connections
3. **Information Disclosure** - Error messages, file content
4. **DoS** - Unbounded file operations, ML predictions

### Medium Priority Threats

1. **Authentication Bypass** - Default API key fallback
2. **Rate Limit Bypass** - In-memory storage reset
3. **CORS Exploitation** - Overly permissive policy

### Low Priority Threats

1. **Log Injection** - Via audit log writes
2. **Cache Poisoning** - Via cached API responses
