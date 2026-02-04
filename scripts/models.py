#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Unified Data Models (Pydantic Schemas)

Provides consistent data models across all 17 modules with validation,
serialization, and OpenAPI schema generation support.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum

# Use Pydantic v2 if available, fallback to dataclasses
try:
    from pydantic import BaseModel, Field, field_validator, ConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    from dataclasses import dataclass, field
    # Create a simple BaseModel fallback
    class BaseModel:
        def model_dump(self) -> Dict:
            return self.__dict__
        def model_dump_json(self) -> str:
            import json
            return json.dumps(self.model_dump(), default=str, ensure_ascii=False)
    def Field(default=None, **kwargs):
        return default


# ═══════════════════════════════════════════════════════════════════════════════
#                         ENUMS - UNIFIED ACROSS ALL MODULES
# ═══════════════════════════════════════════════════════════════════════════════

class WorkflowType(str, Enum):
    """Available workflow types in Venezuela Super Lawyer."""
    CASE_ANALYSIS = "CASE_ANALYSIS"
    LAW_CREATION = "LAW_CREATION"
    RESEARCH = "RESEARCH"
    TSJ_PREDICTION = "TSJ_PREDICTION"
    CONTRACT_REVIEW = "CONTRACT_REVIEW"
    CONSTITUTIONAL_TEST = "CONSTITUTIONAL_TEST"
    VOTING_MAP = "VOTING_MAP"


class NormType(str, Enum):
    """Types of legal norms in Venezuelan hierarchy."""
    CRBV = "CRBV"  # Constitution
    LEY_ORGANICA = "LEY_ORGANICA"
    LEY_ORDINARIA = "LEY_ORDINARIA"
    DECRETO_LEY = "DECRETO_LEY"
    DECRETO = "DECRETO"
    REGLAMENTO = "REGLAMENTO"
    RESOLUCION = "RESOLUCION"
    PROVIDENCIA = "PROVIDENCIA"
    NORMA_TECNICA = "NORMA_TECNICA"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "bajo"
    MEDIUM = "medio"
    HIGH = "alto"
    CRITICAL = "critico"


class ComplianceStatus(str, Enum):
    """Compliance check status."""
    COMPLIANT = "cumple"
    NON_COMPLIANT = "no_cumple"
    PARTIAL = "parcial"
    NOT_APPLICABLE = "no_aplica"
    REQUIRES_REVIEW = "requiere_revision"


class Sector(str, Enum):
    """Industry sectors for specialized analysis."""
    HYDROCARBONS = "hidrocarburos"
    BANKING = "banca"
    MINING = "mineria"
    TELECOMMUNICATIONS = "telecomunicaciones"
    LABOR = "laboral"
    TAX = "tributario"
    ENVIRONMENTAL = "ambiental"
    CORPORATE = "mercantil"
    REAL_ESTATE = "inmobiliario"
    GENERAL = "general"


class TSJSala(str, Enum):
    """TSJ (Supreme Court) chambers."""
    CONSTITUCIONAL = "Sala Constitucional"
    POLITICO_ADMINISTRATIVA = "Sala Político Administrativa"
    ELECTORAL = "Sala Electoral"
    CASACION_CIVIL = "Sala de Casación Civil"
    CASACION_PENAL = "Sala de Casación Penal"
    CASACION_SOCIAL = "Sala de Casación Social"
    PLENA = "Sala Plena"


class UrgencyLevel(str, Enum):
    """Urgency levels for case processing."""
    EMERGENCY = "emergency"
    URGENT = "urgent"
    NORMAL = "normal"
    LOW = "low"


# ═══════════════════════════════════════════════════════════════════════════════
#                         BASE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

if PYDANTIC_AVAILABLE:
    class VSLBaseModel(BaseModel):
        """Base model with common configuration."""
        model_config = ConfigDict(
            use_enum_values=True,
            str_strip_whitespace=True,
            validate_default=True,
            extra='ignore'
        )
else:
    VSLBaseModel = BaseModel


# ═══════════════════════════════════════════════════════════════════════════════
#                         INTAKE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class IntakeRequest(VSLBaseModel):
    """Unified intake request for all workflows."""
    workflow_type: WorkflowType = Field(default=WorkflowType.CASE_ANALYSIS, description="Type of workflow to execute")
    case_name: str = Field(..., min_length=1, max_length=200, description="Unique case identifier")
    client_name: Optional[str] = Field(default=None, description="Client name (optional)")
    problem_statement: Optional[str] = Field(default=None, description="Description of the legal problem")
    desired_outcome: Optional[str] = Field(default=None, description="Desired outcome or objective")
    proposal_text: Optional[str] = Field(default=None, description="Text of the legal proposal (for LAW_CREATION)")
    norm_type: NormType = Field(default=NormType.LEY_ORDINARIA, description="Type of norm being analyzed/created")
    affected_group: Optional[str] = Field(default=None, description="Group affected by the proposal")
    sector: Sector = Field(default=Sector.GENERAL, description="Industry sector")
    urgency_level: UrgencyLevel = Field(default=UrgencyLevel.NORMAL, description="Urgency of processing")
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    facts_timeline: Optional[str] = Field(default=None, description="Timeline of relevant facts")
    existing_law: Optional[str] = Field(default=None, description="Existing law to modify/replace")
    enforcement_mechanism: Optional[str] = Field(default=None, description="Enforcement type: criminal/administrative/civil/incentives")
    political_context: Optional[str] = Field(default=None, description="Political context analysis")
    contract_text: Optional[str] = Field(default=None, description="Contract text for CONTRACT_REVIEW")

    if PYDANTIC_AVAILABLE:
        @field_validator('case_name')
        @classmethod
        def validate_case_name(cls, v: str) -> str:
            """Sanitize case name for file system compatibility."""
            import re
            sanitized = re.sub(r'[<>:"/\\|?*]', '', v)
            sanitized = sanitized.replace(' ', '_')
            return sanitized[:100]


class PreflightCheck(VSLBaseModel):
    """Individual preflight check result."""
    gate: str = Field(..., description="Gate identifier (e.g., GATE_1)")
    name: str = Field(..., description="Check name")
    status: str = Field(..., description="PASS, FAIL, or WARN")
    expected: str = Field(..., description="Expected condition")
    actual: str = Field(..., description="Actual value found")
    blocking: bool = Field(default=True, description="Whether failure blocks execution")


class PreflightResponse(VSLBaseModel):
    """Preflight checks response."""
    passed: bool = Field(..., description="Whether all blocking checks passed")
    gates_passed: int = Field(default=0, description="Number of gates passed")
    gates_failed: int = Field(default=0, description="Number of gates failed")
    warnings: int = Field(default=0, description="Number of warnings")
    checks: List[PreflightCheck] = Field(default_factory=list, description="Individual check results")
    errors: List[str] = Field(default_factory=list, description="Error messages")


# ═══════════════════════════════════════════════════════════════════════════════
#                         CONSTITUTIONAL ANALYSIS MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ConstitutionalConflict(VSLBaseModel):
    """A conflict with the Venezuelan Constitution."""
    article: int = Field(..., ge=1, le=350, description="CRBV article number")
    title: str = Field(..., description="Article title")
    conflict_type: str = Field(..., description="Type of conflict")
    description: str = Field(..., description="Description of the conflict")
    severity: RiskLevel = Field(default=RiskLevel.MEDIUM, description="Severity level")
    recommendation: str = Field(..., description="Recommended action")
    is_eternity_clause: bool = Field(default=False, description="Whether it affects an eternity clause")


class ConstitutionalAnalysis(VSLBaseModel):
    """Constitutional analysis result."""
    risk_score: float = Field(default=0.0, ge=0, le=100, description="Risk score (0-100)")
    compliance_percentage: float = Field(default=100.0, ge=0, le=100, description="Compliance percentage")
    conflicts_found: int = Field(default=0, ge=0, description="Number of conflicts found")
    conflicts: List[ConstitutionalConflict] = Field(default_factory=list, description="List of conflicts")
    eternity_clause_violations: List[str] = Field(default_factory=list, description="Eternity clause violations")
    affected_articles: List[int] = Field(default_factory=list, description="Affected CRBV articles")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class ConstitutionalTest(VSLBaseModel):
    """Individual constitutional test result."""
    test_name: str = Field(..., description="Name of the test")
    passed: bool = Field(..., description="Whether the test passed")
    score: float = Field(default=0.0, ge=0, le=100, description="Test score")
    details: str = Field(default="", description="Test details")
    crbv_articles: List[int] = Field(default_factory=list, description="Related CRBV articles")


class ConstitutionalTestResponse(VSLBaseModel):
    """Constitutional test battery response."""
    total_tests: int = Field(default=0, ge=0, description="Total tests run")
    tests_passed: int = Field(default=0, ge=0, description="Tests passed")
    overall_score: float = Field(default=0.0, ge=0, le=100, description="Overall score")
    tests: List[ConstitutionalTest] = Field(default_factory=list, description="Individual test results")
    recommendation: str = Field(default="", description="Overall recommendation")


# ═══════════════════════════════════════════════════════════════════════════════
#                         TSJ/JURISPRUDENCE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class TSJDecision(VSLBaseModel):
    """TSJ (Supreme Court) decision."""
    id: str = Field(..., description="Decision identifier")
    sala: TSJSala = Field(..., description="TSJ chamber")
    fecha: str = Field(..., description="Decision date")
    expediente: str = Field(default="", description="Case number")
    magistrado_ponente: str = Field(default="", description="Reporting justice")
    partes: str = Field(default="", description="Parties involved")
    materia: str = Field(default="", description="Subject matter")
    resumen: str = Field(default="", description="Decision summary")
    dispositivo: str = Field(default="", description="Ruling")
    vinculante: bool = Field(default=False, description="Whether binding precedent")
    url: Optional[str] = Field(default=None, description="URL to full decision")


class TSJResearchResponse(VSLBaseModel):
    """TSJ research results."""
    query: str = Field(..., description="Search query")
    total_found: int = Field(default=0, ge=0, description="Total decisions found")
    binding_precedents: int = Field(default=0, ge=0, description="Number of binding precedents")
    decisions: List[TSJDecision] = Field(default_factory=list, description="Matching decisions")
    relevant_articles: List[int] = Field(default_factory=list, description="Relevant CRBV articles")


class TSJPrediction(VSLBaseModel):
    """TSJ outcome prediction (ML-based)."""
    predicted_outcome: str = Field(..., description="Predicted outcome")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")
    favorable_probability: float = Field(..., ge=0, le=1, description="Probability of favorable outcome")
    sala_recomendada: TSJSala = Field(..., description="Recommended chamber")
    similar_cases: List[TSJDecision] = Field(default_factory=list, description="Similar historical cases")
    key_factors: List[str] = Field(default_factory=list, description="Key factors affecting prediction")
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors identified")


# ═══════════════════════════════════════════════════════════════════════════════
#                         GACETA OFICIAL MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class GacetaNorm(VSLBaseModel):
    """Norm published in Gaceta Oficial."""
    gaceta_numero: str = Field(..., description="Gaceta number")
    fecha: str = Field(..., description="Publication date")
    tipo: NormType = Field(..., description="Norm type")
    titulo: str = Field(..., description="Norm title")
    organo_emisor: str = Field(default="", description="Issuing body")
    vigente: bool = Field(default=True, description="Whether currently in force")
    derogado_por: Optional[str] = Field(default=None, description="Derogated by")
    contenido_resumen: str = Field(default="", description="Content summary")
    url: Optional[str] = Field(default=None, description="URL to original")


class GacetaVerificationResponse(VSLBaseModel):
    """Gaceta verification response."""
    query: str = Field(..., description="Search query")
    norms_found: int = Field(default=0, ge=0, description="Norms found")
    norms: List[GacetaNorm] = Field(default_factory=list, description="Matching norms")
    verification_status: str = Field(default="", description="Verification status")


# ═══════════════════════════════════════════════════════════════════════════════
#                         VOTING MAP MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class VotingRequirement(VSLBaseModel):
    """Legislative voting requirement."""
    norm_type: NormType = Field(..., description="Type of norm")
    majority_type: str = Field(..., description="Required majority type")
    votes_needed: int = Field(..., ge=0, description="Votes needed")
    total_deputies: int = Field(default=277, ge=0, description="Total deputies")
    percentage: float = Field(..., ge=0, le=100, description="Percentage required")
    crbv_article: int = Field(..., ge=0, description="Constitutional basis")
    special_requirements: List[str] = Field(default_factory=list, description="Special requirements")


class PoliticalFeasibility(VSLBaseModel):
    """Political feasibility assessment."""
    feasibility_score: float = Field(..., ge=0, le=100, description="Feasibility score")
    feasibility_level: str = Field(..., description="alta/media/baja")
    supporting_factors: List[str] = Field(default_factory=list, description="Supporting factors")
    blocking_factors: List[str] = Field(default_factory=list, description="Blocking factors")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class VotingMapResponse(VSLBaseModel):
    """Voting map analysis response."""
    proposal_summary: str = Field(..., description="Proposal summary")
    voting_requirement: VotingRequirement = Field(..., description="Voting requirements")
    feasibility: PoliticalFeasibility = Field(..., description="Political feasibility")
    timeline_estimate: str = Field(default="", description="Estimated timeline")
    procedural_steps: List[str] = Field(default_factory=list, description="Procedural steps")


# ═══════════════════════════════════════════════════════════════════════════════
#                         CONTRACT REVIEW MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ContractParty(VSLBaseModel):
    """Contract party."""
    name: str = Field(..., description="Party name")
    role: str = Field(..., description="Role in contract")
    rif: Optional[str] = Field(default=None, description="RIF/tax ID")
    address: Optional[str] = Field(default=None, description="Address")
    representative: Optional[str] = Field(default=None, description="Legal representative")


class ClauseAnalysis(VSLBaseModel):
    """Individual clause analysis."""
    clause_type: str = Field(..., description="Type of clause")
    found: bool = Field(..., description="Whether clause was found")
    text: str = Field(default="", description="Clause text")
    compliance: ComplianceStatus = Field(default=ComplianceStatus.NOT_APPLICABLE, description="Compliance status")
    risk_level: RiskLevel = Field(default=RiskLevel.LOW, description="Risk level")
    issues: List[str] = Field(default_factory=list, description="Issues identified")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class RiskPattern(VSLBaseModel):
    """Risk pattern found in contract."""
    pattern_name: str = Field(..., description="Pattern name")
    description: str = Field(..., description="Pattern description")
    risk_level: RiskLevel = Field(..., description="Risk level")
    location: str = Field(default="", description="Location in contract")
    recommendation: str = Field(default="", description="Recommendation")


class ContractReviewResponse(VSLBaseModel):
    """Contract review response."""
    contract_type: str = Field(..., description="Detected contract type")
    parties: List[ContractParty] = Field(default_factory=list, description="Contract parties")
    clauses: List[ClauseAnalysis] = Field(default_factory=list, description="Clause analysis")
    risk_patterns: List[RiskPattern] = Field(default_factory=list, description="Risk patterns found")
    overall_risk: RiskLevel = Field(..., description="Overall risk level")
    compliance_score: float = Field(..., ge=0, le=100, description="Compliance score")
    missing_clauses: List[str] = Field(default_factory=list, description="Missing required clauses")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


# ═══════════════════════════════════════════════════════════════════════════════
#                         HYDROCARBONS MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class HydrocarbonsActivityType(str, Enum):
    """Hydrocarbon activity types per LOH."""
    EXPLORACION = "exploracion"
    EXPLOTACION = "explotacion"
    REFINACION = "refinacion"
    INDUSTRIALIZACION = "industrializacion"
    TRANSPORTE = "transporte"
    ALMACENAMIENTO = "almacenamiento"
    COMERCIALIZACION_INTERNA = "comercializacion_interna"
    COMERCIALIZACION_EXTERNA = "comercializacion_externa"
    SERVICIOS = "servicios"


class FiscalObligation(VSLBaseModel):
    """Fiscal obligation under LOH."""
    name: str = Field(..., description="Obligation name")
    rate: str = Field(..., description="Rate or amount")
    base: str = Field(..., description="Calculation base")
    loh_article: int = Field(..., ge=0, description="LOH article")
    frequency: str = Field(..., description="Payment frequency")
    applicable: bool = Field(default=True, description="Whether applicable")


class EmpresaMixtaAnalysis(VSLBaseModel):
    """Empresa mixta (mixed company) analysis."""
    pdvsa_participation: float = Field(..., ge=0, le=100, description="PDVSA participation %")
    private_participation: float = Field(..., ge=0, le=100, description="Private participation %")
    art_9_loh_compliant: bool = Field(..., description="Art. 9 LOH compliance")
    control_analysis: str = Field(default="", description="Control analysis")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


class HydrocarbonsAnalysisResponse(VSLBaseModel):
    """Hydrocarbons analysis response."""
    activity_type: HydrocarbonsActivityType = Field(..., description="Activity type")
    reserved_to_state: bool = Field(..., description="Whether reserved to state")
    empresa_mixta_required: bool = Field(..., description="Whether empresa mixta required")
    private_participation_allowed: bool = Field(..., description="Whether private participation allowed")
    applicable_loh_articles: List[int] = Field(default_factory=list, description="Applicable LOH articles")
    fiscal_obligations: List[FiscalObligation] = Field(default_factory=list, description="Fiscal obligations")
    empresa_mixta: Optional[EmpresaMixtaAnalysis] = Field(default=None, description="Empresa mixta analysis")
    environmental_requirements: List[str] = Field(default_factory=list, description="Environmental requirements")
    permits_required: List[str] = Field(default_factory=list, description="Required permits")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")


# ═══════════════════════════════════════════════════════════════════════════════
#                         LAW GENERATION MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class LegalArticle(VSLBaseModel):
    """Article in a legal instrument."""
    numero: int = Field(..., ge=1, description="Article number")
    titulo: str = Field(..., description="Article title")
    contenido: str = Field(..., description="Article content")
    tipo: str = Field(..., description="Article type")
    crbv_fundamento: List[int] = Field(default_factory=list, description="CRBV basis")
    notas: str = Field(default="", description="Notes")


class ImplementationPhase(VSLBaseModel):
    """Implementation phase."""
    phase_number: int = Field(..., ge=1, description="Phase number")
    name: str = Field(..., description="Phase name")
    duration_days: int = Field(..., ge=0, description="Duration in days")
    tasks: List[str] = Field(default_factory=list, description="Tasks")
    deliverables: List[str] = Field(default_factory=list, description="Deliverables")
    responsible: str = Field(default="", description="Responsible party")


class ImplementationRoadmap(VSLBaseModel):
    """Implementation roadmap for legal instrument."""
    total_days: int = Field(..., ge=0, description="Total implementation days")
    phases: List[ImplementationPhase] = Field(default_factory=list, description="Phases")
    milestones: List[str] = Field(default_factory=list, description="Key milestones")
    risks: List[str] = Field(default_factory=list, description="Implementation risks")


class LawGenerationResponse(VSLBaseModel):
    """Law generation response."""
    instrument_type: NormType = Field(..., description="Instrument type")
    title: str = Field(..., description="Instrument title")
    full_text: str = Field(..., description="Full instrument text")
    article_count: int = Field(..., ge=0, description="Number of articles")
    articles: List[LegalArticle] = Field(default_factory=list, description="Articles")
    exposicion_motivos: str = Field(default="", description="Explanatory statement")
    roadmap: Optional[ImplementationRoadmap] = Field(default=None, description="Implementation roadmap")


# ═══════════════════════════════════════════════════════════════════════════════
#                         UNIFIED ANALYSIS RESPONSE
# ═══════════════════════════════════════════════════════════════════════════════

class AnalysisResponse(VSLBaseModel):
    """Complete analysis response for all workflows."""
    case_name: str = Field(..., description="Case name")
    workflow_type: WorkflowType = Field(..., description="Workflow executed")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp")
    success: bool = Field(..., description="Whether analysis succeeded")
    modules_run: List[str] = Field(default_factory=list, description="Modules executed")

    # Analysis results (optional based on workflow)
    constitutional_analysis: Optional[ConstitutionalAnalysis] = Field(default=None)
    constitutional_tests: Optional[ConstitutionalTestResponse] = Field(default=None)
    gaceta_verification: Optional[GacetaVerificationResponse] = Field(default=None)
    tsj_research: Optional[TSJResearchResponse] = Field(default=None)
    tsj_prediction: Optional[TSJPrediction] = Field(default=None)
    voting_map: Optional[VotingMapResponse] = Field(default=None)
    contract_review: Optional[ContractReviewResponse] = Field(default=None)
    hydrocarbons_analysis: Optional[HydrocarbonsAnalysisResponse] = Field(default=None)
    law_generation: Optional[LawGenerationResponse] = Field(default=None)

    # Output
    report_path: Optional[str] = Field(default=None, description="Path to generated report")
    errors: List[str] = Field(default_factory=list, description="Errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Warnings")


# ═══════════════════════════════════════════════════════════════════════════════
#                         API STATUS MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ModuleStatus(VSLBaseModel):
    """Individual module status."""
    name: str = Field(..., description="Module name")
    available: bool = Field(..., description="Whether module is available")
    version: str = Field(default="", description="Module version")
    capabilities: List[str] = Field(default_factory=list, description="Module capabilities")


class SystemStatus(VSLBaseModel):
    """System status response."""
    status: str = Field(..., description="System status")
    version: str = Field(..., description="System version")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    modules: List[ModuleStatus] = Field(default_factory=list, description="Module statuses")
    workflows_available: List[str] = Field(default_factory=list, description="Available workflows")
    pydantic_available: bool = Field(default=PYDANTIC_AVAILABLE)


class ErrorResponse(VSLBaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[str] = Field(default=None, description="Additional details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
#                         HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_statistics() -> Dict[str, Any]:
    """Get unified data model statistics."""
    return {
        "module": "Unified Data Models",
        "version": __version__,
        "pydantic_available": PYDANTIC_AVAILABLE,
        "enums": [
            "WorkflowType", "NormType", "RiskLevel", "ComplianceStatus",
            "Sector", "TSJSala", "UrgencyLevel", "HydrocarbonsActivityType"
        ],
        "models": {
            "intake": ["IntakeRequest", "PreflightCheck", "PreflightResponse"],
            "constitutional": ["ConstitutionalConflict", "ConstitutionalAnalysis", "ConstitutionalTest", "ConstitutionalTestResponse"],
            "tsj": ["TSJDecision", "TSJResearchResponse", "TSJPrediction"],
            "gaceta": ["GacetaNorm", "GacetaVerificationResponse"],
            "voting": ["VotingRequirement", "PoliticalFeasibility", "VotingMapResponse"],
            "contracts": ["ContractParty", "ClauseAnalysis", "RiskPattern", "ContractReviewResponse"],
            "hydrocarbons": ["FiscalObligation", "EmpresaMixtaAnalysis", "HydrocarbonsAnalysisResponse"],
            "law_generation": ["LegalArticle", "ImplementationPhase", "ImplementationRoadmap", "LawGenerationResponse"],
            "response": ["AnalysisResponse", "ModuleStatus", "SystemStatus", "ErrorResponse"]
        },
        "features": [
            "Pydantic v2 validation (when available)",
            "OpenAPI schema generation",
            "JSON serialization",
            "Type safety",
            "Consistent enums across modules"
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_statistics(), indent=2))
