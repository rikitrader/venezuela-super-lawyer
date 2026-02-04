#!/usr/bin/env python3
"""
Venezuela Super Lawyer - REST API Layer (FastAPI)

Provides RESTful API endpoints for all 7 workflows and 17 modules.
Supports authentication, rate limiting, and comprehensive documentation.

Version: 1.0.0

Usage:
    # Development
    uvicorn api:app --reload --host 0.0.0.0 --port 8000

    # Production
    gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

    # Or run directly
    python3 api.py
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from functools import wraps
import hashlib
import secrets

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Try to import FastAPI (optional dependency)
try:
    from fastapi import FastAPI, HTTPException, Depends, Header, Query, Body, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("Warning: FastAPI not installed. Run: pip install fastapi uvicorn")

# Import unified models
try:
    from models import (
        WorkflowType, NormType, RiskLevel, ComplianceStatus, Sector, TSJSala, UrgencyLevel,
        IntakeRequest, PreflightResponse, AnalysisResponse, SystemStatus, ModuleStatus, ErrorResponse,
        ConstitutionalAnalysis, TSJResearchResponse, TSJPrediction, GacetaVerificationResponse,
        VotingMapResponse, ContractReviewResponse, HydrocarbonsAnalysisResponse, LawGenerationResponse,
        get_statistics as models_stats
    )
    MODELS_AVAILABLE = True
except ImportError as e:
    MODELS_AVAILABLE = False
    print(f"Warning: models not available: {e}")

# Import core modules
try:
    from run_case_analysis import (
        run_full_case_analysis, run_quick_analysis,
        MODULES_AVAILABLE, WORKFLOW_TYPES
    )
    RUN_CASE_AVAILABLE = True
except ImportError as e:
    RUN_CASE_AVAILABLE = False
    print(f"Warning: run_case_analysis not available: {e}")
    MODULES_AVAILABLE = {}
    WORKFLOW_TYPES = {}


# ═══════════════════════════════════════════════════════════════════════════════
#                         API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

API_TITLE = "Venezuela Super Lawyer API"
API_DESCRIPTION = """
## AI Legal Operating System for Venezuelan Law

This API provides programmatic access to Venezuela Super Lawyer's 17 modules and 7 workflows.

### Workflows Available:
- **CASE_ANALYSIS** - Full legal case analysis
- **LAW_CREATION** - Generate legal instruments
- **RESEARCH** - Legal research and jurisprudence
- **TSJ_PREDICTION** - Supreme Court outcome prediction
- **CONTRACT_REVIEW** - Contract compliance review
- **CONSTITUTIONAL_TEST** - Constitutional compliance testing
- **VOTING_MAP** - Legislative voting analysis

### Authentication:
All endpoints require Bearer token authentication. Set the `VSL_API_KEY` environment variable
or use the token provided during registration.

### Rate Limits:
- Standard: 100 requests/hour
- Premium: 1000 requests/hour
"""

API_VERSION = "2.0.0"
API_TAGS = [
    {"name": "system", "description": "System status and health checks"},
    {"name": "analysis", "description": "Case analysis and workflows"},
    {"name": "constitutional", "description": "Constitutional analysis and testing"},
    {"name": "tsj", "description": "TSJ research and predictions"},
    {"name": "contracts", "description": "Contract review and compliance"},
    {"name": "hydrocarbons", "description": "Hydrocarbons sector analysis"},
    {"name": "law-generation", "description": "Legal instrument generation"},
    {"name": "research", "description": "Legal research endpoints"},
]


# ═══════════════════════════════════════════════════════════════════════════════
#                         AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

# API key storage (in production, use database/Redis)
API_KEYS: Dict[str, Dict[str, Any]] = {}
DEFAULT_API_KEY = os.environ.get("VSL_API_KEY", "")

# Rate limiting storage
RATE_LIMITS: Dict[str, List[datetime]] = {}
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = timedelta(hours=1)


def generate_api_key(user_id: str, tier: str = "standard") -> str:
    """Generate a new API key."""
    key = f"vsl_{secrets.token_urlsafe(32)}"
    API_KEYS[key] = {
        "user_id": user_id,
        "tier": tier,
        "created": datetime.now().isoformat(),
        "requests": 0
    }
    return key


def validate_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """Validate an API key and return user info."""
    if api_key in API_KEYS:
        return API_KEYS[api_key]
    if api_key == DEFAULT_API_KEY and DEFAULT_API_KEY:
        return {"user_id": "default", "tier": "premium", "requests": 0}
    return None


def check_rate_limit(api_key: str) -> bool:
    """Check if request is within rate limits."""
    now = datetime.now()

    # Clean old requests
    if api_key in RATE_LIMITS:
        RATE_LIMITS[api_key] = [
            t for t in RATE_LIMITS[api_key]
            if now - t < RATE_LIMIT_WINDOW
        ]
    else:
        RATE_LIMITS[api_key] = []

    # Check limit
    user_info = validate_api_key(api_key)
    limit = RATE_LIMIT_REQUESTS * 10 if user_info and user_info.get("tier") == "premium" else RATE_LIMIT_REQUESTS

    if len(RATE_LIMITS[api_key]) >= limit:
        return False

    RATE_LIMITS[api_key].append(now)
    return True


# ═══════════════════════════════════════════════════════════════════════════════
#                         FASTAPI APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        openapi_tags=API_TAGS,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # CORS middleware - configurable via environment variable
    # Set VSL_ALLOWED_ORIGINS="https://app.example.com,https://admin.example.com" in production
    _cors_origins_env = os.environ.get("VSL_ALLOWED_ORIGINS", "")
    ALLOWED_ORIGINS = [o.strip() for o in _cors_origins_env.split(",") if o.strip()] if _cors_origins_env else ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
    )

    security = HTTPBearer(auto_error=False)


    # ═══════════════════════════════════════════════════════════════════════════
    #                         DEPENDENCIES
    # ═══════════════════════════════════════════════════════════════════════════

    async def get_api_key(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        x_api_key: Optional[str] = Header(None, alias="X-API-Key")
    ) -> Dict[str, Any]:
        """Validate API key from Bearer token or X-API-Key header."""
        api_key = None

        if credentials:
            api_key = credentials.credentials
        elif x_api_key:
            api_key = x_api_key
        elif DEFAULT_API_KEY:
            api_key = DEFAULT_API_KEY

        if not api_key:
            raise HTTPException(
                status_code=401,
                detail="API key required. Provide via Bearer token or X-API-Key header."
            )

        user_info = validate_api_key(api_key)
        if not user_info:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )

        if not check_rate_limit(api_key):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        return {"api_key": api_key, **user_info}


    # ═══════════════════════════════════════════════════════════════════════════
    #                         SYSTEM ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.get("/", tags=["system"])
    async def root():
        """API root - returns basic info."""
        return {
            "name": API_TITLE,
            "version": API_VERSION,
            "status": "operational",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }


    @app.get("/health", tags=["system"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION
        }


    @app.get("/status", response_model=SystemStatus, tags=["system"])
    async def system_status(user: Dict = Depends(get_api_key)):
        """Get detailed system status including module availability."""
        modules = []
        for name, available in MODULES_AVAILABLE.items():
            modules.append(ModuleStatus(
                name=name,
                available=available,
                version=__version__,
                capabilities=[]
            ))

        return SystemStatus(
            status="operational",
            version=API_VERSION,
            modules=modules,
            workflows_available=list(WORKFLOW_TYPES.keys()) if WORKFLOW_TYPES else []
        )


    @app.get("/modules", tags=["system"])
    async def list_modules(user: Dict = Depends(get_api_key)):
        """List all available modules and their status."""
        return {
            "modules": MODULES_AVAILABLE,
            "total": len(MODULES_AVAILABLE),
            "available": sum(1 for v in MODULES_AVAILABLE.values() if v)
        }


    @app.get("/workflows", tags=["system"])
    async def list_workflows(user: Dict = Depends(get_api_key)):
        """List all available workflows."""
        workflows = []
        for wf_type in WorkflowType:
            config = WORKFLOW_TYPES.get(wf_type.value, {}) if WORKFLOW_TYPES else {}
            workflows.append({
                "type": wf_type.value,
                "description": config.get("description", ""),
                "required_fields": config.get("required_fields", []),
                "modules_used": config.get("modules", [])
            })
        return {"workflows": workflows}


    # ═══════════════════════════════════════════════════════════════════════════
    #                         ANALYSIS ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.post("/api/v1/analyze", response_model=AnalysisResponse, tags=["analysis"])
    async def analyze_case(
        request: IntakeRequest,
        background_tasks: BackgroundTasks,
        user: Dict = Depends(get_api_key)
    ):
        """
        Run full case analysis.

        This endpoint executes the complete analysis workflow based on the specified
        workflow_type. Results include constitutional analysis, TSJ research,
        voting maps, and more depending on the workflow.
        """
        if not RUN_CASE_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Analysis module not available"
            )

        try:
            # Convert Pydantic model to dict for existing function
            intake_dict = request.model_dump() if hasattr(request, 'model_dump') else request.__dict__

            # Run analysis
            result = run_full_case_analysis(
                case_name=request.case_name,
                workflow_type=request.workflow_type.value if hasattr(request.workflow_type, 'value') else request.workflow_type,
                proposal_text=request.proposal_text,
                keywords=request.keywords,
                sector=request.sector.value if hasattr(request.sector, 'value') else request.sector,
                norm_type=request.norm_type.value if hasattr(request.norm_type, 'value') else request.norm_type
            )

            # Convert to response model
            return AnalysisResponse(
                case_name=request.case_name,
                workflow_type=request.workflow_type,
                success=result.success if hasattr(result, 'success') else True,
                modules_run=result.modules_run if hasattr(result, 'modules_run') else [],
                report_path=result.report_path if hasattr(result, 'report_path') else None,
                errors=result.errors if hasattr(result, 'errors') else []
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )


    @app.post("/api/v1/analyze/quick", tags=["analysis"])
    async def quick_analysis(
        text: str = Body(..., embed=True, description="Text to analyze"),
        user: Dict = Depends(get_api_key)
    ):
        """
        Quick text analysis without creating a full case.

        Performs rapid constitutional conflict detection and risk assessment.
        """
        if not RUN_CASE_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="Analysis module not available"
            )

        try:
            result = run_quick_analysis(text)
            return result.to_dict() if hasattr(result, 'to_dict') else result
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Quick analysis failed: {str(e)}"
            )


    # ═══════════════════════════════════════════════════════════════════════════
    #                         CONSTITUTIONAL ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.post("/api/v1/constitutional/test", tags=["constitutional"])
    async def constitutional_test(
        text: str = Body(..., embed=True, description="Legal text to test"),
        norm_type: NormType = Body(default=NormType.LEY_ORDINARIA),
        user: Dict = Depends(get_api_key)
    ):
        """
        Run constitutional compliance tests on legal text.

        Tests include eternity clause violations, rights conflicts,
        competency issues, and procedural compliance.
        """
        if not MODULES_AVAILABLE.get("constitutional_test"):
            raise HTTPException(
                status_code=503,
                detail="Constitutional test module not available"
            )

        try:
            from constitutional_test import run_full_constitutional_test
            result = run_full_constitutional_test(text, norm_type.value)
            return result.to_dict() if hasattr(result, 'to_dict') else result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/constitutional/article/{article_num}", tags=["constitutional"])
    async def get_constitutional_article(
        article_num: int,
        user: Dict = Depends(get_api_key)
    ):
        """Get a specific CRBV article by number."""
        if not MODULES_AVAILABLE.get("constitution_diff"):
            raise HTTPException(
                status_code=503,
                detail="Constitution diff module not available"
            )

        try:
            from constitution_diff import get_article
            article = get_article(article_num)
            if article:
                return article
            raise HTTPException(status_code=404, detail=f"Article {article_num} not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/constitutional/search", tags=["constitutional"])
    async def search_constitution(
        query: str = Query(..., min_length=2, description="Search query"),
        user: Dict = Depends(get_api_key)
    ):
        """Search the Venezuelan Constitution."""
        if not MODULES_AVAILABLE.get("constitution_diff"):
            raise HTTPException(
                status_code=503,
                detail="Constitution diff module not available"
            )

        try:
            from constitution_diff import search_articles
            results = search_articles(query)
            return {"query": query, "results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/constitutional/eternity-clauses", tags=["constitutional"])
    async def get_eternity_clauses(user: Dict = Depends(get_api_key)):
        """Get all eternity clauses (cláusulas pétreas) from CRBV."""
        if not MODULES_AVAILABLE.get("constitution_diff"):
            raise HTTPException(
                status_code=503,
                detail="Constitution diff module not available"
            )

        try:
            from constitution_diff import get_eternity_clauses
            return {"eternity_clauses": get_eternity_clauses()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ═══════════════════════════════════════════════════════════════════════════
    #                         TSJ ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.get("/api/v1/tsj/search", tags=["tsj"])
    async def search_tsj(
        query: str = Query(..., min_length=2, description="Search query"),
        sala: Optional[TSJSala] = Query(None, description="Filter by chamber"),
        vinculante: Optional[bool] = Query(None, description="Filter binding only"),
        limit: int = Query(20, ge=1, le=100, description="Max results"),
        user: Dict = Depends(get_api_key)
    ):
        """
        Search TSJ jurisprudence database.

        Returns matching Supreme Court decisions with metadata.
        """
        if not MODULES_AVAILABLE.get("tsj_search"):
            raise HTTPException(
                status_code=503,
                detail="TSJ search module not available"
            )

        try:
            from tsj_search import buscar_por_texto, buscar_vinculantes, buscar_por_sala

            if vinculante:
                results = buscar_vinculantes()
            elif sala:
                results = buscar_por_sala(sala.value)
            else:
                results = buscar_por_texto(query)

            return {
                "query": query,
                "total_found": len(results),
                "decisions": results[:limit]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.post("/api/v1/tsj/predict", response_model=TSJPrediction, tags=["tsj"])
    async def predict_tsj_outcome(
        case_facts: str = Body(..., embed=True, description="Case facts"),
        legal_area: str = Body(..., embed=True, description="Legal area"),
        user: Dict = Depends(get_api_key)
    ):
        """
        Predict TSJ case outcome using ML model.

        Analyzes case facts and returns probability of favorable outcome
        along with similar historical cases.
        """
        # Check if ML predictor is available
        try:
            from tsj_predictor import predict_outcome
            result = predict_outcome(case_facts, legal_area)
            return result
        except ImportError:
            # Fallback to heuristic prediction
            return TSJPrediction(
                predicted_outcome="Requiere análisis detallado",
                confidence=0.5,
                favorable_probability=0.5,
                sala_recomendada=TSJSala.CONSTITUCIONAL,
                similar_cases=[],
                key_factors=["Análisis ML no disponible - usando heurísticas"],
                risk_factors=["Predicción basada en patrones generales"]
            )


    # ═══════════════════════════════════════════════════════════════════════════
    #                         GACETA OFICIAL ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.get("/api/v1/gaceta/search", tags=["research"])
    async def search_gaceta(
        query: str = Query(..., min_length=2, description="Search query"),
        tipo: Optional[NormType] = Query(None, description="Filter by norm type"),
        vigente: Optional[bool] = Query(None, description="Filter by current validity"),
        limit: int = Query(20, ge=1, le=100, description="Max results"),
        user: Dict = Depends(get_api_key)
    ):
        """
        Search Gaceta Oficial database.

        Returns published norms matching the query.
        """
        if not MODULES_AVAILABLE.get("gaceta_verify"):
            raise HTTPException(
                status_code=503,
                detail="Gaceta verify module not available"
            )

        try:
            from gaceta_verify import search_norms, get_norms_by_type

            if tipo:
                results = get_norms_by_type(tipo.value)
            else:
                results = search_norms(query)

            if vigente is not None:
                results = [r for r in results if r.get("vigente") == vigente]

            return {
                "query": query,
                "norms_found": len(results),
                "norms": results[:limit]
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/gaceta/verify/{gaceta_numero}", tags=["research"])
    async def verify_gaceta(
        gaceta_numero: str,
        user: Dict = Depends(get_api_key)
    ):
        """Verify a specific Gaceta Oficial number."""
        if not MODULES_AVAILABLE.get("gaceta_verify"):
            raise HTTPException(
                status_code=503,
                detail="Gaceta verify module not available"
            )

        try:
            from gaceta_verify import search_norms
            results = search_norms(gaceta_numero)
            if results:
                return {"verified": True, "norm": results[0]}
            return {"verified": False, "norm": None}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ═══════════════════════════════════════════════════════════════════════════
    #                         CONTRACT REVIEW ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.post("/api/v1/contracts/review", response_model=ContractReviewResponse, tags=["contracts"])
    async def review_contract(
        contract_text: str = Body(..., embed=True, description="Contract text to review"),
        contract_type: Optional[str] = Body(None, embed=True, description="Expected contract type"),
        user: Dict = Depends(get_api_key)
    ):
        """
        Review a contract for Venezuelan law compliance.

        Analyzes clauses, identifies risks, and checks legal compliance.
        """
        if not MODULES_AVAILABLE.get("contract_review"):
            raise HTTPException(
                status_code=503,
                detail="Contract review module not available"
            )

        try:
            from contract_review import review_contract as do_review
            result = do_review(contract_text, contract_type)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.post("/api/v1/contracts/clause-check", tags=["contracts"])
    async def check_clause(
        clause_text: str = Body(..., embed=True, description="Clause text"),
        clause_type: str = Body(..., embed=True, description="Type of clause"),
        user: Dict = Depends(get_api_key)
    ):
        """Check a specific contract clause for compliance."""
        if not MODULES_AVAILABLE.get("contract_review"):
            raise HTTPException(
                status_code=503,
                detail="Contract review module not available"
            )

        try:
            from contract_review import analyze_clauses
            result = analyze_clauses(clause_text)
            return {"clause_type": clause_type, "analysis": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ═══════════════════════════════════════════════════════════════════════════
    #                         HYDROCARBONS ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.post("/api/v1/hydrocarbons/analyze", response_model=HydrocarbonsAnalysisResponse, tags=["hydrocarbons"])
    async def analyze_hydrocarbons(
        activity_type: str = Body(..., embed=True, description="Activity type (exploracion, explotacion, etc.)"),
        company_name: Optional[str] = Body(None, embed=True),
        pdvsa_participation: Optional[float] = Body(None, embed=True, ge=0, le=100),
        user: Dict = Depends(get_api_key)
    ):
        """
        Analyze hydrocarbons sector activity under LOH.

        Returns applicable regulations, fiscal obligations, and compliance requirements.
        """
        if not MODULES_AVAILABLE.get("hydrocarbons_playbook"):
            raise HTTPException(
                status_code=503,
                detail="Hydrocarbons playbook module not available"
            )

        try:
            from hydrocarbons_playbook import run_full_hydrocarbons_analysis
            result = run_full_hydrocarbons_analysis(
                activity_type=activity_type,
                company_name=company_name,
                pdvsa_participation=pdvsa_participation
            )
            return result.to_dict() if hasattr(result, 'to_dict') else result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/hydrocarbons/loh/article/{article_num}", tags=["hydrocarbons"])
    async def get_loh_article(
        article_num: int,
        user: Dict = Depends(get_api_key)
    ):
        """Get a specific LOH article."""
        if not MODULES_AVAILABLE.get("hydrocarbons_playbook"):
            raise HTTPException(
                status_code=503,
                detail="Hydrocarbons playbook module not available"
            )

        try:
            from hydrocarbons_playbook import LOH_ARTICLES
            article = LOH_ARTICLES.get(article_num)
            if article:
                return {"article_number": article_num, **article}
            raise HTTPException(status_code=404, detail=f"LOH Article {article_num} not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/hydrocarbons/fiscal-obligations", tags=["hydrocarbons"])
    async def get_fiscal_obligations(user: Dict = Depends(get_api_key)):
        """Get all fiscal obligations under LOH."""
        if not MODULES_AVAILABLE.get("hydrocarbons_playbook"):
            raise HTTPException(
                status_code=503,
                detail="Hydrocarbons playbook module not available"
            )

        try:
            from hydrocarbons_playbook import FISCAL_OBLIGATIONS
            return {"fiscal_obligations": FISCAL_OBLIGATIONS}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ═══════════════════════════════════════════════════════════════════════════
    #                         LAW GENERATION ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.post("/api/v1/laws/generate", response_model=LawGenerationResponse, tags=["law-generation"])
    async def generate_law(
        title: str = Body(..., embed=True, description="Law title"),
        instrument_type: NormType = Body(default=NormType.LEY_ORDINARIA),
        sector: Sector = Body(default=Sector.GENERAL),
        objectives: List[str] = Body(default=[], embed=True),
        enforcement: str = Body(default="administrative", embed=True),
        user: Dict = Depends(get_api_key)
    ):
        """
        Generate a complete legal instrument.

        Creates a full law/decree/resolution with proper Venezuelan format,
        including exposición de motivos, articles, and implementation roadmap.
        """
        if not MODULES_AVAILABLE.get("law_generator"):
            raise HTTPException(
                status_code=503,
                detail="Law generator module not available"
            )

        try:
            from law_generator import generate_legal_instrument, generate_implementation_roadmap

            instrument = generate_legal_instrument(
                titulo=title,
                tipo=instrument_type.value,
                sector=sector.value,
                objetivos=objectives,
                enforcement=enforcement
            )

            roadmap = generate_implementation_roadmap(instrument)

            return LawGenerationResponse(
                instrument_type=instrument_type,
                title=title,
                full_text=instrument.to_full_text() if hasattr(instrument, 'to_full_text') else str(instrument),
                article_count=instrument.get_article_count() if hasattr(instrument, 'get_article_count') else 0,
                articles=[],
                exposicion_motivos=instrument.exposicion_motivos if hasattr(instrument, 'exposicion_motivos') else "",
                roadmap=None
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.post("/api/v1/laws/hydrocarbons", tags=["law-generation"])
    async def generate_hydrocarbons_law(
        title: str = Body(..., embed=True),
        objectives: List[str] = Body(default=[], embed=True),
        user: Dict = Depends(get_api_key)
    ):
        """Generate a hydrocarbons sector specific law."""
        if not MODULES_AVAILABLE.get("law_generator"):
            raise HTTPException(
                status_code=503,
                detail="Law generator module not available"
            )

        try:
            from law_generator import generate_hydrocarbons_instrument
            instrument = generate_hydrocarbons_instrument(title, objectives)
            return {
                "title": title,
                "full_text": instrument.to_full_text() if hasattr(instrument, 'to_full_text') else str(instrument),
                "article_count": instrument.get_article_count() if hasattr(instrument, 'get_article_count') else 0
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ═══════════════════════════════════════════════════════════════════════════
    #                         VOTING MAP ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.post("/api/v1/voting/map", response_model=VotingMapResponse, tags=["analysis"])
    async def generate_voting_map(
        proposal_text: str = Body(..., embed=True, description="Proposal text"),
        norm_type: NormType = Body(default=NormType.LEY_ORDINARIA),
        user: Dict = Depends(get_api_key)
    ):
        """
        Generate legislative voting map for a proposal.

        Analyzes voting requirements, political feasibility, and procedural steps.
        """
        if not MODULES_AVAILABLE.get("voting_map"):
            raise HTTPException(
                status_code=503,
                detail="Voting map module not available"
            )

        try:
            from voting_map import generate_voting_map as do_voting_map, NormType as VotingNormType
            result = do_voting_map(proposal_text, VotingNormType(norm_type.value))
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/voting/requirements/{norm_type}", tags=["analysis"])
    async def get_voting_requirements(
        norm_type: NormType,
        user: Dict = Depends(get_api_key)
    ):
        """Get voting requirements for a specific norm type."""
        if not MODULES_AVAILABLE.get("voting_map"):
            raise HTTPException(
                status_code=503,
                detail="Voting map module not available"
            )

        try:
            from voting_map import get_majority_comparison
            return get_majority_comparison(norm_type.value)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ═══════════════════════════════════════════════════════════════════════════
    #                         REPORTS ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.get("/api/v1/reports", tags=["research"])
    async def list_reports(
        limit: int = Query(20, ge=1, le=100),
        user: Dict = Depends(get_api_key)
    ):
        """List all generated reports."""
        if not MODULES_AVAILABLE.get("report_manager"):
            raise HTTPException(
                status_code=503,
                detail="Report manager module not available"
            )

        try:
            from report_manager import list_reports
            reports = list_reports()
            return {"reports": reports[:limit], "total": len(reports)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @app.get("/api/v1/reports/{report_id}", tags=["research"])
    async def get_report(
        report_id: str,
        user: Dict = Depends(get_api_key)
    ):
        """Get a specific report by ID."""
        if not MODULES_AVAILABLE.get("report_manager"):
            raise HTTPException(
                status_code=503,
                detail="Report manager module not available"
            )

        try:
            from report_manager import get_report_path
            report_path = get_report_path(report_id)
            if report_path.exists():
                content = report_path.read_text(encoding='utf-8')
                return {"report_id": report_id, "content": content, "path": str(report_path)}
            raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    # ═══════════════════════════════════════════════════════════════════════════
    #                         ERROR HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "code": f"HTTP_{exc.status_code}",
                "timestamp": datetime.now().isoformat()
            }
        )


    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "code": "INTERNAL_ERROR",
                "details": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )

else:
    # Fallback when FastAPI is not available
    app = None


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def get_statistics() -> Dict[str, Any]:
    """Get API statistics."""
    return {
        "module": "REST API Layer",
        "version": __version__,
        "fastapi_available": FASTAPI_AVAILABLE,
        "models_available": MODELS_AVAILABLE,
        "run_case_available": RUN_CASE_AVAILABLE,
        "endpoints": {
            "system": ["/", "/health", "/status", "/modules", "/workflows"],
            "analysis": ["/api/v1/analyze", "/api/v1/analyze/quick"],
            "constitutional": ["/api/v1/constitutional/test", "/api/v1/constitutional/article/{num}",
                            "/api/v1/constitutional/search", "/api/v1/constitutional/eternity-clauses"],
            "tsj": ["/api/v1/tsj/search", "/api/v1/tsj/predict"],
            "gaceta": ["/api/v1/gaceta/search", "/api/v1/gaceta/verify/{num}"],
            "contracts": ["/api/v1/contracts/review", "/api/v1/contracts/clause-check"],
            "hydrocarbons": ["/api/v1/hydrocarbons/analyze", "/api/v1/hydrocarbons/loh/article/{num}",
                           "/api/v1/hydrocarbons/fiscal-obligations"],
            "law_generation": ["/api/v1/laws/generate", "/api/v1/laws/hydrocarbons"],
            "voting": ["/api/v1/voting/map", "/api/v1/voting/requirements/{norm_type}"],
            "reports": ["/api/v1/reports", "/api/v1/reports/{report_id}"]
        },
        "authentication": "Bearer token or X-API-Key header",
        "rate_limits": {
            "standard": f"{RATE_LIMIT_REQUESTS} requests/hour",
            "premium": f"{RATE_LIMIT_REQUESTS * 10} requests/hour"
        }
    }


def main():
    """Run the API server."""
    import argparse

    parser = argparse.ArgumentParser(description="Venezuela Super Lawyer REST API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--stats", action="store_true", help="Show API statistics")

    args = parser.parse_args()

    if args.stats:
        import json
        print(json.dumps(get_statistics(), indent=2))
        return

    if not FASTAPI_AVAILABLE:
        print("ERROR: FastAPI not installed. Run: pip install fastapi uvicorn")
        sys.exit(1)

    try:
        import uvicorn
        print(f"\n{'='*60}")
        print(f"  VENEZUELA SUPER LAWYER - REST API v{API_VERSION}")
        print(f"{'='*60}")
        print(f"  Starting server on http://{args.host}:{args.port}")
        print(f"  API Docs: http://{args.host}:{args.port}/docs")
        print(f"  ReDoc: http://{args.host}:{args.port}/redoc")
        print(f"{'='*60}\n")

        uvicorn.run(
            "api:app",
            host=args.host,
            port=args.port,
            reload=args.reload
        )
    except ImportError:
        print("ERROR: uvicorn not installed. Run: pip install uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    main()
