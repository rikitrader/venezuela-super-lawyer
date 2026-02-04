# Venezuela Super Lawyer - API Reference

## Overview

The REST API provides programmatic access to all Venezuela Super Lawyer functionality. Built with FastAPI, it offers automatic OpenAPI documentation, request validation, and async support.

---

## Quick Start

### Starting the Server

```bash
cd ~/.claude/skills/venezuela-super-lawyer

# Development mode (with auto-reload)
python3 scripts/api.py --port 8000 --reload

# Production mode
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Base URL

```
http://localhost:8000
```

### Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Authentication

### API Key Authentication

Include your API key in one of these headers:

```bash
# Bearer token
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8000/status

# X-API-Key header
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/status
```

### Environment Variables

```bash
export VSL_API_KEY="your-secure-api-key"
export VSL_ACCESS_KEY="your-access-key"  # For protected operations
```

### Rate Limits

| Tier | Limit |
|------|-------|
| Standard | 100 requests/hour |
| Premium | 1,000 requests/hour |

---

## Endpoints

### System Endpoints

#### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Status

```http
GET /status
```

**Headers:** `Authorization: Bearer <API_KEY>`

**Response:**
```json
{
  "status": "operational",
  "version": "2.0.0",
  "modules_available": {
    "constitutional_test": true,
    "tsj_search": true,
    "gaceta_verify": true,
    "voting_map": true,
    "law_generator": true,
    "contract_review": true,
    "hydrocarbons_playbook": true,
    "report_manager": true,
    "tsj_predictor": true,
    "live_data": true,
    "models": true
  },
  "cases_count": 5,
  "reports_count": 12
}
```

---

### Case Analysis

#### Run Full Analysis

```http
POST /analyze
```

**Headers:** `Authorization: Bearer <API_KEY>`

**Request Body:**
```json
{
  "case_name": "Case_001",
  "workflow": "CASE_ANALYSIS",
  "facts": "Description of the case facts...",
  "legal_area": "laboral",
  "options": {
    "include_tsj_prediction": true,
    "include_constitutional_analysis": true,
    "include_recommendations": true
  }
}
```

**Response:**
```json
{
  "case_id": "Case_001",
  "workflow": "CASE_ANALYSIS",
  "timestamp": "2024-01-15T10:30:00Z",
  "analysis": {
    "constitutional": {...},
    "tsj_search": {...},
    "prediction": {...},
    "recommendations": [...]
  },
  "report_path": "reportes_legales/Case_001_analysis.md"
}
```

#### List Cases

```http
GET /cases
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 50 | Maximum results |
| `offset` | int | 0 | Pagination offset |

**Response:**
```json
{
  "cases": ["Case_001", "Case_002", "Case_003"],
  "total": 3
}
```

#### Get Case Details

```http
GET /cases/{case_name}
```

**Response:**
```json
{
  "name": "Case_001",
  "created": "2024-01-15T10:30:00Z",
  "files": ["intake.json", "analysis.json"],
  "status": "completed"
}
```

---

### Constitutional Analysis

#### Test Constitutionality

```http
POST /constitutional/test
```

**Request Body:**
```json
{
  "norm_text": "Text of the norm to analyze...",
  "norm_type": "LEY",
  "articles_to_check": [19, 21, 89, 112]
}
```

**Response:**
```json
{
  "is_constitutional": false,
  "violations": [
    {
      "article": 89,
      "text": "El trabajo es un hecho social...",
      "violation_type": "direct",
      "explanation": "The norm contradicts labor protections..."
    }
  ],
  "recommendations": [
    "Modify section 3 to align with Article 89..."
  ],
  "confidence": 0.85
}
```

#### Compare Constitutions

```http
GET /constitutional/diff
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `version1` | string | First constitution version (e.g., "1961") |
| `version2` | string | Second constitution version (e.g., "1999") |
| `articles` | string | Comma-separated article numbers (optional) |

**Response:**
```json
{
  "changes": [
    {
      "article": 112,
      "type": "modified",
      "old_text": "...",
      "new_text": "...",
      "analysis": "Economic freedom provisions were expanded..."
    }
  ],
  "summary": {
    "added": 45,
    "removed": 12,
    "modified": 89
  }
}
```

---

### TSJ (Supreme Court)

#### Search Jurisprudence

```http
POST /tsj/search
```

**Request Body:**
```json
{
  "query": "despido injustificado",
  "sala": "CASACION_SOCIAL",
  "date_from": "2020-01-01",
  "date_to": "2024-12-31",
  "limit": 20
}
```

**Response:**
```json
{
  "results": [
    {
      "case_number": "RC-000123",
      "date": "2023-05-15",
      "sala": "CASACION_SOCIAL",
      "summary": "...",
      "relevance_score": 0.92
    }
  ],
  "total": 45,
  "query_time_ms": 125
}
```

#### Predict Outcome

```http
POST /tsj/predict
```

**Request Body:**
```json
{
  "case_facts": "Worker dismissed after 5 years without cause...",
  "legal_area": "laboral",
  "include_similar_cases": true
}
```

**Response:**
```json
{
  "predicted_outcome": "FAVORABLE_DEMANDANTE",
  "confidence": 0.78,
  "factors": [
    {
      "factor": "employment_duration",
      "weight": 0.3,
      "value": "high"
    },
    {
      "factor": "lack_of_just_cause",
      "weight": 0.4,
      "value": "present"
    }
  ],
  "similar_cases": [
    {
      "case_number": "RC-000089",
      "outcome": "FAVORABLE_DEMANDANTE",
      "similarity": 0.85
    }
  ],
  "legal_basis": ["LOTTT Art. 76", "LOTTT Art. 92"]
}
```

---

### Gaceta Oficial

#### Verify Publication

```http
POST /gaceta/verify
```

**Request Body:**
```json
{
  "norm_identifier": "Decreto N° 4.160",
  "expected_date": "2020-03-13",
  "norm_type": "DECRETO"
}
```

**Response:**
```json
{
  "verified": true,
  "gaceta_number": "6.519 Extraordinario",
  "publication_date": "2020-03-13",
  "full_text_available": true,
  "url": "https://..."
}
```

#### Search Gaceta

```http
GET /gaceta/search
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search terms |
| `year` | int | Filter by year |
| `type` | string | Norm type filter |
| `limit` | int | Max results (default: 20) |

**Response:**
```json
{
  "results": [
    {
      "gaceta_number": "6.519 Extraordinario",
      "date": "2020-03-13",
      "title": "Decreto N° 4.160...",
      "type": "DECRETO"
    }
  ],
  "total": 15
}
```

---

### Contract Review

#### Analyze Contract

```http
POST /contracts/review
```

**Request Body:**
```json
{
  "contract_text": "Full contract text...",
  "contract_type": "SERVICIOS",
  "sector": "OIL_GAS",
  "check_options": {
    "constitutional": true,
    "labor_compliance": true,
    "tax_implications": true,
    "currency_regulations": true
  }
}
```

**Response:**
```json
{
  "overall_risk": "MEDIUM",
  "risk_score": 0.45,
  "issues": [
    {
      "clause": "Section 5.2",
      "issue_type": "labor_compliance",
      "severity": "HIGH",
      "description": "Clause may violate LOTTT Art. 89...",
      "recommendation": "Modify to include..."
    }
  ],
  "compliant_areas": ["tax_structure", "corporate_governance"],
  "recommendations": [...]
}
```

---

### Hydrocarbons

#### Analyze Hydrocarbons Project

```http
POST /hydrocarbons/analyze
```

**Request Body:**
```json
{
  "project_description": "Upstream exploration project...",
  "activity_type": "EXPLORACION",
  "participation_structure": {
    "pdvsa_percentage": 60,
    "foreign_percentage": 40
  },
  "contract_type": "EMPRESA_MIXTA"
}
```

**Response:**
```json
{
  "loh_compliance": {
    "compliant": true,
    "article_checks": [
      {"article": 22, "status": "compliant", "notes": "..."}
    ]
  },
  "risk_assessment": {
    "overall_risk": "LOW",
    "factors": [...]
  },
  "required_approvals": [
    "MENPET authorization",
    "Environmental impact study",
    "AN approval (if applicable)"
  ],
  "recommendations": [...]
}
```

---

### Law Generation

#### Generate Legal Text

```http
POST /law/generate
```

**Request Body:**
```json
{
  "title": "Ley de Protección de Datos Personales",
  "purpose": "Regulate personal data processing...",
  "scope": "All entities processing personal data...",
  "key_provisions": [
    "Data subject rights",
    "Controller obligations",
    "Cross-border transfers"
  ],
  "format": "PROYECTO_LEY"
}
```

**Response:**
```json
{
  "generated_text": "EXPOSICIÓN DE MOTIVOS\n...\nTÍTULO I\nDISPOSICIONES GENERALES\n...",
  "structure": {
    "titles": 5,
    "chapters": 12,
    "articles": 45
  },
  "constitutional_alignment": {
    "aligned": true,
    "relevant_articles": [28, 60]
  }
}
```

---

### Voting Map

#### Generate Voting Map

```http
POST /voting/map
```

**Request Body:**
```json
{
  "project_title": "Reform of Tax Code",
  "project_type": "LEY_ORGANICA",
  "current_composition": {
    "PSUV": 92,
    "opposition": 65
  }
}
```

**Response:**
```json
{
  "required_votes": 105,
  "vote_type": "MAYORIA_CALIFICADA",
  "current_projection": {
    "favor": 92,
    "contra": 65,
    "abstain": 0
  },
  "passes": false,
  "swing_votes_needed": 13,
  "analysis": "Requires 2/3 majority for organic law..."
}
```

---

### Reports

#### List Reports

```http
GET /reports
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `case_name` | string | Filter by case |
| `report_type` | string | Filter by type |
| `limit` | int | Max results |

**Response:**
```json
{
  "reports": [
    {
      "filename": "Case_001_analysis.md",
      "case": "Case_001",
      "type": "analysis",
      "created": "2024-01-15T10:30:00Z",
      "size_bytes": 15420
    }
  ],
  "total": 12
}
```

#### Get Report

```http
GET /reports/{filename}
```

**Response:** Raw markdown content of the report

#### Generate Report

```http
POST /reports/generate
```

**Request Body:**
```json
{
  "case_name": "Case_001",
  "report_type": "FULL_ANALYSIS",
  "include_sections": [
    "executive_summary",
    "constitutional_analysis",
    "tsj_jurisprudence",
    "recommendations"
  ],
  "format": "markdown"
}
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": {
    "error": "error_code",
    "message": "Human-readable error message",
    "field": "field_name (if applicable)"
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

### Common Errors

```json
// Rate limit exceeded
{
  "detail": {
    "error": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 3600 seconds.",
    "retry_after": 3600
  }
}

// Invalid API key
{
  "detail": {
    "error": "unauthorized",
    "message": "Invalid or missing API key"
  }
}

// Validation error
{
  "detail": [
    {
      "loc": ["body", "case_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## SDK Examples

### Python

```python
import requests

API_URL = "http://localhost:8000"
API_KEY = "your-api-key"

headers = {"Authorization": f"Bearer {API_KEY}"}

# Run analysis
response = requests.post(
    f"{API_URL}/analyze",
    headers=headers,
    json={
        "case_name": "Test_Case",
        "workflow": "CASE_ANALYSIS",
        "facts": "Worker dismissed without cause...",
        "legal_area": "laboral"
    }
)
result = response.json()
print(result["analysis"])
```

### JavaScript

```javascript
const API_URL = "http://localhost:8000";
const API_KEY = "your-api-key";

async function runAnalysis(caseName, facts) {
  const response = await fetch(`${API_URL}/analyze`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      case_name: caseName,
      workflow: "CASE_ANALYSIS",
      facts: facts,
      legal_area: "laboral"
    })
  });
  return response.json();
}
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Run analysis
curl -X POST http://localhost:8000/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "case_name": "Test_Case",
    "workflow": "CASE_ANALYSIS",
    "facts": "Worker dismissed without cause...",
    "legal_area": "laboral"
  }'

# Search TSJ
curl -X POST http://localhost:8000/tsj/search \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "despido injustificado", "sala": "CASACION_SOCIAL"}'
```

---

## Webhooks (Future)

Webhook support for async notifications is planned for a future release.

---

## Changelog

### v2.0.0
- Initial REST API release
- Full coverage of all VSL modules
- Authentication and rate limiting
- OpenAPI documentation
