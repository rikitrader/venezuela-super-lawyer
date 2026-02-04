#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Contract Review Module (Module 9)

Specialized contract analysis and compliance review for Venezuelan law.
Supports contract review, risk assessment, clause analysis, and compliance checking.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


# ═══════════════════════════════════════════════════════════════════════════════
#                         ENUMS AND CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class ContractType(Enum):
    """Types of contracts."""
    COMPRAVENTA = "Compraventa"
    ARRENDAMIENTO = "Arrendamiento"
    PRESTAMO = "Préstamo"
    SERVICIO = "Prestación de Servicios"
    TRABAJO = "Contrato de Trabajo"
    SOCIEDAD = "Sociedad"
    ASOCIACION = "Asociación Estratégica"
    JOINT_VENTURE = "Joint Venture"
    FRANQUICIA = "Franquicia"
    DISTRIBUCION = "Distribución"
    SUMINISTRO = "Suministro"
    OBRA = "Obra"
    MANDATO = "Mandato"
    FIANZA = "Fianza"
    HIPOTECA = "Hipoteca"
    PRENDA = "Prenda"
    OTRO = "Otro"


class ClauseType(Enum):
    """Types of contract clauses."""
    OBJETO = "Objeto"
    PRECIO = "Precio y Forma de Pago"
    PLAZO = "Plazo y Duración"
    OBLIGACIONES = "Obligaciones de las Partes"
    GARANTIAS = "Garantías"
    PENALIDADES = "Penalidades e Incumplimiento"
    RESOLUCION = "Resolución y Terminación"
    FUERZA_MAYOR = "Fuerza Mayor"
    CONFIDENCIALIDAD = "Confidencialidad"
    PROPIEDAD_INTELECTUAL = "Propiedad Intelectual"
    ARBITRAJE = "Arbitraje"
    JURISDICCION = "Jurisdicción"
    LEY_APLICABLE = "Ley Aplicable"
    NOTIFICACIONES = "Notificaciones"
    CESION = "Cesión"
    MODIFICACIONES = "Modificaciones"
    INTEGRIDAD = "Cláusula de Integridad"
    INTERPRETACION = "Interpretación"


class RiskLevel(Enum):
    """Risk levels for clauses."""
    LOW = "Bajo"
    MEDIUM = "Medio"
    HIGH = "Alto"
    CRITICAL = "Crítico"


class ComplianceStatus(Enum):
    """Compliance status."""
    COMPLIANT = "Cumple"
    NON_COMPLIANT = "No Cumple"
    PARTIAL = "Parcialmente"
    NOT_APPLICABLE = "No Aplica"
    REQUIRES_REVIEW = "Requiere Revisión"


# ═══════════════════════════════════════════════════════════════════════════════
#                         LEGAL REQUIREMENTS DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

# Mandatory clauses by contract type
MANDATORY_CLAUSES = {
    ContractType.COMPRAVENTA: ["objeto", "precio", "entrega", "vicios_ocultos"],
    ContractType.ARRENDAMIENTO: ["objeto", "canon", "plazo", "uso", "mantenimiento"],
    ContractType.TRABAJO: ["objeto", "salario", "jornada", "beneficios", "terminacion"],
    ContractType.SERVICIO: ["objeto", "precio", "plazo", "entregables"],
    ContractType.SOCIEDAD: ["objeto_social", "capital", "administracion", "utilidades", "disolucion"],
    ContractType.JOINT_VENTURE: ["objeto", "aportes", "administracion", "utilidades", "terminacion", "ley_aplicable"],
}

# Venezuelan law compliance checks
COMPLIANCE_CHECKS = {
    "moneda": {
        "name": "Moneda de Pago",
        "rule": "Verificar si el pago en moneda extranjera está permitido (Art. 128 Ley BCV)",
        "risk_if_fail": RiskLevel.MEDIUM
    },
    "arbitraje": {
        "name": "Cláusula Arbitral",
        "rule": "Verificar cumplimiento de Ley de Arbitraje Comercial y requisitos de arbitrabilidad",
        "risk_if_fail": RiskLevel.MEDIUM
    },
    "jurisdiccion": {
        "name": "Jurisdicción",
        "rule": "Contratos con el Estado: jurisdicción venezolana obligatoria (Art. 151 CRBV)",
        "risk_if_fail": RiskLevel.HIGH
    },
    "ley_aplicable": {
        "name": "Ley Aplicable",
        "rule": "Verificar si la ley extranjera es aplicable según Ley de DIPr",
        "risk_if_fail": RiskLevel.MEDIUM
    },
    "registro": {
        "name": "Registro",
        "rule": "Contratos sobre inmuebles requieren registro (Art. 1920 CC)",
        "risk_if_fail": RiskLevel.HIGH
    },
    "capacidad": {
        "name": "Capacidad de las Partes",
        "rule": "Verificar capacidad legal (mayores de edad, empresas válidamente constituidas)",
        "risk_if_fail": RiskLevel.CRITICAL
    },
    "objeto_licito": {
        "name": "Objeto Lícito",
        "rule": "El objeto debe ser lícito, posible, determinado o determinable (Art. 1155 CC)",
        "risk_if_fail": RiskLevel.CRITICAL
    },
    "causa_licita": {
        "name": "Causa Lícita",
        "rule": "La causa del contrato debe ser lícita (Art. 1157 CC)",
        "risk_if_fail": RiskLevel.CRITICAL
    },
    "clausula_penal": {
        "name": "Cláusula Penal",
        "rule": "Verificar proporcionalidad y límites de la cláusula penal",
        "risk_if_fail": RiskLevel.MEDIUM
    },
    "ilat": {
        "name": "ILAT - Prevención Lavado",
        "rule": "Verificar cumplimiento de debida diligencia en contratos de alto valor",
        "risk_if_fail": RiskLevel.HIGH
    }
}

# Risk indicators in contract text
RISK_PATTERNS = [
    {
        "pattern": r"renuncia.*derecho",
        "description": "Renuncia de derechos",
        "risk": RiskLevel.HIGH,
        "recommendation": "Verificar que la renuncia no afecte derechos irrenunciables"
    },
    {
        "pattern": r"sin.*limit(e|ación).*responsabilidad",
        "description": "Responsabilidad ilimitada",
        "risk": RiskLevel.CRITICAL,
        "recommendation": "Establecer límites a la responsabilidad"
    },
    {
        "pattern": r"exclusiva.*jurisdicción.*extranjera",
        "description": "Jurisdicción extranjera exclusiva",
        "risk": RiskLevel.HIGH,
        "recommendation": "Verificar aplicabilidad según interés público"
    },
    {
        "pattern": r"modificar.*unilateral",
        "description": "Modificación unilateral",
        "risk": RiskLevel.HIGH,
        "recommendation": "Establecer procedimiento bilateral de modificación"
    },
    {
        "pattern": r"renovación.*automática.*sin.*aviso",
        "description": "Renovación automática sin aviso",
        "risk": RiskLevel.MEDIUM,
        "recommendation": "Incluir mecanismo de notificación previa"
    },
    {
        "pattern": r"indemnidad.*total",
        "description": "Cláusula de indemnidad amplia",
        "risk": RiskLevel.HIGH,
        "recommendation": "Limitar alcance de la indemnidad"
    },
    {
        "pattern": r"cesión.*libre.*sin.*consentimiento",
        "description": "Cesión libre sin consentimiento",
        "risk": RiskLevel.MEDIUM,
        "recommendation": "Requerir consentimiento para cesión"
    },
    {
        "pattern": r"confidencialidad.*perpetua|indefinida",
        "description": "Confidencialidad perpetua",
        "risk": RiskLevel.MEDIUM,
        "recommendation": "Establecer plazo razonable de confidencialidad"
    },
    {
        "pattern": r"penalidad.*desproporcionada|\d{3,}%",
        "description": "Penalidad potencialmente excesiva",
        "risk": RiskLevel.HIGH,
        "recommendation": "Verificar proporcionalidad de la penalidad"
    },
    {
        "pattern": r"terminación.*inmediata.*sin.*causa",
        "description": "Terminación sin causa y sin preaviso",
        "risk": RiskLevel.HIGH,
        "recommendation": "Establecer preaviso razonable"
    }
]


# ═══════════════════════════════════════════════════════════════════════════════
#                         DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ClauseAnalysis:
    """Analysis of a contract clause."""
    tipo: ClauseType
    texto: str
    presente: bool
    risk_level: RiskLevel
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    legal_basis: str = ""

    def to_dict(self) -> Dict:
        return {
            "tipo": self.tipo.value,
            "texto_extracto": self.texto[:200] + "..." if len(self.texto) > 200 else self.texto,
            "presente": self.presente,
            "risk_level": self.risk_level.value,
            "issues": self.issues,
            "recommendations": self.recommendations,
            "legal_basis": self.legal_basis
        }


@dataclass
class ComplianceCheck:
    """Result of a compliance check."""
    check_name: str
    status: ComplianceStatus
    details: str
    risk_level: RiskLevel
    legal_basis: str = ""

    def to_dict(self) -> Dict:
        return {
            "check_name": self.check_name,
            "status": self.status.value,
            "details": self.details,
            "risk_level": self.risk_level.value,
            "legal_basis": self.legal_basis
        }


@dataclass
class ContractReviewResult:
    """Complete contract review result."""
    case_name: str
    contract_type: ContractType
    parties: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Analysis results
    overall_risk: RiskLevel = RiskLevel.LOW
    compliance_score: float = 0.0
    clause_analysis: List[ClauseAnalysis] = field(default_factory=list)
    compliance_checks: List[ComplianceCheck] = field(default_factory=list)
    risk_findings: List[Dict] = field(default_factory=list)
    missing_clauses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict:
        return {
            "case_name": self.case_name,
            "contract_type": self.contract_type.value,
            "parties": self.parties,
            "timestamp": self.timestamp,
            "overall_risk": self.overall_risk.value,
            "compliance_score": self.compliance_score,
            "clause_analysis": [c.to_dict() for c in self.clause_analysis],
            "compliance_checks": [c.to_dict() for c in self.compliance_checks],
            "risk_findings": self.risk_findings,
            "missing_clauses": self.missing_clauses,
            "recommendations": self.recommendations,
            "summary": self.summary
        }

    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = []
        lines.append(f"# Contract Review: {self.case_name}")
        lines.append(f"\n**Date:** {self.timestamp}")
        lines.append(f"**Contract Type:** {self.contract_type.value}")
        lines.append(f"**Parties:** {', '.join(self.parties)}")
        lines.append(f"\n## Overall Assessment")
        lines.append(f"- **Risk Level:** {self.overall_risk.value}")
        lines.append(f"- **Compliance Score:** {self.compliance_score:.1f}%")
        lines.append(f"\n{self.summary}")

        if self.risk_findings:
            lines.append(f"\n## Risk Findings")
            for finding in self.risk_findings:
                lines.append(f"- [{finding.get('risk', 'N/A')}] {finding.get('description', '')}")
                if finding.get('recommendation'):
                    lines.append(f"  - _Recomendación: {finding['recommendation']}_")

        if self.missing_clauses:
            lines.append(f"\n## Missing Clauses")
            for clause in self.missing_clauses:
                lines.append(f"- {clause}")

        if self.compliance_checks:
            lines.append(f"\n## Compliance Checks")
            for check in self.compliance_checks:
                status_icon = "✓" if check.status == ComplianceStatus.COMPLIANT else ("⚠" if check.status == ComplianceStatus.PARTIAL else "✗")
                lines.append(f"- [{status_icon}] {check.check_name}: {check.status.value}")
                if check.details:
                    lines.append(f"  - {check.details}")

        if self.recommendations:
            lines.append(f"\n## Recommendations")
            for i, rec in enumerate(self.recommendations, 1):
                lines.append(f"{i}. {rec}")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#                         ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def detect_contract_type(text: str) -> ContractType:
    """Detect contract type from text."""
    text_lower = text.lower()

    type_indicators = {
        ContractType.COMPRAVENTA: ["compraventa", "vender", "comprar", "precio de venta"],
        ContractType.ARRENDAMIENTO: ["arrendamiento", "arrendar", "canon", "inquilino", "arrendador"],
        ContractType.TRABAJO: ["contrato de trabajo", "empleador", "trabajador", "salario", "jornada laboral"],
        ContractType.SERVICIO: ["prestación de servicios", "servicios profesionales", "honorarios"],
        ContractType.SOCIEDAD: ["constitución de sociedad", "capital social", "acciones", "socios"],
        ContractType.JOINT_VENTURE: ["joint venture", "asociación estratégica", "consorcio"],
        ContractType.FRANQUICIA: ["franquicia", "franquiciante", "franquiciado"],
        ContractType.DISTRIBUCION: ["distribución", "distribuidor", "territorio exclusivo"],
        ContractType.SUMINISTRO: ["suministro", "proveedor", "abastecimiento"],
        ContractType.OBRA: ["contrato de obra", "construcción", "contratista", "obra civil"],
        ContractType.PRESTAMO: ["préstamo", "mutuante", "mutuario", "intereses"],
    }

    for contract_type, indicators in type_indicators.items():
        for indicator in indicators:
            if indicator in text_lower:
                return contract_type

    return ContractType.OTRO


def extract_parties(text: str) -> List[str]:
    """Extract party names from contract text."""
    parties = []

    # Common patterns for party identification
    patterns = [
        r"(?:entre|por una parte)[,:]?\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s,\.]+?)(?:,\s*(?:identificad|representad|en adelante))",
        r"(?:PARTE [A-Z]+|PRIMERA PARTE|SEGUNDA PARTE)[,:]?\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s,\.]+?)(?:,)",
        r'"([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]+)".*?(?:en adelante|denominad)',
        r"(?:contratante|arrendador|arrendatario|vendedor|comprador|empleador|trabajador)[,:]?\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s,\.]+?)(?:,)"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            party = match.strip().strip(',').strip()
            if party and len(party) > 3 and party not in parties:
                parties.append(party)

    # If no parties found, return placeholder
    if not parties:
        parties = ["Parte A (no identificada)", "Parte B (no identificada)"]

    return parties[:4]  # Maximum 4 parties


def analyze_clauses(text: str, contract_type: ContractType) -> List[ClauseAnalysis]:
    """Analyze contract clauses."""
    analyses = []
    text_lower = text.lower()

    # Define clause patterns
    clause_patterns = {
        ClauseType.OBJETO: {
            "patterns": ["objeto del contrato", "objeto:", "cláusula.*objeto", "el objeto"],
            "required": True
        },
        ClauseType.PRECIO: {
            "patterns": ["precio", "contraprestación", "monto", "valor del contrato"],
            "required": contract_type in [ContractType.COMPRAVENTA, ContractType.SERVICIO]
        },
        ClauseType.PLAZO: {
            "patterns": ["plazo", "duración", "vigencia", "término"],
            "required": True
        },
        ClauseType.GARANTIAS: {
            "patterns": ["garantía", "fianza", "aval", "caución"],
            "required": False
        },
        ClauseType.PENALIDADES: {
            "patterns": ["penalidad", "incumplimiento", "indemnización", "daños y perjuicios"],
            "required": False
        },
        ClauseType.RESOLUCION: {
            "patterns": ["resolución", "terminación", "rescisión", "fin del contrato"],
            "required": True
        },
        ClauseType.FUERZA_MAYOR: {
            "patterns": ["fuerza mayor", "caso fortuito", "causas no imputables"],
            "required": False
        },
        ClauseType.CONFIDENCIALIDAD: {
            "patterns": ["confidencialidad", "secreto", "información confidencial"],
            "required": False
        },
        ClauseType.ARBITRAJE: {
            "patterns": ["arbitraje", "tribunal arbitral", "laudo"],
            "required": False
        },
        ClauseType.JURISDICCION: {
            "patterns": ["jurisdicción", "tribunales competentes", "fuero"],
            "required": True
        },
        ClauseType.LEY_APLICABLE: {
            "patterns": ["ley aplicable", "legislación aplicable", "derecho aplicable"],
            "required": True
        }
    }

    for clause_type, config in clause_patterns.items():
        found = False
        extracted_text = ""

        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                found = True
                # Try to extract the clause text
                match = re.search(
                    f"(?:{pattern}).*?(?=cláusula|artículo|\\n\\n|$)",
                    text_lower,
                    re.DOTALL
                )
                if match:
                    extracted_text = match.group(0)[:500]
                break

        risk = RiskLevel.LOW
        issues = []
        recommendations = []

        if config["required"] and not found:
            risk = RiskLevel.HIGH
            issues.append(f"Cláusula requerida no encontrada: {clause_type.value}")
            recommendations.append(f"Incluir cláusula de {clause_type.value}")

        analyses.append(ClauseAnalysis(
            tipo=clause_type,
            texto=extracted_text,
            presente=found,
            risk_level=risk,
            issues=issues,
            recommendations=recommendations
        ))

    return analyses


def check_compliance(text: str, contract_type: ContractType, parties: List[str]) -> List[ComplianceCheck]:
    """Run compliance checks on contract."""
    checks = []
    text_lower = text.lower()

    # Check for foreign currency clauses
    if re.search(r"dólar|usd|euro|eur|\$", text_lower):
        status = ComplianceStatus.REQUIRES_REVIEW
        details = "Contrato contiene referencias a moneda extranjera - verificar cumplimiento Art. 128 Ley BCV"
    else:
        status = ComplianceStatus.COMPLIANT
        details = "No se detectaron cláusulas en moneda extranjera"

    checks.append(ComplianceCheck(
        check_name="Moneda de Pago",
        status=status,
        details=details,
        risk_level=COMPLIANCE_CHECKS["moneda"]["risk_if_fail"],
        legal_basis="Art. 128 Ley BCV"
    ))

    # Check jurisdiction
    if "jurisdicción exclusiva" in text_lower and ("extranjera" in text_lower or "nueva york" in text_lower or "delaware" in text_lower):
        checks.append(ComplianceCheck(
            check_name="Jurisdicción",
            status=ComplianceStatus.REQUIRES_REVIEW,
            details="Cláusula de jurisdicción extranjera exclusiva detectada",
            risk_level=RiskLevel.HIGH,
            legal_basis="Art. 151 CRBV (contratos de interés público)"
        ))
    elif "tribunales de venezuela" in text_lower or "jurisdicción venezolana" in text_lower:
        checks.append(ComplianceCheck(
            check_name="Jurisdicción",
            status=ComplianceStatus.COMPLIANT,
            details="Jurisdicción venezolana establecida",
            risk_level=RiskLevel.LOW,
            legal_basis="Art. 151 CRBV"
        ))
    else:
        checks.append(ComplianceCheck(
            check_name="Jurisdicción",
            status=ComplianceStatus.NOT_APPLICABLE,
            details="No se encontró cláusula de jurisdicción específica",
            risk_level=RiskLevel.MEDIUM,
            legal_basis="Art. 151 CRBV"
        ))

    # Check arbitration clause
    if "arbitraje" in text_lower:
        if "centro de arbitraje" in text_lower or "cámara de comercio" in text_lower:
            status = ComplianceStatus.COMPLIANT
            details = "Cláusula arbitral con institución identificada"
        else:
            status = ComplianceStatus.PARTIAL
            details = "Cláusula arbitral presente pero sin institución específica"

        checks.append(ComplianceCheck(
            check_name="Cláusula Arbitral",
            status=status,
            details=details,
            risk_level=RiskLevel.MEDIUM,
            legal_basis="Ley de Arbitraje Comercial"
        ))

    # Check for objeto lícito
    prohibited_terms = ["narcóticos", "armas ilegales", "contrabando", "lavado de dinero"]
    if any(term in text_lower for term in prohibited_terms):
        checks.append(ComplianceCheck(
            check_name="Objeto Lícito",
            status=ComplianceStatus.NON_COMPLIANT,
            details="Posible objeto ilícito detectado en el contrato",
            risk_level=RiskLevel.CRITICAL,
            legal_basis="Art. 1155 Código Civil"
        ))
    else:
        checks.append(ComplianceCheck(
            check_name="Objeto Lícito",
            status=ComplianceStatus.COMPLIANT,
            details="No se detectaron indicios de objeto ilícito",
            risk_level=RiskLevel.LOW,
            legal_basis="Art. 1155 Código Civil"
        ))

    # Check for property registration requirement
    if contract_type == ContractType.COMPRAVENTA and ("inmueble" in text_lower or "terreno" in text_lower or "edificio" in text_lower):
        if "registro" in text_lower:
            status = ComplianceStatus.COMPLIANT
            details = "Contrato de inmueble con mención de registro"
        else:
            status = ComplianceStatus.REQUIRES_REVIEW
            details = "Contrato de inmueble - verificar registro obligatorio"

        checks.append(ComplianceCheck(
            check_name="Registro de Inmueble",
            status=status,
            details=details,
            risk_level=RiskLevel.HIGH,
            legal_basis="Art. 1920 Código Civil"
        ))

    return checks


def find_risk_patterns(text: str) -> List[Dict]:
    """Find risk patterns in contract text."""
    findings = []
    text_lower = text.lower()

    for pattern_config in RISK_PATTERNS:
        if re.search(pattern_config["pattern"], text_lower):
            findings.append({
                "description": pattern_config["description"],
                "risk": pattern_config["risk"].value,
                "recommendation": pattern_config["recommendation"],
                "pattern_matched": pattern_config["pattern"]
            })

    return findings


def calculate_overall_risk(
    clause_analyses: List[ClauseAnalysis],
    compliance_checks: List[ComplianceCheck],
    risk_findings: List[Dict]
) -> Tuple[RiskLevel, float]:
    """Calculate overall risk level and compliance score."""

    # Count issues by severity
    critical_count = 0
    high_count = 0
    medium_count = 0

    # From clause analyses
    for clause in clause_analyses:
        if clause.risk_level == RiskLevel.CRITICAL:
            critical_count += 1
        elif clause.risk_level == RiskLevel.HIGH:
            high_count += 1
        elif clause.risk_level == RiskLevel.MEDIUM:
            medium_count += 1

    # From compliance checks
    for check in compliance_checks:
        if check.status == ComplianceStatus.NON_COMPLIANT:
            if check.risk_level == RiskLevel.CRITICAL:
                critical_count += 1
            elif check.risk_level == RiskLevel.HIGH:
                high_count += 1
        elif check.status == ComplianceStatus.REQUIRES_REVIEW:
            medium_count += 1

    # From risk findings
    for finding in risk_findings:
        if finding["risk"] == "Crítico":
            critical_count += 1
        elif finding["risk"] == "Alto":
            high_count += 1
        elif finding["risk"] == "Medio":
            medium_count += 1

    # Determine overall risk
    if critical_count > 0:
        overall_risk = RiskLevel.CRITICAL
    elif high_count >= 2:
        overall_risk = RiskLevel.HIGH
    elif high_count >= 1 or medium_count >= 3:
        overall_risk = RiskLevel.MEDIUM
    else:
        overall_risk = RiskLevel.LOW

    # Calculate compliance score
    total_checks = len(compliance_checks)
    compliant_checks = sum(1 for c in compliance_checks if c.status == ComplianceStatus.COMPLIANT)
    partial_checks = sum(1 for c in compliance_checks if c.status == ComplianceStatus.PARTIAL) * 0.5

    if total_checks > 0:
        compliance_score = ((compliant_checks + partial_checks) / total_checks) * 100
    else:
        compliance_score = 100.0

    return overall_risk, compliance_score


def review_contract(
    text: str,
    case_name: str = "Contract Review",
    contract_type: Optional[ContractType] = None
) -> ContractReviewResult:
    """
    Run complete contract review.

    Args:
        text: Contract text to analyze
        case_name: Name for the review
        contract_type: Type of contract (auto-detected if not provided)

    Returns:
        ContractReviewResult with complete analysis
    """

    # Detect contract type if not provided
    if contract_type is None:
        contract_type = detect_contract_type(text)

    # Extract parties
    parties = extract_parties(text)

    # Analyze clauses
    clause_analyses = analyze_clauses(text, contract_type)

    # Run compliance checks
    compliance_checks = check_compliance(text, contract_type, parties)

    # Find risk patterns
    risk_findings = find_risk_patterns(text)

    # Calculate overall risk
    overall_risk, compliance_score = calculate_overall_risk(
        clause_analyses, compliance_checks, risk_findings
    )

    # Find missing mandatory clauses
    mandatory = MANDATORY_CLAUSES.get(contract_type, [])
    missing = []
    for clause in clause_analyses:
        if not clause.presente and clause.issues:
            missing.append(clause.tipo.value)

    # Generate recommendations
    recommendations = []
    if overall_risk in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
        recommendations.append("Se recomienda revisión legal exhaustiva antes de firmar")
    if missing:
        recommendations.append(f"Agregar cláusulas faltantes: {', '.join(missing)}")
    for finding in risk_findings:
        recommendations.append(finding["recommendation"])

    # Generate summary
    if overall_risk == RiskLevel.CRITICAL:
        summary = "⚠️ ALERTA CRÍTICA: El contrato presenta riesgos significativos que requieren atención inmediata."
    elif overall_risk == RiskLevel.HIGH:
        summary = "⚠️ RIESGO ALTO: El contrato requiere modificaciones importantes antes de su suscripción."
    elif overall_risk == RiskLevel.MEDIUM:
        summary = "⚡ RIESGO MEDIO: El contrato es aceptable con algunas mejoras recomendadas."
    else:
        summary = "✓ RIESGO BAJO: El contrato cumple con los requisitos básicos de forma adecuada."

    return ContractReviewResult(
        case_name=case_name,
        contract_type=contract_type,
        parties=parties,
        overall_risk=overall_risk,
        compliance_score=compliance_score,
        clause_analysis=clause_analyses,
        compliance_checks=compliance_checks,
        risk_findings=risk_findings,
        missing_clauses=missing,
        recommendations=recommendations,
        summary=summary
    )


def get_statistics() -> Dict:
    """Get contract review module statistics."""
    return {
        "contract_types_supported": len(ContractType),
        "clause_types_analyzed": len(ClauseType),
        "compliance_checks_available": len(COMPLIANCE_CHECKS),
        "risk_patterns_monitored": len(RISK_PATTERNS)
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for contract review."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Venezuela Super Lawyer - Contract Review (Module 9)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Review command
    review_parser = subparsers.add_parser("review", help="Review a contract")
    review_parser.add_argument("--text", "-t", help="Contract text")
    review_parser.add_argument("--file", "-f", help="Contract file path")
    review_parser.add_argument("--name", "-n", default="Contract Review",
                               help="Review name")
    review_parser.add_argument("--type", "-T",
                               choices=[t.name for t in ContractType],
                               help="Contract type (auto-detected if not provided)")

    # Stats command
    subparsers.add_parser("stats", help="Get module statistics")

    # Output format
    parser.add_argument("--output", "-o", choices=["json", "text", "markdown"],
                       default="json", help="Output format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "review":
        # Get text from argument or file
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        elif args.text:
            text = args.text
        else:
            print("Error: Provide --text or --file")
            return

        # Get contract type
        contract_type = None
        if args.type:
            contract_type = ContractType[args.type]

        result = review_contract(text, args.name, contract_type)

        if args.output == "json":
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        elif args.output == "markdown":
            print(result.to_markdown())
        else:
            print(f"\n{'='*60}")
            print(f"CONTRACT REVIEW: {result.case_name}")
            print(f"{'='*60}")
            print(f"Type: {result.contract_type.value}")
            print(f"Parties: {', '.join(result.parties)}")
            print(f"Overall Risk: {result.overall_risk.value}")
            print(f"Compliance Score: {result.compliance_score:.1f}%")
            print(f"\n{result.summary}")
            if result.risk_findings:
                print(f"\nRisk Findings:")
                for finding in result.risk_findings:
                    print(f"  - [{finding['risk']}] {finding['description']}")
            if result.recommendations:
                print(f"\nRecommendations:")
                for rec in result.recommendations:
                    print(f"  - {rec}")

    elif args.command == "stats":
        stats = get_statistics()
        if args.output == "json":
            print(json.dumps(stats, indent=2))
        else:
            print("\nContract Review Module Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
