#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Voting Map Engine (Module 17)
Analyzes legislative voting requirements and political feasibility for
proposed legislation in Venezuela.

Based on:
- CRBV Articles 186-224 (Poder Legislativo)
- CRBV Articles 202-218 (Formación de las Leyes)
- CRBV Articles 340-350 (Reforma Constitucional)
- Reglamento Interior y de Debates de la Asamblea Nacional

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import sys
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import math

# ═══════════════════════════════════════════════════════════════════════════════
#                         LEGISLATIVE FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════

class NormType(Enum):
    """Types of legal norms in Venezuelan system."""
    LEY_ORDINARIA = "Ley Ordinaria"
    LEY_ORGANICA = "Ley Orgánica"
    LEY_HABILITANTE = "Ley Habilitante"
    DECRETO_LEY = "Decreto con Rango, Valor y Fuerza de Ley"
    REGLAMENTO = "Reglamento"
    RESOLUCION = "Resolución"
    ORDENANZA = "Ordenanza Municipal"
    ENMIENDA = "Enmienda Constitucional"
    REFORMA = "Reforma Constitucional"
    CONSTITUYENTE = "Asamblea Nacional Constituyente"


class MajorityType(Enum):
    """Types of majority required for legislative votes."""
    SIMPLE = "Mayoría Simple"                    # >50% of present members
    ABSOLUTA = "Mayoría Absoluta"                # >50% of total members
    CALIFICADA_2_3 = "Mayoría Calificada (2/3)"  # ≥2/3 of total members
    CALIFICADA_3_5 = "Mayoría Calificada (3/5)"  # ≥3/5 of total members
    UNANIMIDAD = "Unanimidad"                     # 100% of total members


class VotingBody(Enum):
    """Entities that participate in legislative voting."""
    ASAMBLEA_NACIONAL = "Asamblea Nacional"
    PRESIDENTE = "Presidente de la República"
    SALA_CONSTITUCIONAL = "Sala Constitucional TSJ"
    PUEBLO = "Pueblo (Referendo)"
    CONSEJO_MUNICIPAL = "Consejo Municipal"
    CONSEJO_LEGISLATIVO = "Consejo Legislativo Estadal"


class LegislativePhase(Enum):
    """Phases of the legislative process."""
    INICIATIVA = "Iniciativa Legislativa"
    PRIMERA_DISCUSION = "Primera Discusión"
    SEGUNDA_DISCUSION = "Segunda Discusión"
    SANCION = "Sanción"
    PROMULGACION = "Promulgación"
    PUBLICACION = "Publicación en Gaceta"
    REFERENDO = "Referendo (si aplica)"
    VIGENCIA = "Entrada en Vigencia"


class FeasibilityLevel(Enum):
    """Feasibility levels for legislative proposals."""
    MUY_ALTA = "Muy Alta"      # >80%
    ALTA = "Alta"              # 60-80%
    MEDIA = "Media"            # 40-60%
    BAJA = "Baja"              # 20-40%
    MUY_BAJA = "Muy Baja"      # <20%


# ═══════════════════════════════════════════════════════════════════════════════
#                         DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class VotingRequirement:
    """Voting requirement for a specific phase."""
    phase: LegislativePhase
    voting_body: VotingBody
    majority_type: MajorityType
    quorum_required: float  # Percentage (0.0 to 1.0)
    votes_needed: int
    total_members: int
    description: str
    constitutional_basis: str


@dataclass
class LegislativeTimeline:
    """Timeline for legislative process."""
    phase: LegislativePhase
    description: str
    min_days: int
    max_days: int
    responsible: str
    requirements: List[str] = field(default_factory=list)


@dataclass
class PoliticalBlocker:
    """Political or legal blocker for legislation."""
    name: str
    description: str
    severity: str  # "Alta", "Media", "Baja"
    mitigation: str
    probability: float  # 0.0 to 1.0


@dataclass
class VotingMap:
    """Complete voting map for a legislative proposal."""
    norm_type: NormType
    title: str
    description: str
    total_an_members: int
    current_composition: Dict[str, int]  # Party -> seats
    voting_requirements: List[VotingRequirement]
    timeline: List[LegislativeTimeline]
    blockers: List[PoliticalBlocker]
    feasibility_score: float
    feasibility_level: FeasibilityLevel
    recommended_strategy: str
    alternative_routes: List[str]
    generated_at: str = ""

    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


# ═══════════════════════════════════════════════════════════════════════════════
#                         CONSTITUTIONAL REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════════════

# Total members of the Asamblea Nacional (per 2024 composition)
AN_TOTAL_MEMBERS = 277

# Voting requirements by norm type
VOTING_REQUIREMENTS = {
    NormType.LEY_ORDINARIA: {
        "majority": MajorityType.SIMPLE,
        "quorum": 0.5,  # Majority of total members present
        "discussions": 2,
        "referendo_required": False,
        "constitutional_basis": "CRBV Art. 211-214"
    },
    NormType.LEY_ORGANICA: {
        "majority": MajorityType.CALIFICADA_2_3,
        "quorum": 0.5,
        "discussions": 2,
        "referendo_required": False,
        "constitutional_basis": "CRBV Art. 203"
    },
    NormType.LEY_HABILITANTE: {
        "majority": MajorityType.CALIFICADA_3_5,
        "quorum": 0.5,
        "discussions": 2,
        "referendo_required": False,
        "constitutional_basis": "CRBV Art. 203"
    },
    NormType.ENMIENDA: {
        "majority": MajorityType.SIMPLE,
        "quorum": 0.5,
        "discussions": 2,
        "referendo_required": True,
        "constitutional_basis": "CRBV Art. 340-341"
    },
    NormType.REFORMA: {
        "majority": MajorityType.CALIFICADA_2_3,
        "quorum": 0.5,
        "discussions": 3,
        "referendo_required": True,
        "constitutional_basis": "CRBV Art. 342-346"
    },
    NormType.CONSTITUYENTE: {
        "majority": MajorityType.CALIFICADA_2_3,
        "quorum": 0.5,
        "discussions": 1,
        "referendo_required": True,
        "constitutional_basis": "CRBV Art. 347-349"
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
#                         CALCULATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_votes_needed(
    total_members: int,
    majority_type: MajorityType,
    quorum_percentage: float = 0.5
) -> Tuple[int, int]:
    """
    Calculate votes needed and quorum required.

    Args:
        total_members: Total number of assembly members
        majority_type: Type of majority required
        quorum_percentage: Minimum percentage for quorum

    Returns:
        Tuple of (votes_needed, quorum_needed)
    """
    quorum_needed = math.ceil(total_members * quorum_percentage) + 1

    if majority_type == MajorityType.SIMPLE:
        # Simple majority: >50% of members present (assuming quorum)
        votes_needed = math.ceil(quorum_needed / 2) + 1
    elif majority_type == MajorityType.ABSOLUTA:
        # Absolute majority: >50% of total members
        votes_needed = math.ceil(total_members / 2) + 1
    elif majority_type == MajorityType.CALIFICADA_2_3:
        # Qualified majority: ≥2/3 of total members
        votes_needed = math.ceil(total_members * 2 / 3)
    elif majority_type == MajorityType.CALIFICADA_3_5:
        # Qualified majority: ≥3/5 of total members
        votes_needed = math.ceil(total_members * 3 / 5)
    elif majority_type == MajorityType.UNANIMIDAD:
        votes_needed = total_members
    else:
        votes_needed = math.ceil(total_members / 2) + 1

    return votes_needed, quorum_needed


def calculate_feasibility(
    votes_needed: int,
    estimated_favorable_votes: int,
    blockers: List[PoliticalBlocker]
) -> Tuple[float, FeasibilityLevel]:
    """
    Calculate feasibility score and level.

    Args:
        votes_needed: Number of votes required
        estimated_favorable_votes: Estimated favorable votes
        blockers: List of political blockers

    Returns:
        Tuple of (feasibility_score, feasibility_level)
    """
    # Base score from vote ratio
    if votes_needed > 0:
        vote_ratio = estimated_favorable_votes / votes_needed
        base_score = min(1.0, vote_ratio)
    else:
        base_score = 1.0

    # Deduct for blockers
    blocker_penalty = 0.0
    for blocker in blockers:
        if blocker.severity == "Alta":
            blocker_penalty += blocker.probability * 0.3
        elif blocker.severity == "Media":
            blocker_penalty += blocker.probability * 0.15
        else:
            blocker_penalty += blocker.probability * 0.05

    final_score = max(0.0, base_score - blocker_penalty)

    # Determine level
    if final_score >= 0.8:
        level = FeasibilityLevel.MUY_ALTA
    elif final_score >= 0.6:
        level = FeasibilityLevel.ALTA
    elif final_score >= 0.4:
        level = FeasibilityLevel.MEDIA
    elif final_score >= 0.2:
        level = FeasibilityLevel.BAJA
    else:
        level = FeasibilityLevel.MUY_BAJA

    return round(final_score, 2), level


def get_legislative_timeline(norm_type: NormType) -> List[LegislativeTimeline]:
    """Get standard timeline for legislative process by norm type."""
    timelines = {
        NormType.LEY_ORDINARIA: [
            LegislativeTimeline(
                phase=LegislativePhase.INICIATIVA,
                description="Presentación del proyecto de ley",
                min_days=1,
                max_days=7,
                responsible="Proponente (Diputados, Ejecutivo, TSJ, Ciudadanos)",
                requirements=["Exposición de motivos", "Articulado completo"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PRIMERA_DISCUSION,
                description="Primera discusión en plenaria",
                min_days=15,
                max_days=30,
                responsible="Asamblea Nacional - Plenaria",
                requirements=["Informe de Comisión", "Quórum reglamentario"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.SEGUNDA_DISCUSION,
                description="Segunda discusión artículo por artículo",
                min_days=15,
                max_days=45,
                responsible="Asamblea Nacional - Plenaria",
                requirements=["Aprobación en primera discusión"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.SANCION,
                description="Sanción de la ley",
                min_days=1,
                max_days=5,
                responsible="Presidente de la Asamblea Nacional",
                requirements=["Aprobación en segunda discusión"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PROMULGACION,
                description="Promulgación por el Ejecutivo",
                min_days=1,
                max_days=10,
                responsible="Presidente de la República",
                requirements=["Ley sancionada"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PUBLICACION,
                description="Publicación en Gaceta Oficial",
                min_days=1,
                max_days=5,
                responsible="Imprenta Nacional",
                requirements=["Ley promulgada"]
            ),
        ],
        NormType.LEY_ORGANICA: [
            LegislativeTimeline(
                phase=LegislativePhase.INICIATIVA,
                description="Presentación del proyecto de ley orgánica",
                min_days=1,
                max_days=7,
                responsible="Proponente",
                requirements=["Exposición de motivos", "Justificación carácter orgánico"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PRIMERA_DISCUSION,
                description="Primera discusión - admisión carácter orgánico",
                min_days=20,
                max_days=45,
                responsible="Asamblea Nacional - Plenaria",
                requirements=["Informe de Comisión", "Votación 2/3 carácter orgánico"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.SEGUNDA_DISCUSION,
                description="Segunda discusión con mayoría calificada",
                min_days=20,
                max_days=60,
                responsible="Asamblea Nacional - Plenaria",
                requirements=["2/3 de los diputados"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.SANCION,
                description="Sanción de la ley orgánica",
                min_days=1,
                max_days=5,
                responsible="Presidente de la Asamblea Nacional",
                requirements=["Aprobación con 2/3"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PROMULGACION,
                description="Remisión a Sala Constitucional + Promulgación",
                min_days=10,
                max_days=30,
                responsible="Sala Constitucional TSJ",
                requirements=["Control previo de constitucionalidad (Art. 203)"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PUBLICACION,
                description="Publicación en Gaceta Oficial",
                min_days=1,
                max_days=5,
                responsible="Imprenta Nacional",
                requirements=["Pronunciamiento favorable Sala Constitucional"]
            ),
        ],
        NormType.ENMIENDA: [
            LegislativeTimeline(
                phase=LegislativePhase.INICIATIVA,
                description="Iniciativa de enmienda (15% electores, 30% AN, o Presidente)",
                min_days=30,
                max_days=90,
                responsible="Proponente según Art. 341 CRBV",
                requirements=["15% electores inscritos O 30% AN O Presidente"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PRIMERA_DISCUSION,
                description="Tramitación en la Asamblea Nacional",
                min_days=30,
                max_days=60,
                responsible="Asamblea Nacional",
                requirements=["Mayoría simple para aprobación"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.REFERENDO,
                description="Referendo aprobatorio",
                min_days=30,
                max_days=90,
                responsible="Consejo Nacional Electoral",
                requirements=["Mayoría de votantes", "Participación >25%"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PROMULGACION,
                description="Promulgación de la enmienda",
                min_days=1,
                max_days=10,
                responsible="Presidente de la República",
                requirements=["Aprobación en referendo"]
            ),
        ],
        NormType.REFORMA: [
            LegislativeTimeline(
                phase=LegislativePhase.INICIATIVA,
                description="Iniciativa de reforma (15% electores, mayoría AN, o Presidente + Ministros)",
                min_days=30,
                max_days=90,
                responsible="Proponente según Art. 342 CRBV",
                requirements=["15% electores O mayoría AN O Presidente en Consejo"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PRIMERA_DISCUSION,
                description="Primera discusión en período ordinario",
                min_days=30,
                max_days=60,
                responsible="Asamblea Nacional",
                requirements=["Durante sesiones ordinarias"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.SEGUNDA_DISCUSION,
                description="Segunda discusión",
                min_days=30,
                max_days=60,
                responsible="Asamblea Nacional",
                requirements=["Aprobación primera discusión"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.SANCION,
                description="Tercera discusión y aprobación con 2/3",
                min_days=30,
                max_days=60,
                responsible="Asamblea Nacional",
                requirements=["2/3 de los integrantes"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.REFERENDO,
                description="Referendo aprobatorio obligatorio",
                min_days=30,
                max_days=90,
                responsible="Consejo Nacional Electoral",
                requirements=["Dentro de 30 días de sanción"]
            ),
            LegislativeTimeline(
                phase=LegislativePhase.PROMULGACION,
                description="Promulgación de la reforma",
                min_days=1,
                max_days=10,
                responsible="Presidente de la República",
                requirements=["Aprobación popular en referendo"]
            ),
        ],
    }

    return timelines.get(norm_type, timelines[NormType.LEY_ORDINARIA])


def get_common_blockers(norm_type: NormType) -> List[PoliticalBlocker]:
    """Get common political blockers by norm type."""
    common = [
        PoliticalBlocker(
            name="Quórum insuficiente",
            description="No se alcanza el quórum reglamentario para sesionar",
            severity="Alta",
            mitigation="Coordinar asistencia con bloques parlamentarios",
            probability=0.2
        ),
        PoliticalBlocker(
            name="Obstrucción parlamentaria",
            description="Tácticas dilatorias de la oposición",
            severity="Media",
            mitigation="Negociación y acuerdos de gobernabilidad",
            probability=0.3
        ),
        PoliticalBlocker(
            name="Veto presidencial",
            description="El Ejecutivo devuelve la ley sin promulgar",
            severity="Alta",
            mitigation="Coordinación previa con Ejecutivo o mayoría para insistencia",
            probability=0.15
        ),
    ]

    if norm_type in [NormType.LEY_ORGANICA, NormType.LEY_HABILITANTE]:
        common.append(PoliticalBlocker(
            name="No alcanzar mayoría calificada",
            description=f"No se obtienen los 2/3 o 3/5 requeridos",
            severity="Alta",
            mitigation="Negociación con bloques minoritarios",
            probability=0.4
        ))

    if norm_type in [NormType.ENMIENDA, NormType.REFORMA]:
        common.extend([
            PoliticalBlocker(
                name="Rechazo en referendo",
                description="El pueblo no aprueba la enmienda/reforma",
                severity="Alta",
                mitigation="Campaña de información y consulta previa",
                probability=0.35
            ),
            PoliticalBlocker(
                name="Abstención masiva",
                description="Participación inferior al umbral requerido",
                severity="Media",
                mitigation="Movilización ciudadana",
                probability=0.25
            ),
        ])

    if norm_type == NormType.LEY_ORGANICA:
        common.append(PoliticalBlocker(
            name="Inconstitucionalidad (Sala Constitucional)",
            description="La Sala Constitucional declara vicios de inconstitucionalidad",
            severity="Alta",
            mitigation="Revisión previa con expertos constitucionalistas",
            probability=0.2
        ))

    return common


# ═══════════════════════════════════════════════════════════════════════════════
#                         PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def generate_voting_map(
    norm_type: NormType,
    title: str,
    description: str = "",
    total_members: int = AN_TOTAL_MEMBERS,
    composition: Optional[Dict[str, int]] = None,
    estimated_favorable: Optional[int] = None,
    custom_blockers: Optional[List[Dict]] = None
) -> VotingMap:
    """
    Generate a complete voting map for a legislative proposal.

    Args:
        norm_type: Type of norm being proposed
        title: Title of the proposal
        description: Brief description
        total_members: Total assembly members
        composition: Party composition {party: seats}
        estimated_favorable: Estimated favorable votes
        custom_blockers: Additional custom blockers

    Returns:
        Complete VotingMap object
    """
    # Get requirements for this norm type
    req = VOTING_REQUIREMENTS.get(norm_type, VOTING_REQUIREMENTS[NormType.LEY_ORDINARIA])

    # Calculate votes needed
    votes_needed, quorum_needed = calculate_votes_needed(
        total_members,
        req["majority"],
        req["quorum"]
    )

    # Build voting requirements list
    voting_requirements = []

    # Main voting requirement
    voting_requirements.append(VotingRequirement(
        phase=LegislativePhase.SEGUNDA_DISCUSION,
        voting_body=VotingBody.ASAMBLEA_NACIONAL,
        majority_type=req["majority"],
        quorum_required=req["quorum"],
        votes_needed=votes_needed,
        total_members=total_members,
        description=f"Aprobación en {req['discussions']}ª discusión con {req['majority'].value}",
        constitutional_basis=req["constitutional_basis"]
    ))

    # Add referendo if required
    if req["referendo_required"]:
        voting_requirements.append(VotingRequirement(
            phase=LegislativePhase.REFERENDO,
            voting_body=VotingBody.PUEBLO,
            majority_type=MajorityType.SIMPLE,
            quorum_required=0.25,  # Minimum participation
            votes_needed=0,  # Depends on turnout
            total_members=0,  # Electoral register
            description="Referendo aprobatorio popular",
            constitutional_basis=req["constitutional_basis"]
        ))

    # Get timeline
    timeline = get_legislative_timeline(norm_type)

    # Get blockers
    blockers = get_common_blockers(norm_type)
    if custom_blockers:
        for cb in custom_blockers:
            blockers.append(PoliticalBlocker(**cb))

    # Estimate favorable votes if not provided
    if estimated_favorable is None:
        # Conservative estimate: 50% of total
        estimated_favorable = total_members // 2

    # Calculate feasibility
    feasibility_score, feasibility_level = calculate_feasibility(
        votes_needed,
        estimated_favorable,
        blockers
    )

    # Generate strategy recommendation
    if feasibility_level in [FeasibilityLevel.MUY_ALTA, FeasibilityLevel.ALTA]:
        strategy = "Proceder con trámite legislativo estándar. Alta probabilidad de éxito."
    elif feasibility_level == FeasibilityLevel.MEDIA:
        strategy = "Recomendable negociar con bloques minoritarios antes de someter a votación."
    else:
        strategy = "Considerar rutas alternativas o reformular el proyecto para obtener mayor consenso."

    # Alternative routes
    alternatives = []
    if norm_type == NormType.LEY_ORDINARIA:
        alternatives = [
            "Decreto con fuerza de ley (requiere Ley Habilitante vigente)",
            "Reglamento (si materia lo permite)",
            "Resolución ministerial (alcance limitado)"
        ]
    elif norm_type == NormType.LEY_ORGANICA:
        alternatives = [
            "Tramitar como ley ordinaria (si materia lo permite)",
            "Solicitar ley habilitante para decreto-ley"
        ]
    elif norm_type == NormType.ENMIENDA:
        alternatives = [
            "Reforma constitucional (si cambio es más amplio)",
            "Interpretación constitucional por Sala Constitucional"
        ]

    # Default composition if not provided
    if composition is None:
        composition = {"Oficialismo": 190, "Oposición": 87}

    return VotingMap(
        norm_type=norm_type,
        title=title,
        description=description,
        total_an_members=total_members,
        current_composition=composition,
        voting_requirements=voting_requirements,
        timeline=timeline,
        blockers=blockers,
        feasibility_score=feasibility_score,
        feasibility_level=feasibility_level,
        recommended_strategy=strategy,
        alternative_routes=alternatives
    )


def analyze_proposal(
    title: str,
    norm_type_str: str,
    description: str = "",
    favorable_votes: Optional[int] = None
) -> Dict[str, Any]:
    """
    Analyze a legislative proposal and return complete voting map.

    Args:
        title: Proposal title
        norm_type_str: Type of norm as string
        description: Brief description
        favorable_votes: Estimated favorable votes

    Returns:
        Dictionary with complete analysis
    """
    # Parse norm type
    norm_type_map = {
        "ordinaria": NormType.LEY_ORDINARIA,
        "organica": NormType.LEY_ORGANICA,
        "habilitante": NormType.LEY_HABILITANTE,
        "decreto": NormType.DECRETO_LEY,
        "enmienda": NormType.ENMIENDA,
        "reforma": NormType.REFORMA,
        "constituyente": NormType.CONSTITUYENTE,
    }

    norm_type = norm_type_map.get(norm_type_str.lower(), NormType.LEY_ORDINARIA)

    # Generate voting map
    voting_map = generate_voting_map(
        norm_type=norm_type,
        title=title,
        description=description,
        estimated_favorable=favorable_votes
    )

    # Convert to dict for output
    result = {
        "title": voting_map.title,
        "norm_type": voting_map.norm_type.value,
        "description": voting_map.description,
        "total_members": voting_map.total_an_members,
        "composition": voting_map.current_composition,
        "voting_requirements": [
            {
                "phase": vr.phase.value,
                "voting_body": vr.voting_body.value,
                "majority_type": vr.majority_type.value,
                "quorum": f"{vr.quorum_required:.0%}",
                "votes_needed": vr.votes_needed,
                "description": vr.description,
                "constitutional_basis": vr.constitutional_basis
            }
            for vr in voting_map.voting_requirements
        ],
        "timeline": [
            {
                "phase": t.phase.value,
                "description": t.description,
                "duration": f"{t.min_days}-{t.max_days} días",
                "responsible": t.responsible,
                "requirements": t.requirements
            }
            for t in voting_map.timeline
        ],
        "blockers": [
            {
                "name": b.name,
                "severity": b.severity,
                "probability": f"{b.probability:.0%}",
                "mitigation": b.mitigation
            }
            for b in voting_map.blockers
        ],
        "feasibility": {
            "score": f"{voting_map.feasibility_score:.0%}",
            "level": voting_map.feasibility_level.value,
            "strategy": voting_map.recommended_strategy
        },
        "alternatives": voting_map.alternative_routes,
        "generated_at": voting_map.generated_at
    }

    return result


def get_majority_comparison() -> Dict[str, Any]:
    """Get comparison of all majority types and their requirements."""
    return {
        "total_members": AN_TOTAL_MEMBERS,
        "majorities": {
            "Simple (>50% presentes)": calculate_votes_needed(AN_TOTAL_MEMBERS, MajorityType.SIMPLE)[0],
            "Absoluta (>50% total)": calculate_votes_needed(AN_TOTAL_MEMBERS, MajorityType.ABSOLUTA)[0],
            "Calificada 2/3": calculate_votes_needed(AN_TOTAL_MEMBERS, MajorityType.CALIFICADA_2_3)[0],
            "Calificada 3/5": calculate_votes_needed(AN_TOTAL_MEMBERS, MajorityType.CALIFICADA_3_5)[0],
        },
        "quorum": calculate_votes_needed(AN_TOTAL_MEMBERS, MajorityType.SIMPLE)[1],
        "norm_requirements": {
            nt.value: {
                "majority": VOTING_REQUIREMENTS[nt]["majority"].value,
                "votes_needed": calculate_votes_needed(
                    AN_TOTAL_MEMBERS,
                    VOTING_REQUIREMENTS[nt]["majority"]
                )[0],
                "referendo": VOTING_REQUIREMENTS[nt]["referendo_required"]
            }
            for nt in VOTING_REQUIREMENTS.keys()
        }
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         ASCII DIAGRAM GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_ascii_diagram(voting_map: VotingMap) -> str:
    """Generate ASCII diagram for voting map."""
    lines = []
    lines.append("╔" + "═" * 78 + "╗")
    lines.append("║" + f" VOTING MAP: {voting_map.title[:60]}".ljust(78) + "║")
    lines.append("╠" + "═" * 78 + "╣")

    # Norm type and requirements
    lines.append("║" + f" Tipo de Norma: {voting_map.norm_type.value}".ljust(78) + "║")
    lines.append("║" + "─" * 78 + "║")

    # Votes needed
    for vr in voting_map.voting_requirements:
        if vr.voting_body == VotingBody.ASAMBLEA_NACIONAL:
            lines.append("║" + f" VOTOS REQUERIDOS: {vr.votes_needed} de {voting_map.total_an_members}".ljust(78) + "║")
            lines.append("║" + f" Tipo de Mayoría: {vr.majority_type.value}".ljust(78) + "║")
            lines.append("║" + f" Quórum: {vr.quorum_required:.0%} ({int(voting_map.total_an_members * vr.quorum_required)} diputados)".ljust(78) + "║")

    lines.append("║" + "─" * 78 + "║")

    # Feasibility
    bar_width = 40
    filled = int(voting_map.feasibility_score * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    lines.append("║" + f" FACTIBILIDAD: [{bar}] {voting_map.feasibility_score:.0%}".ljust(78) + "║")
    lines.append("║" + f" Nivel: {voting_map.feasibility_level.value}".ljust(78) + "║")

    lines.append("║" + "─" * 78 + "║")

    # Timeline summary
    total_min = sum(t.min_days for t in voting_map.timeline)
    total_max = sum(t.max_days for t in voting_map.timeline)
    lines.append("║" + f" DURACIÓN ESTIMADA: {total_min} - {total_max} días".ljust(78) + "║")

    lines.append("║" + "─" * 78 + "║")

    # Blockers count
    high_blockers = sum(1 for b in voting_map.blockers if b.severity == "Alta")
    lines.append("║" + f" BLOQUEADORES: {len(voting_map.blockers)} total ({high_blockers} de alta severidad)".ljust(78) + "║")

    lines.append("╚" + "═" * 78 + "╝")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def print_voting_map(voting_map: VotingMap) -> None:
    """Print formatted voting map."""
    print(generate_ascii_diagram(voting_map))

    print(f"\n{'═' * 80}")
    print("DETALLE DEL MAPA DE VOTACIÓN")
    print(f"{'═' * 80}")

    print(f"\n📋 DESCRIPCIÓN:")
    print(f"   {voting_map.description or 'Sin descripción'}")

    print(f"\n🗳️ REQUISITOS DE VOTACIÓN:")
    for vr in voting_map.voting_requirements:
        print(f"\n   ► {vr.phase.value}")
        print(f"     Órgano: {vr.voting_body.value}")
        print(f"     Mayoría: {vr.majority_type.value}")
        print(f"     Votos necesarios: {vr.votes_needed}")
        print(f"     Base constitucional: {vr.constitutional_basis}")

    print(f"\n📅 CRONOGRAMA LEGISLATIVO:")
    total_min = 0
    total_max = 0
    for t in voting_map.timeline:
        total_min += t.min_days
        total_max += t.max_days
        print(f"\n   {t.phase.value}")
        print(f"     └─ {t.description}")
        print(f"        Duración: {t.min_days}-{t.max_days} días")
        print(f"        Responsable: {t.responsible}")

    print(f"\n   ⏱️ TOTAL ESTIMADO: {total_min} - {total_max} días")

    print(f"\n⚠️ BLOQUEADORES POTENCIALES:")
    for b in voting_map.blockers:
        icon = "🔴" if b.severity == "Alta" else "🟡" if b.severity == "Media" else "🟢"
        print(f"\n   {icon} {b.name} [{b.severity}] - {b.probability:.0%} probabilidad")
        print(f"      Mitigación: {b.mitigation}")

    print(f"\n📊 ANÁLISIS DE FACTIBILIDAD:")
    print(f"   Puntaje: {voting_map.feasibility_score:.0%}")
    print(f"   Nivel: {voting_map.feasibility_level.value}")
    print(f"\n   💡 ESTRATEGIA RECOMENDADA:")
    print(f"   {voting_map.recommended_strategy}")

    if voting_map.alternative_routes:
        print(f"\n🔀 RUTAS ALTERNATIVAS:")
        for alt in voting_map.alternative_routes:
            print(f"   • {alt}")

    print(f"\n{'═' * 80}\n")


def main():
    """CLI interface for Voting Map Engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Venezuela Super Lawyer - Voting Map Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 voting_map.py analyze "Ley de X" --type ordinaria
  python3 voting_map.py analyze "Ley Orgánica de Y" --type organica --votes 200
  python3 voting_map.py analyze "Enmienda Art. 230" --type enmienda
  python3 voting_map.py compare
  python3 voting_map.py requirements ordinaria
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze legislative proposal")
    analyze_parser.add_argument("title", help="Proposal title")
    analyze_parser.add_argument("--type", "-t", required=True,
                                choices=["ordinaria", "organica", "habilitante",
                                        "decreto", "enmienda", "reforma", "constituyente"],
                                help="Type of norm")
    analyze_parser.add_argument("--description", "-d", default="",
                                help="Brief description")
    analyze_parser.add_argument("--votes", "-v", type=int,
                                help="Estimated favorable votes")
    analyze_parser.add_argument("--json", action="store_true",
                                help="Output as JSON")

    # Compare command
    subparsers.add_parser("compare", help="Compare majority requirements")

    # Requirements command
    req_parser = subparsers.add_parser("requirements", help="Show requirements for norm type")
    req_parser.add_argument("type", choices=["ordinaria", "organica", "habilitante",
                                             "decreto", "enmienda", "reforma", "constituyente"],
                           help="Type of norm")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "analyze":
        norm_type_map = {
            "ordinaria": NormType.LEY_ORDINARIA,
            "organica": NormType.LEY_ORGANICA,
            "habilitante": NormType.LEY_HABILITANTE,
            "decreto": NormType.DECRETO_LEY,
            "enmienda": NormType.ENMIENDA,
            "reforma": NormType.REFORMA,
            "constituyente": NormType.CONSTITUYENTE,
        }

        voting_map = generate_voting_map(
            norm_type=norm_type_map[args.type],
            title=args.title,
            description=args.description,
            estimated_favorable=args.votes
        )

        if args.json:
            result = analyze_proposal(args.title, args.type, args.description, args.votes)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_voting_map(voting_map)

    elif args.command == "compare":
        comparison = get_majority_comparison()
        print(f"\n{'═' * 60}")
        print("COMPARACIÓN DE MAYORÍAS - ASAMBLEA NACIONAL")
        print(f"{'═' * 60}")
        print(f"\nTotal de Diputados: {comparison['total_members']}")
        print(f"Quórum reglamentario: {comparison['quorum']} diputados")
        print(f"\n{'─' * 60}")
        print("VOTOS NECESARIOS POR TIPO DE MAYORÍA:")
        print(f"{'─' * 60}")
        for maj_type, votes in comparison['majorities'].items():
            print(f"  {maj_type}: {votes} votos")
        print(f"\n{'─' * 60}")
        print("REQUISITOS POR TIPO DE NORMA:")
        print(f"{'─' * 60}")
        for norm, req in comparison['norm_requirements'].items():
            ref = "✓" if req['referendo'] else "✗"
            print(f"  {norm}:")
            print(f"    Mayoría: {req['majority']}")
            print(f"    Votos: {req['votes_needed']}")
            print(f"    Referendo: {ref}")
        print()

    elif args.command == "requirements":
        norm_type_map = {
            "ordinaria": NormType.LEY_ORDINARIA,
            "organica": NormType.LEY_ORGANICA,
            "habilitante": NormType.LEY_HABILITANTE,
            "decreto": NormType.DECRETO_LEY,
            "enmienda": NormType.ENMIENDA,
            "reforma": NormType.REFORMA,
            "constituyente": NormType.CONSTITUYENTE,
        }
        norm_type = norm_type_map[args.type]
        req = VOTING_REQUIREMENTS.get(norm_type, VOTING_REQUIREMENTS[NormType.LEY_ORDINARIA])
        votes, quorum = calculate_votes_needed(AN_TOTAL_MEMBERS, req["majority"])

        print(f"\n{'═' * 60}")
        print(f"REQUISITOS: {norm_type.value.upper()}")
        print(f"{'═' * 60}")
        print(f"\nBase constitucional: {req['constitutional_basis']}")
        print(f"Tipo de mayoría: {req['majority'].value}")
        print(f"Votos necesarios: {votes} de {AN_TOTAL_MEMBERS}")
        print(f"Quórum: {quorum} diputados ({req['quorum']:.0%})")
        print(f"Número de discusiones: {req['discussions']}")
        print(f"Referendo requerido: {'Sí' if req['referendo_required'] else 'No'}")
        print()


if __name__ == "__main__":
    main()
