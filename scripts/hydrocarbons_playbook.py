#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Module 7: Hydrocarbons Law Playbook

Specialized analysis engine for Venezuelan oil & gas sector legal matters.
Covers LOH, empresas mixtas, PDVSA structure, royalties, fiscal regime,
environmental compliance, and sector-specific jurisprudence.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import sys
import json
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

class ActivityType(Enum):
    """Types of hydrocarbon activities."""
    EXPLORACION = "Exploración"
    EXPLOTACION = "Explotación"
    REFINACION = "Refinación"
    INDUSTRIALIZACION = "Industrialización"
    TRANSPORTE = "Transporte"
    ALMACENAMIENTO = "Almacenamiento"
    COMERCIALIZACION_INTERNA = "Comercialización Interna"
    COMERCIALIZACION_EXTERNA = "Comercialización Externa"
    SERVICIOS = "Servicios Petroleros"


class ContractType(Enum):
    """Types of hydrocarbon contracts."""
    EMPRESA_MIXTA = "Empresa Mixta"
    SERVICIO = "Contrato de Servicio"
    ASOCIACION_ESTRATEGICA = "Asociación Estratégica"
    LICENCIA = "Licencia"
    PERMISO = "Permiso"
    AUTORIZACION = "Autorización"


class RegimeType(Enum):
    """Fiscal regime types."""
    LOH_2001 = "LOH 2001"
    LOH_2006 = "LOH 2006 (Reforma)"
    LOHG = "Ley Orgánica de Hidrocarburos Gaseosos"
    REGIMEN_ESPECIAL = "Régimen Especial Faja"


# ═══════════════════════════════════════════════════════════════════════════════
#                         LEGAL FRAMEWORK DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

# Key articles from LOH (Ley Orgánica de Hidrocarburos)
LOH_ARTICLES = {
    1: {
        "titulo": "Objeto",
        "contenido": "La presente Ley tiene por objeto regular todo lo relativo a la exploración, explotación, refinación, industrialización, transporte, almacenamiento y comercialización de los hidrocarburos.",
        "keywords": ["objeto", "alcance", "regulación"]
    },
    2: {
        "titulo": "Reserva al Estado",
        "contenido": "Los yacimientos de hidrocarburos existentes en el territorio nacional pertenecen a la República, son bienes del dominio público y, por tanto, inalienables e imprescriptibles.",
        "keywords": ["reserva", "dominio público", "propiedad"]
    },
    3: {
        "titulo": "Actividades Reservadas",
        "contenido": "Las actividades relativas a la exploración en busca de yacimientos de los hidrocarburos comprendidos en esta Ley, la extracción de ellos en estado natural, su recolección, transporte y almacenamiento iniciales, están reservadas al Estado.",
        "keywords": ["reserva", "actividades primarias", "estado"]
    },
    9: {
        "titulo": "Empresas Mixtas",
        "contenido": "El Estado realizará las actividades señaladas en el artículo 3 de esta Ley, directamente por el Ejecutivo Nacional o a través de empresas de su exclusiva propiedad. Igualmente podrá hacerlo mediante empresas donde tenga el control de sus decisiones, por mantener una participación mayor del cincuenta por ciento (50%) del capital social.",
        "keywords": ["empresas mixtas", "participación estatal", "control"]
    },
    22: {
        "titulo": "Participación del Sector Privado",
        "contenido": "Las empresas que realicen las actividades de refinación, industrialización, transporte, almacenamiento y comercialización de hidrocarburos no estarán sujetas a las limitaciones establecidas en el artículo 9 de esta Ley.",
        "keywords": ["sector privado", "actividades secundarias"]
    },
    44: {
        "titulo": "Regalía",
        "contenido": "Los titulares de las actividades de producción de hidrocarburos pagarán al Estado una regalía equivalente al treinta por ciento (30%) de los hidrocarburos líquidos extraídos de cualquier yacimiento.",
        "keywords": ["regalía", "30%", "producción"]
    },
    45: {
        "titulo": "Regalía Adicional",
        "contenido": "El Ejecutivo Nacional podrá elevar la regalía hasta un máximo de treinta y tres y un tercio por ciento (33 1/3%), cuando así lo considere conveniente para el interés nacional.",
        "keywords": ["regalía adicional", "33.33%", "interés nacional"]
    },
    46: {
        "titulo": "Impuesto de Extracción",
        "contenido": "Los titulares de las actividades de producción de hidrocarburos pagarán al Estado un impuesto de extracción equivalente a un tercio (1/3) del valor de los hidrocarburos líquidos extraídos.",
        "keywords": ["impuesto extracción", "33.33%"]
    },
    48: {
        "titulo": "Impuesto de Registro de Exportación",
        "contenido": "Las exportaciones de hidrocarburos líquidos naturales y sus derivados, pagarán un impuesto de registro de exportación equivalente a 0,1% del valor de los hidrocarburos exportados.",
        "keywords": ["exportación", "0.1%"]
    },
    50: {
        "titulo": "Canon de Superficie",
        "contenido": "Los titulares de las actividades de producción de hidrocarburos pagarán al Estado un canon de superficie equivalente a cien unidades tributarias (100 U.T.) por cada kilómetro cuadrado.",
        "keywords": ["canon", "superficie", "100 UT"]
    },
    56: {
        "titulo": "ISLR",
        "contenido": "Las empresas que realicen las actividades primarias estarán sujetas al régimen fiscal previsto en la Ley de Impuesto sobre la Renta para las personas jurídicas dedicadas a la explotación de hidrocarburos.",
        "keywords": ["ISLR", "impuesto", "renta"]
    }
}

# Fiscal obligations summary
FISCAL_OBLIGATIONS = {
    "regalia": {
        "name": "Regalía",
        "rate": "30% (hasta 33.33%)",
        "base": "Hidrocarburos líquidos extraídos",
        "loh_article": 44,
        "frequency": "Mensual"
    },
    "impuesto_extraccion": {
        "name": "Impuesto de Extracción",
        "rate": "33.33%",
        "base": "Valor de hidrocarburos líquidos extraídos",
        "loh_article": 46,
        "frequency": "Mensual"
    },
    "registro_exportacion": {
        "name": "Impuesto de Registro de Exportación",
        "rate": "0.1%",
        "base": "Valor de hidrocarburos exportados",
        "loh_article": 48,
        "frequency": "Por exportación"
    },
    "canon_superficie": {
        "name": "Canon de Superficie",
        "rate": "100 UT/km²",
        "base": "Área concesionada",
        "loh_article": 50,
        "frequency": "Anual"
    },
    "islr": {
        "name": "ISLR Actividades Primarias",
        "rate": "50%",
        "base": "Enriquecimiento neto",
        "loh_article": 56,
        "frequency": "Anual"
    },
    "aporte_social": {
        "name": "Aporte Social",
        "rate": "Variable (1-3.33%)",
        "base": "Utilidades",
        "loh_article": "Leyes especiales",
        "frequency": "Anual"
    }
}

# Key institutions
INSTITUTIONS = {
    "menpet": {
        "name": "Ministerio del Poder Popular de Petróleo",
        "role": "Órgano rector de la política petrolera",
        "competencias": [
            "Formulación de políticas petroleras",
            "Supervisión de PDVSA",
            "Otorgamiento de permisos y autorizaciones",
            "Negociación de convenios internacionales"
        ]
    },
    "pdvsa": {
        "name": "Petróleos de Venezuela, S.A.",
        "role": "Empresa estatal de hidrocarburos",
        "competencias": [
            "Ejecución de actividades primarias",
            "Participación en empresas mixtas",
            "Comercialización internacional",
            "Refinación y distribución"
        ],
        "filiales": [
            "PDVSA Petróleo, S.A.",
            "CVP (Corporación Venezolana del Petróleo)",
            "CITGO Petroleum Corporation",
            "PDV Marina",
            "INTEVEP"
        ]
    },
    "cvp": {
        "name": "Corporación Venezolana del Petróleo",
        "role": "Gestión de empresas mixtas",
        "competencias": [
            "Representación estatal en empresas mixtas",
            "Gestión de nuevos proyectos",
            "Negociación con socios privados"
        ]
    },
    "seniat": {
        "name": "SENIAT",
        "role": "Recaudación tributaria",
        "competencias": [
            "Fiscalización de obligaciones tributarias",
            "Cobro de ISLR sector hidrocarburos",
            "Impuestos de registro"
        ]
    }
}

# Environmental requirements (LOA - Ley Orgánica del Ambiente)
ENVIRONMENTAL_REQUIREMENTS = {
    "eia": {
        "name": "Estudio de Impacto Ambiental (EIA)",
        "required_for": ["Exploración", "Explotación", "Nuevos proyectos"],
        "authority": "Ministerio del Ambiente",
        "timeline": "90-180 días"
    },
    "aac": {
        "name": "Autorización de Afectación de Recursos Naturales",
        "required_for": ["Deforestación", "Uso de aguas", "Emisiones"],
        "authority": "Ministerio del Ambiente",
        "timeline": "60-120 días"
    },
    "plan_supervision": {
        "name": "Plan de Supervisión Ambiental",
        "required_for": ["Todas las operaciones"],
        "authority": "Ministerio del Ambiente + PDVSA INTEVEP",
        "timeline": "Continuo"
    },
    "remediacion": {
        "name": "Plan de Remediación y Cierre",
        "required_for": ["Abandono de pozos", "Cierre de instalaciones"],
        "authority": "Ministerio del Ambiente",
        "timeline": "Según plan aprobado"
    }
}


# ═══════════════════════════════════════════════════════════════════════════════
#                         DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class EmpresaMixta:
    """Structure for empresa mixta analysis."""
    nombre: str
    participacion_pdvsa: float  # Percentage
    participacion_privada: float
    socio_privado: str
    ubicacion: str
    actividad: ActivityType
    produccion_bpd: int  # Barrels per day
    estado_operacional: str
    observaciones: str = ""

    def validate_participation(self) -> Tuple[bool, str]:
        """Validate that PDVSA has majority control (>50%)."""
        if self.participacion_pdvsa > 50:
            return True, "Cumple Art. 9 LOH - PDVSA mantiene control mayoritario"
        else:
            return False, f"ALERTA: Incumple Art. 9 LOH - PDVSA tiene solo {self.participacion_pdvsa}%"

    def to_dict(self) -> Dict:
        result = asdict(self)
        result["actividad"] = self.actividad.value
        return result


@dataclass
class FiscalCalculation:
    """Fiscal obligation calculation."""
    produccion_bpd: int
    precio_barril_usd: float
    dias_periodo: int = 30
    area_km2: float = 0
    ut_value_bs: float = 9.0  # Valor UT actual aproximado

    def calculate_all(self) -> Dict[str, Any]:
        """Calculate all fiscal obligations."""
        total_production = self.produccion_bpd * self.dias_periodo
        gross_value = total_production * self.precio_barril_usd

        return {
            "periodo": f"{self.dias_periodo} días",
            "produccion_total_barriles": total_production,
            "valor_bruto_usd": gross_value,
            "obligaciones": {
                "regalia_30": {
                    "tasa": "30%",
                    "base": total_production,
                    "barriles": total_production * 0.30,
                    "valor_usd": gross_value * 0.30
                },
                "impuesto_extraccion": {
                    "tasa": "33.33%",
                    "base_usd": gross_value,
                    "monto_usd": gross_value * 0.3333
                },
                "canon_superficie": {
                    "tasa": "100 UT/km²",
                    "area_km2": self.area_km2,
                    "monto_ut": self.area_km2 * 100,
                    "monto_bs": self.area_km2 * 100 * self.ut_value_bs
                }
            },
            "total_carga_fiscal_estimada_usd": gross_value * 0.6333,  # 30% + 33.33%
            "porcentaje_carga_fiscal": 63.33
        }


@dataclass
class HydrocarbonsAnalysis:
    """Complete hydrocarbons sector analysis."""
    case_name: str
    activity_type: ActivityType
    contract_type: ContractType
    regime: RegimeType
    empresa_mixta: Optional[EmpresaMixta] = None
    fiscal_calc: Optional[FiscalCalculation] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Activity characteristics
    reserved_to_state: bool = False
    empresa_mixta_required: bool = False
    private_participation_allowed: bool = True

    # Analysis results
    applicable_loh_articles: List[int] = field(default_factory=list)
    constitutional_basis: List[int] = field(default_factory=list)
    fiscal_obligations: List[str] = field(default_factory=list)
    environmental_requirements: List[str] = field(default_factory=list)
    required_permits: List[str] = field(default_factory=list)
    risks: List[Dict[str, str]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        result = {
            "case_name": self.case_name,
            "activity_type": self.activity_type.value,
            "contract_type": self.contract_type.value,
            "regime": self.regime.value,
            "timestamp": self.timestamp,
            "reserved_to_state": self.reserved_to_state,
            "empresa_mixta_required": self.empresa_mixta_required,
            "private_participation_allowed": self.private_participation_allowed,
            "applicable_loh_articles": self.applicable_loh_articles,
            "constitutional_basis": self.constitutional_basis,
            "fiscal_obligations": self.fiscal_obligations,
            "environmental_requirements": self.environmental_requirements,
            "required_permits": self.required_permits,
            "risks": self.risks,
            "recommendations": self.recommendations
        }
        if self.empresa_mixta:
            result["empresa_mixta"] = self.empresa_mixta.to_dict()
        if self.fiscal_calc:
            result["fiscal_calculation"] = self.fiscal_calc.calculate_all()
        return result


# ═══════════════════════════════════════════════════════════════════════════════
#                         ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_activity(activity_type: ActivityType) -> Dict[str, Any]:
    """Analyze legal requirements for a specific hydrocarbon activity."""

    analysis = {
        "activity": activity_type.value,
        "reserved_to_state": False,
        "private_participation_allowed": True,
        "empresa_mixta_required": False,
        "applicable_loh_articles": [],
        "permits_required": [],
        "environmental_requirements": []
    }

    # Primary activities (reserved to state)
    if activity_type in [ActivityType.EXPLORACION, ActivityType.EXPLOTACION]:
        analysis["reserved_to_state"] = True
        analysis["empresa_mixta_required"] = True
        analysis["private_participation_allowed"] = True  # Via empresa mixta
        analysis["applicable_loh_articles"] = [1, 2, 3, 9, 44, 45, 46, 50]
        analysis["permits_required"] = [
            "Autorización del Ministerio de Petróleo",
            "Contrato de empresa mixta aprobado por AN",
            "Permiso ambiental (EIA completo)"
        ]
        analysis["environmental_requirements"] = ["eia", "aac", "plan_supervision"]

    # Secondary activities
    elif activity_type in [ActivityType.REFINACION, ActivityType.INDUSTRIALIZACION]:
        analysis["applicable_loh_articles"] = [22, 56]
        analysis["permits_required"] = [
            "Autorización del Ministerio de Petróleo",
            "Permiso ambiental",
            "Licencia de operación industrial"
        ]
        analysis["environmental_requirements"] = ["eia", "aac"]

    elif activity_type in [ActivityType.TRANSPORTE, ActivityType.ALMACENAMIENTO]:
        analysis["applicable_loh_articles"] = [22]
        analysis["permits_required"] = [
            "Autorización del Ministerio de Petróleo",
            "Permiso de construcción",
            "Estudio de impacto ambiental"
        ]
        analysis["environmental_requirements"] = ["eia"]

    elif activity_type in [ActivityType.COMERCIALIZACION_INTERNA, ActivityType.COMERCIALIZACION_EXTERNA]:
        analysis["applicable_loh_articles"] = [22, 48]
        analysis["permits_required"] = [
            "Registro en Ministerio de Petróleo",
            "Autorización de exportación (si aplica)"
        ]

    elif activity_type == ActivityType.SERVICIOS:
        analysis["applicable_loh_articles"] = [22]
        analysis["permits_required"] = [
            "Registro de empresa de servicios petroleros",
            "Certificación técnica"
        ]

    return analysis


def analyze_empresa_mixta(
    nombre: str,
    participacion_pdvsa: float,
    socio_privado: str,
    produccion_bpd: int = 0
) -> Dict[str, Any]:
    """Analyze empresa mixta compliance with LOH."""

    empresa = EmpresaMixta(
        nombre=nombre,
        participacion_pdvsa=participacion_pdvsa,
        participacion_privada=100 - participacion_pdvsa,
        socio_privado=socio_privado,
        ubicacion="Venezuela",
        actividad=ActivityType.EXPLOTACION,
        produccion_bpd=produccion_bpd,
        estado_operacional="Operativa"
    )

    compliant, message = empresa.validate_participation()

    analysis = {
        "empresa": empresa.to_dict(),
        "compliance": {
            "art_9_loh": compliant,
            "message": message
        },
        "governance_requirements": [
            "Junta Directiva con mayoría de representantes PDVSA",
            "Decisiones estratégicas requieren aprobación PDVSA",
            "Gerente General designado por PDVSA",
            "Auditoría por Contraloría General de la República"
        ],
        "reporting_obligations": [
            "Informe mensual al Ministerio de Petróleo",
            "Declaración de producción diaria",
            "Estados financieros trimestrales",
            "Auditoría anual certificada"
        ],
        "constitutional_basis": [12, 302, 303],
        "applicable_loh_articles": [3, 9, 10, 11, 12]
    }

    if not compliant:
        analysis["risks"] = [
            {
                "risk": "Nulidad del contrato por inconstitucionalidad",
                "severity": "CRITICAL",
                "basis": "Art. 302 CRBV + Art. 9 LOH"
            },
            {
                "risk": "Sanciones administrativas a directivos",
                "severity": "HIGH",
                "basis": "LOCGRSNCF"
            }
        ]
        analysis["recommendations"] = [
            "Reestructurar participación accionaria inmediatamente",
            "Obtener aprobación de la AN para nueva estructura",
            "Consultar con Procuraduría General de la República"
        ]

    return analysis


def calculate_fiscal_obligations(
    produccion_bpd: int,
    precio_barril_usd: float,
    area_km2: float = 100,
    dias: int = 30
) -> Dict[str, Any]:
    """Calculate fiscal obligations for hydrocarbon production."""

    calc = FiscalCalculation(
        produccion_bpd=produccion_bpd,
        precio_barril_usd=precio_barril_usd,
        dias_periodo=dias,
        area_km2=area_km2
    )

    result = calc.calculate_all()
    result["legal_basis"] = [
        {"obligation": "Regalía", "loh_article": 44, "crbv_article": 12},
        {"obligation": "Impuesto de Extracción", "loh_article": 46},
        {"obligation": "Canon de Superficie", "loh_article": 50},
        {"obligation": "ISLR 50%", "loh_article": 56}
    ]
    result["payment_deadlines"] = {
        "regalia": "Primeros 15 días del mes siguiente",
        "impuesto_extraccion": "Primeros 15 días del mes siguiente",
        "canon_superficie": "Primer trimestre del año",
        "islr": "Según calendario SENIAT"
    }

    return result


def get_environmental_requirements(activity_type: ActivityType) -> Dict[str, Any]:
    """Get environmental requirements for hydrocarbon activity."""

    requirements = {
        "activity": activity_type.value,
        "general_requirements": [
            "Cumplimiento de Ley Orgánica del Ambiente (LOA)",
            "Cumplimiento de Ley Penal del Ambiente",
            "Normas técnicas sobre calidad de aire, agua y suelos"
        ],
        "specific_requirements": [],
        "permits": [],
        "timeline": ""
    }

    if activity_type in [ActivityType.EXPLORACION, ActivityType.EXPLOTACION]:
        requirements["specific_requirements"] = [
            "Estudio de Impacto Ambiental y Sociocultural (EIASC) completo",
            "Plan de Gestión Ambiental",
            "Plan de Contingencia para derrames",
            "Programa de monitoreo continuo",
            "Fondo de garantía ambiental"
        ]
        requirements["permits"] = [
            ENVIRONMENTAL_REQUIREMENTS["eia"],
            ENVIRONMENTAL_REQUIREMENTS["aac"],
            ENVIRONMENTAL_REQUIREMENTS["plan_supervision"]
        ]
        requirements["timeline"] = "6-12 meses para obtener todos los permisos"

    elif activity_type in [ActivityType.REFINACION, ActivityType.INDUSTRIALIZACION]:
        requirements["specific_requirements"] = [
            "EIASC para instalaciones industriales",
            "Plan de manejo de emisiones atmosféricas",
            "Plan de tratamiento de efluentes",
            "Plan de manejo de residuos peligrosos"
        ]
        requirements["permits"] = [
            ENVIRONMENTAL_REQUIREMENTS["eia"],
            ENVIRONMENTAL_REQUIREMENTS["aac"]
        ]
        requirements["timeline"] = "6-9 meses"

    elif activity_type == ActivityType.TRANSPORTE:
        requirements["specific_requirements"] = [
            "EIASC para construcción de oleoductos/gasoductos",
            "Plan de prevención de derrames",
            "Programa de mantenimiento preventivo",
            "Sistema de detección de fugas"
        ]
        requirements["timeline"] = "4-6 meses"

    requirements["penalties"] = {
        "administrative": "Multas de 100-10,000 UT",
        "criminal": "Prisión de 1-10 años (Ley Penal del Ambiente)",
        "civil": "Reparación integral del daño causado"
    }

    return requirements


def run_full_hydrocarbons_analysis(
    case_name: str,
    activity: str,
    contract: str = "EMPRESA_MIXTA",
    produccion_bpd: int = 0,
    precio_barril: float = 70.0,
    participacion_pdvsa: float = 60.0,
    socio: str = "Socio Privado",
    area_km2: float = 100
) -> HydrocarbonsAnalysis:
    """Run complete hydrocarbons sector analysis."""

    # Parse enums
    activity_type = ActivityType[activity.upper()] if isinstance(activity, str) else activity
    contract_type = ContractType[contract.upper()] if isinstance(contract, str) else contract

    # Create analysis object
    analysis = HydrocarbonsAnalysis(
        case_name=case_name,
        activity_type=activity_type,
        contract_type=contract_type,
        regime=RegimeType.LOH_2006
    )

    # Activity analysis
    activity_analysis = analyze_activity(activity_type)
    analysis.applicable_loh_articles = activity_analysis["applicable_loh_articles"]
    analysis.required_permits = activity_analysis["permits_required"]
    analysis.environmental_requirements = activity_analysis["environmental_requirements"]

    # Set activity characteristics
    analysis.reserved_to_state = activity_analysis.get("reserved_to_state", False)
    analysis.empresa_mixta_required = activity_analysis.get("empresa_mixta_required", False)
    analysis.private_participation_allowed = activity_analysis.get("private_participation_allowed", True)

    # Constitutional basis
    analysis.constitutional_basis = [12, 302, 303]  # Hydrocarbon articles in CRBV

    # Empresa mixta analysis (if applicable)
    if contract_type == ContractType.EMPRESA_MIXTA and activity_type in [ActivityType.EXPLORACION, ActivityType.EXPLOTACION]:
        empresa = EmpresaMixta(
            nombre=case_name,
            participacion_pdvsa=participacion_pdvsa,
            participacion_privada=100 - participacion_pdvsa,
            socio_privado=socio,
            ubicacion="Venezuela",
            actividad=activity_type,
            produccion_bpd=produccion_bpd,
            estado_operacional="En análisis"
        )
        analysis.empresa_mixta = empresa

        compliant, message = empresa.validate_participation()
        if not compliant:
            analysis.risks.append({
                "risk": "Estructura societaria no cumple con Art. 9 LOH",
                "severity": "CRITICAL",
                "mitigation": "Reestructurar participación para dar mayoría a PDVSA"
            })

    # Fiscal calculation
    if produccion_bpd > 0:
        analysis.fiscal_calc = FiscalCalculation(
            produccion_bpd=produccion_bpd,
            precio_barril_usd=precio_barril,
            area_km2=area_km2
        )

    # Get fiscal obligations
    for key, obligation in FISCAL_OBLIGATIONS.items():
        if obligation["loh_article"] in analysis.applicable_loh_articles or key == "islr":
            analysis.fiscal_obligations.append(f"{obligation['name']}: {obligation['rate']}")

    # Environmental requirements
    env_reqs = get_environmental_requirements(activity_type)
    analysis.environmental_requirements = [r["name"] for r in env_reqs.get("permits", [])]

    # Risks based on activity
    if activity_type in [ActivityType.EXPLORACION, ActivityType.EXPLOTACION]:
        analysis.risks.extend([
            {"risk": "Riesgo de nulidad si empresa mixta no tiene aprobación AN", "severity": "HIGH"},
            {"risk": "Riesgo ambiental por derrames o fugas", "severity": "MEDIUM"},
            {"risk": "Variación de precios internacionales afecta rentabilidad", "severity": "MEDIUM"}
        ])

    # Recommendations
    analysis.recommendations = [
        "Verificar que la estructura de empresa mixta cumple Art. 9 LOH",
        "Obtener todos los permisos ambientales antes de iniciar operaciones",
        "Establecer mecanismo de monitoreo fiscal continuo",
        "Mantener comunicación regular con Ministerio de Petróleo",
        "Implementar programa de cumplimiento regulatorio"
    ]

    return analysis


def search_loh_articles(keyword: str) -> List[Dict]:
    """Search LOH articles by keyword."""
    results = []
    keyword_lower = keyword.lower()

    for num, article in LOH_ARTICLES.items():
        if (keyword_lower in article["contenido"].lower() or
            keyword_lower in article["titulo"].lower() or
            any(keyword_lower in k for k in article["keywords"])):
            results.append({
                "numero": num,
                "titulo": article["titulo"],
                "contenido": article["contenido"],
                "match": "keyword match"
            })

    return results


def get_institution_info(institution_key: str) -> Dict:
    """Get information about a hydrocarbon sector institution."""
    return INSTITUTIONS.get(institution_key, {"error": "Institution not found"})


def get_statistics() -> Dict:
    """Get hydrocarbons playbook statistics."""
    return {
        "loh_articles_indexed": len(LOH_ARTICLES),
        "fiscal_obligations_tracked": len(FISCAL_OBLIGATIONS),
        "institutions_registered": len(INSTITUTIONS),
        "environmental_requirements": len(ENVIRONMENTAL_REQUIREMENTS),
        "activity_types": len(ActivityType),
        "contract_types": len(ContractType)
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for hydrocarbons playbook."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Venezuela Super Lawyer - Hydrocarbons Playbook (Module 7)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run full hydrocarbons analysis")
    analyze_parser.add_argument("case_name", help="Case name")
    analyze_parser.add_argument("--activity", "-a",
                               choices=[a.name for a in ActivityType],
                               default="EXPLOTACION",
                               help="Activity type")
    analyze_parser.add_argument("--contract", "-c",
                               choices=[c.name for c in ContractType],
                               default="EMPRESA_MIXTA",
                               help="Contract type")
    analyze_parser.add_argument("--production", "-p", type=int, default=0,
                               help="Production in BPD")
    analyze_parser.add_argument("--price", type=float, default=70.0,
                               help="Oil price USD/barrel")
    analyze_parser.add_argument("--pdvsa-share", type=float, default=60.0,
                               help="PDVSA participation percentage")
    analyze_parser.add_argument("--partner", default="Socio Privado",
                               help="Private partner name")
    analyze_parser.add_argument("--area", type=float, default=100,
                               help="Area in km²")

    # Fiscal command
    fiscal_parser = subparsers.add_parser("fiscal", help="Calculate fiscal obligations")
    fiscal_parser.add_argument("production", type=int, help="Production in BPD")
    fiscal_parser.add_argument("--price", "-p", type=float, default=70.0,
                               help="Oil price USD/barrel")
    fiscal_parser.add_argument("--days", "-d", type=int, default=30,
                               help="Period in days")
    fiscal_parser.add_argument("--area", type=float, default=100,
                               help="Area in km²")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search LOH articles")
    search_parser.add_argument("keyword", help="Search keyword")

    # Stats command
    subparsers.add_parser("stats", help="Get playbook statistics")

    # Output format
    parser.add_argument("--output", "-o", choices=["json", "text"], default="json",
                       help="Output format")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "analyze":
        result = run_full_hydrocarbons_analysis(
            case_name=args.case_name,
            activity=args.activity,
            contract=args.contract,
            produccion_bpd=args.production,
            precio_barril=args.price,
            participacion_pdvsa=args.pdvsa_share,
            socio=args.partner,
            area_km2=args.area
        )
        if args.output == "json":
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"HYDROCARBONS ANALYSIS: {result.case_name}")
            print(f"{'='*60}")
            print(f"Activity: {result.activity_type.value}")
            print(f"Contract: {result.contract_type.value}")
            print(f"Regime: {result.regime.value}")
            print(f"\nApplicable LOH Articles: {result.applicable_loh_articles}")
            print(f"Constitutional Basis: Arts. {result.constitutional_basis} CRBV")
            print(f"\nFiscal Obligations:")
            for obl in result.fiscal_obligations:
                print(f"  - {obl}")
            print(f"\nRequired Permits:")
            for permit in result.required_permits:
                print(f"  - {permit}")
            if result.risks:
                print(f"\nRisks Identified:")
                for risk in result.risks:
                    print(f"  - [{risk.get('severity', 'N/A')}] {risk.get('risk', '')}")

    elif args.command == "fiscal":
        result = calculate_fiscal_obligations(
            produccion_bpd=args.production,
            precio_barril_usd=args.price,
            area_km2=args.area,
            dias=args.days
        )
        if args.output == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\nFISCAL CALCULATION")
            print(f"Production: {args.production} BPD")
            print(f"Price: ${args.price}/barrel")
            print(f"Period: {args.days} days")
            print(f"\nTotal Production: {result['produccion_total_barriles']:,} barrels")
            print(f"Gross Value: ${result['valor_bruto_usd']:,.2f}")
            print(f"\nObligations:")
            for key, obl in result['obligaciones'].items():
                if 'valor_usd' in obl:
                    print(f"  - {key}: ${obl['valor_usd']:,.2f}")
                elif 'monto_usd' in obl:
                    print(f"  - {key}: ${obl['monto_usd']:,.2f}")
            print(f"\nTotal Fiscal Burden: {result['porcentaje_carga_fiscal']:.2f}%")
            print(f"Estimated Total: ${result['total_carga_fiscal_estimada_usd']:,.2f}")

    elif args.command == "search":
        results = search_loh_articles(args.keyword)
        if args.output == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print(f"\nSearch Results for '{args.keyword}':")
            for art in results:
                print(f"\nArt. {art['numero']}: {art['titulo']}")
                print(f"  {art['contenido'][:200]}...")

    elif args.command == "stats":
        stats = get_statistics()
        if args.output == "json":
            print(json.dumps(stats, indent=2))
        else:
            print("\nHydrocarbons Playbook Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
