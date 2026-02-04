#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Module 16: Law & Resolution Generation Engine

Generates complete legal instruments (leyes, decretos, reglamentos, resoluciones)
with proper Venezuelan legal format, constitutional compliance, and implementation roadmaps.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


# ═══════════════════════════════════════════════════════════════════════════════
#                         ENUMS AND DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class InstrumentType(Enum):
    """Types of legal instruments."""
    LEY_ORDINARIA = "Ley Ordinaria"
    LEY_ORGANICA = "Ley Orgánica"
    DECRETO_LEY = "Decreto con Rango, Valor y Fuerza de Ley"
    DECRETO = "Decreto"
    RESOLUCION = "Resolución"
    REGLAMENTO = "Reglamento"
    PROVIDENCIA = "Providencia Administrativa"
    NORMA_TECNICA = "Norma Técnica"


class EnforcementType(Enum):
    """Types of enforcement mechanisms."""
    CRIMINAL = "criminal"
    ADMINISTRATIVE = "administrative"
    CIVIL = "civil"
    INCENTIVES = "incentives"
    MIXED = "mixed"


class ArticleType(Enum):
    """Types of articles in legal instruments."""
    OBJETO = "objeto"
    AMBITO = "ambito"
    DEFINICIONES = "definiciones"
    PRINCIPIOS = "principios"
    DERECHOS = "derechos"
    OBLIGACIONES = "obligaciones"
    PROHIBICIONES = "prohibiciones"
    PROCEDIMIENTO = "procedimiento"
    SANCIONES = "sanciones"
    ORGANO_RECTOR = "organo_rector"
    FINANCIAMIENTO = "financiamiento"
    TRANSITORIO = "transitorio"
    DEROGATORIA = "derogatoria"
    VIGENCIA = "vigencia"


@dataclass
class LegalArticle:
    """Represents a single article in a legal instrument."""
    numero: int
    titulo: str
    contenido: str
    tipo: ArticleType
    crbv_fundamento: List[int] = field(default_factory=list)  # CRBV articles as legal basis
    notas: str = ""

    def to_text(self) -> str:
        """Convert article to legal text format."""
        text = f"**Artículo {self.numero}.** _{self.titulo}_\n\n"
        text += self.contenido
        if self.crbv_fundamento:
            text += f"\n\n_Fundamento constitucional: Artículos {', '.join(map(str, self.crbv_fundamento))} CRBV_"
        return text

    def to_dict(self) -> Dict:
        return {
            "numero": self.numero,
            "titulo": self.titulo,
            "contenido": self.contenido,
            "tipo": self.tipo.value,
            "crbv_fundamento": self.crbv_fundamento,
            "notas": self.notas
        }


@dataclass
class LegalInstrument:
    """Complete legal instrument with all components."""
    tipo: InstrumentType
    titulo: str
    exposicion_motivos: str
    considerandos: List[str]
    articulos: List[LegalArticle]
    disposiciones_transitorias: List[str]
    disposicion_derogatoria: str
    disposicion_final: str
    fecha_sancion: Optional[str] = None
    gaceta_numero: Optional[str] = None
    organo_emisor: str = "ASAMBLEA NACIONAL DE LA REPÚBLICA BOLIVARIANA DE VENEZUELA"

    def get_article_count(self) -> int:
        return len(self.articulos)

    def get_articles_by_type(self, tipo: ArticleType) -> List[LegalArticle]:
        return [a for a in self.articulos if a.tipo == tipo]

    def to_full_text(self) -> str:
        """Generate complete legal instrument text."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(f"REPÚBLICA BOLIVARIANA DE VENEZUELA")
        lines.append(f"{self.organo_emisor}")
        lines.append("=" * 80)
        lines.append("")

        # Title
        lines.append(f"# {self.tipo.value.upper()}")
        lines.append(f"## {self.titulo}")
        lines.append("")

        # Exposición de Motivos
        lines.append("---")
        lines.append("## EXPOSICIÓN DE MOTIVOS")
        lines.append("")
        lines.append(self.exposicion_motivos)
        lines.append("")

        # Considerandos
        lines.append("---")
        lines.append("## CONSIDERANDOS")
        lines.append("")
        for i, considerando in enumerate(self.considerandos, 1):
            lines.append(f"**CONSIDERANDO {self._roman(i)}:** {considerando}")
            lines.append("")

        # Decreta/Sanciona
        lines.append("---")
        if self.tipo in [InstrumentType.LEY_ORDINARIA, InstrumentType.LEY_ORGANICA]:
            lines.append("## LA ASAMBLEA NACIONAL DECRETA")
        elif self.tipo == InstrumentType.DECRETO_LEY:
            lines.append("## EL PRESIDENTE DE LA REPÚBLICA EN CONSEJO DE MINISTROS DECRETA")
        elif self.tipo == InstrumentType.RESOLUCION:
            lines.append("## EL MINISTRO DEL PODER POPULAR RESUELVE")
        else:
            lines.append("## SE DECRETA")
        lines.append("")

        # Título I - Disposiciones Generales (objeto, ámbito, definiciones)
        general_articles = [a for a in self.articulos if a.tipo in [
            ArticleType.OBJETO, ArticleType.AMBITO, ArticleType.DEFINICIONES, ArticleType.PRINCIPIOS
        ]]
        if general_articles:
            lines.append("### TÍTULO I")
            lines.append("### DISPOSICIONES GENERALES")
            lines.append("")
            for art in general_articles:
                lines.append(art.to_text())
                lines.append("")

        # Título II - Derechos y Obligaciones
        rights_articles = [a for a in self.articulos if a.tipo in [
            ArticleType.DERECHOS, ArticleType.OBLIGACIONES
        ]]
        if rights_articles:
            lines.append("### TÍTULO II")
            lines.append("### DE LOS DERECHOS Y OBLIGACIONES")
            lines.append("")
            for art in rights_articles:
                lines.append(art.to_text())
                lines.append("")

        # Título III - Prohibiciones y Sanciones
        sanction_articles = [a for a in self.articulos if a.tipo in [
            ArticleType.PROHIBICIONES, ArticleType.SANCIONES
        ]]
        if sanction_articles:
            lines.append("### TÍTULO III")
            lines.append("### DEL RÉGIMEN SANCIONATORIO")
            lines.append("")
            for art in sanction_articles:
                lines.append(art.to_text())
                lines.append("")

        # Título IV - Procedimientos
        procedure_articles = [a for a in self.articulos if a.tipo == ArticleType.PROCEDIMIENTO]
        if procedure_articles:
            lines.append("### TÍTULO IV")
            lines.append("### DE LOS PROCEDIMIENTOS")
            lines.append("")
            for art in procedure_articles:
                lines.append(art.to_text())
                lines.append("")

        # Título V - Órgano Rector y Financiamiento
        institutional_articles = [a for a in self.articulos if a.tipo in [
            ArticleType.ORGANO_RECTOR, ArticleType.FINANCIAMIENTO
        ]]
        if institutional_articles:
            lines.append("### TÍTULO V")
            lines.append("### DEL ÓRGANO RECTOR Y FINANCIAMIENTO")
            lines.append("")
            for art in institutional_articles:
                lines.append(art.to_text())
                lines.append("")

        # Disposiciones Transitorias
        if self.disposiciones_transitorias:
            lines.append("---")
            lines.append("## DISPOSICIONES TRANSITORIAS")
            lines.append("")
            for i, transitoria in enumerate(self.disposiciones_transitorias, 1):
                lines.append(f"**PRIMERA (transitoria {i}):** {transitoria}")
                lines.append("")

        # Disposición Derogatoria
        lines.append("---")
        lines.append("## DISPOSICIÓN DEROGATORIA")
        lines.append("")
        lines.append(f"**ÚNICA:** {self.disposicion_derogatoria}")
        lines.append("")

        # Disposición Final
        lines.append("---")
        lines.append("## DISPOSICIÓN FINAL")
        lines.append("")
        lines.append(f"**ÚNICA:** {self.disposicion_final}")
        lines.append("")

        # Footer
        lines.append("---")
        if self.fecha_sancion:
            lines.append(f"_Dada, firmada y sellada en el Palacio Federal Legislativo, sede de la Asamblea Nacional, en Caracas, a los {self.fecha_sancion}._")
        if self.gaceta_numero:
            lines.append(f"\n_Publicada en Gaceta Oficial N° {self.gaceta_numero}_")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        return {
            "tipo": self.tipo.value,
            "titulo": self.titulo,
            "exposicion_motivos": self.exposicion_motivos,
            "considerandos": self.considerandos,
            "articulos": [a.to_dict() for a in self.articulos],
            "disposiciones_transitorias": self.disposiciones_transitorias,
            "disposicion_derogatoria": self.disposicion_derogatoria,
            "disposicion_final": self.disposicion_final,
            "fecha_sancion": self.fecha_sancion,
            "gaceta_numero": self.gaceta_numero,
            "organo_emisor": self.organo_emisor,
            "article_count": self.get_article_count()
        }

    @staticmethod
    def _roman(num: int) -> str:
        """Convert number to Roman numeral."""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num


@dataclass
class ImplementationPhase:
    """Phase of implementation roadmap."""
    fase: int
    nombre: str
    duracion_dias: int
    descripcion: str
    actividades: List[str]
    responsables: List[str]
    entregables: List[str]
    riesgos: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ImplementationRoadmap:
    """Complete implementation roadmap for legal instrument."""
    instrument_title: str
    total_phases: int
    total_days: int
    phases: List[ImplementationPhase]
    dependencies: List[str]
    budget_estimate: str
    success_metrics: List[str]
    monitoring_mechanism: str

    def to_dict(self) -> Dict:
        return {
            "instrument_title": self.instrument_title,
            "total_phases": self.total_phases,
            "total_days": self.total_days,
            "phases": [p.to_dict() for p in self.phases],
            "dependencies": self.dependencies,
            "budget_estimate": self.budget_estimate,
            "success_metrics": self.success_metrics,
            "monitoring_mechanism": self.monitoring_mechanism
        }

    def to_markdown(self) -> str:
        """Generate markdown roadmap."""
        lines = []
        lines.append(f"# Hoja de Ruta de Implementación")
        lines.append(f"## {self.instrument_title}")
        lines.append("")
        lines.append(f"**Total de Fases:** {self.total_phases}")
        lines.append(f"**Duración Estimada:** {self.total_days} días ({self.total_days // 30} meses aprox.)")
        lines.append(f"**Presupuesto Estimado:** {self.budget_estimate}")
        lines.append("")

        lines.append("## Cronograma de Fases")
        lines.append("")
        lines.append("```")
        current_day = 0
        for phase in self.phases:
            end_day = current_day + phase.duracion_dias
            lines.append(f"Fase {phase.fase}: {phase.nombre}")
            lines.append(f"  Días {current_day + 1}-{end_day} ({phase.duracion_dias} días)")
            current_day = end_day
        lines.append("```")
        lines.append("")

        for phase in self.phases:
            lines.append(f"### Fase {phase.fase}: {phase.nombre}")
            lines.append(f"**Duración:** {phase.duracion_dias} días")
            lines.append("")
            lines.append(phase.descripcion)
            lines.append("")

            lines.append("**Actividades:**")
            for act in phase.actividades:
                lines.append(f"- {act}")
            lines.append("")

            lines.append("**Responsables:**")
            for resp in phase.responsables:
                lines.append(f"- {resp}")
            lines.append("")

            lines.append("**Entregables:**")
            for ent in phase.entregables:
                lines.append(f"- {ent}")
            lines.append("")

            if phase.riesgos:
                lines.append("**Riesgos:**")
                for risk in phase.riesgos:
                    lines.append(f"- ⚠️ {risk}")
                lines.append("")

        lines.append("## Dependencias")
        for dep in self.dependencies:
            lines.append(f"- {dep}")
        lines.append("")

        lines.append("## Métricas de Éxito")
        for metric in self.success_metrics:
            lines.append(f"- {metric}")
        lines.append("")

        lines.append("## Mecanismo de Monitoreo")
        lines.append(self.monitoring_mechanism)

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
#                         TEMPLATE GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

# Constitutional basis articles by topic
CRBV_BASIS = {
    "rights": [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
    "property": [115, 116, 117],
    "economic": [112, 113, 114, 118, 299, 300, 301, 302, 303, 304],
    "labor": [87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97],
    "environment": [127, 128, 129],
    "health": [83, 84, 85, 86],
    "education": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
    "hydrocarbons": [12, 302, 303],
    "mining": [12, 302],
    "telecom": [108, 110],
    "banking": [318, 319, 320],
    "taxes": [316, 317],
    "administration": [141, 143, 144, 145, 146],
    "due_process": [49],
    "judicial": [253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267],
}


def generate_standard_articles(
    objeto: str,
    ambito: str,
    definiciones: Dict[str, str],
    principios: List[str],
    sector: str = "general",
    enforcement: EnforcementType = EnforcementType.ADMINISTRATIVE
) -> List[LegalArticle]:
    """Generate standard articles for any legal instrument."""
    articles = []
    article_num = 1

    # Article 1 - Objeto
    articles.append(LegalArticle(
        numero=article_num,
        titulo="Objeto",
        contenido=f"La presente Ley tiene por objeto {objeto}",
        tipo=ArticleType.OBJETO,
        crbv_fundamento=CRBV_BASIS.get(sector, [1, 2, 3])
    ))
    article_num += 1

    # Article 2 - Ámbito de Aplicación
    articles.append(LegalArticle(
        numero=article_num,
        titulo="Ámbito de Aplicación",
        contenido=f"Las disposiciones de esta Ley se aplican a {ambito}",
        tipo=ArticleType.AMBITO,
        crbv_fundamento=[156, 157, 158]  # Competencias
    ))
    article_num += 1

    # Article 3 - Definiciones
    if definiciones:
        def_text = "A los efectos de esta Ley se entiende por:\n\n"
        for i, (term, definition) in enumerate(definiciones.items(), 1):
            def_text += f"{i}. **{term}:** {definition}\n\n"
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Definiciones",
            contenido=def_text,
            tipo=ArticleType.DEFINICIONES
        ))
        article_num += 1

    # Article 4 - Principios
    if principios:
        princ_text = "La aplicación e interpretación de esta Ley se regirán por los siguientes principios:\n\n"
        for i, principio in enumerate(principios, 1):
            princ_text += f"{i}. {principio}\n"
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Principios Rectores",
            contenido=princ_text,
            tipo=ArticleType.PRINCIPIOS,
            crbv_fundamento=[2, 3, 7]  # Principios fundamentales
        ))
        article_num += 1

    return articles


def generate_sanction_articles(
    enforcement: EnforcementType,
    base_article_num: int = 20,
    sector: str = "general"
) -> List[LegalArticle]:
    """Generate sanction articles based on enforcement type."""
    articles = []
    article_num = base_article_num

    if enforcement == EnforcementType.CRIMINAL:
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Sanciones Penales",
            contenido="""Las personas naturales o jurídicas que incurran en las conductas tipificadas
en esta Ley serán sancionadas conforme a lo establecido en el Código Penal y leyes especiales,
sin perjuicio de las responsabilidades civiles y administrativas que correspondan.

Las penas privativas de libertad no serán susceptibles de beneficios procesales cuando
se trate de delitos cometidos contra el patrimonio público o que afecten intereses colectivos.""",
            tipo=ArticleType.SANCIONES,
            crbv_fundamento=[49, 257]
        ))

    elif enforcement == EnforcementType.ADMINISTRATIVE:
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Sanciones Administrativas",
            contenido="""Sin perjuicio de las responsabilidades civiles y penales que correspondan,
las infracciones a esta Ley serán sancionadas con:

1. **Amonestación escrita:** Para infracciones leves.

2. **Multa:** De cincuenta (50) a cinco mil (5.000) unidades tributarias (UT),
según la gravedad de la infracción.

3. **Suspensión temporal de actividades:** De treinta (30) a ciento ochenta (180) días.

4. **Revocatoria de permisos, licencias o autorizaciones:** Para infracciones graves reiteradas.

5. **Inhabilitación:** Para ejercer la actividad regulada por un período de uno (1) a cinco (5) años.

El procedimiento sancionatorio se regirá por lo establecido en la Ley Orgánica de
Procedimientos Administrativos, garantizando el derecho a la defensa y al debido proceso.""",
            tipo=ArticleType.SANCIONES,
            crbv_fundamento=[49, 141]
        ))

    elif enforcement == EnforcementType.CIVIL:
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Responsabilidad Civil",
            contenido="""Toda persona natural o jurídica que cause daños o perjuicios por
incumplimiento de las disposiciones de esta Ley estará obligada a la reparación integral
del daño causado.

La acción para reclamar la indemnización de daños y perjuicios prescribirá en el plazo
de cinco (5) años, contados a partir del momento en que el afectado tuvo o debió tener
conocimiento del daño.""",
            tipo=ArticleType.SANCIONES,
            crbv_fundamento=[115, 140]
        ))

    elif enforcement == EnforcementType.INCENTIVES:
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Incentivos y Beneficios",
            contenido="""El Estado promoverá el cumplimiento de esta Ley mediante los
siguientes incentivos:

1. **Incentivos fiscales:** Exoneraciones y rebajas de impuestos para quienes
cumplan con los estándares establecidos.

2. **Acceso preferencial:** A programas de financiamiento público y créditos blandos.

3. **Certificaciones:** Reconocimiento público mediante sellos y certificaciones
de cumplimiento.

4. **Prioridad en contrataciones:** Preferencia en procesos de contratación pública.

El órgano rector establecerá el procedimiento para acceder a estos incentivos.""",
            tipo=ArticleType.SANCIONES,
            crbv_fundamento=[112, 118, 299]
        ))

    else:  # MIXED
        articles.extend(generate_sanction_articles(EnforcementType.ADMINISTRATIVE, article_num))
        articles.extend(generate_sanction_articles(EnforcementType.CIVIL, article_num + 1))

    return articles


def generate_implementation_roadmap(
    instrument_title: str,
    instrument_type: InstrumentType,
    sector: str = "general",
    urgency: str = "normal"
) -> ImplementationRoadmap:
    """Generate implementation roadmap for legal instrument."""

    # Adjust timelines based on urgency
    time_multiplier = 0.5 if urgency == "emergency" else 1.0

    phases = []

    # Phase 1: Regulatory Development
    phases.append(ImplementationPhase(
        fase=1,
        nombre="Desarrollo Reglamentario",
        duracion_dias=int(90 * time_multiplier),
        descripcion="Elaboración del reglamento de la ley y normas técnicas complementarias.",
        actividades=[
            "Conformar comisión redactora del reglamento",
            "Realizar consulta con sectores afectados",
            "Redactar proyecto de reglamento",
            "Revisión jurídica del reglamento",
            "Aprobación y publicación en Gaceta Oficial"
        ],
        responsables=[
            "Ministerio del ramo",
            "Consultoría Jurídica",
            "Órgano rector (si existe)"
        ],
        entregables=[
            "Reglamento de la Ley",
            "Normas técnicas (si aplica)",
            "Manual de procedimientos"
        ],
        riesgos=[
            "Retrasos en consultas intersectoriales",
            "Conflictos con normativa existente"
        ]
    ))

    # Phase 2: Institutional Setup
    phases.append(ImplementationPhase(
        fase=2,
        nombre="Adecuación Institucional",
        duracion_dias=int(60 * time_multiplier),
        descripcion="Creación o fortalecimiento de la estructura institucional para aplicar la ley.",
        actividades=[
            "Identificar o crear órgano rector",
            "Definir estructura organizativa",
            "Asignar recursos humanos y presupuestarios",
            "Establecer sistemas de información",
            "Capacitar al personal"
        ],
        responsables=[
            "Ministerio del ramo",
            "Oficina de Planificación",
            "Recursos Humanos"
        ],
        entregables=[
            "Resolución de creación de unidad (si aplica)",
            "Manual de organización y funciones",
            "Plan de capacitación"
        ],
        riesgos=[
            "Insuficiencia presupuestaria",
            "Falta de personal calificado"
        ]
    ))

    # Phase 3: Communication and Outreach
    phases.append(ImplementationPhase(
        fase=3,
        nombre="Divulgación y Sensibilización",
        duracion_dias=int(45 * time_multiplier),
        descripcion="Campaña de comunicación para dar a conocer la ley a los destinatarios.",
        actividades=[
            "Diseñar estrategia de comunicación",
            "Elaborar materiales divulgativos",
            "Realizar talleres y jornadas informativas",
            "Publicar en medios oficiales y redes",
            "Establecer canales de consulta ciudadana"
        ],
        responsables=[
            "Oficina de Comunicaciones",
            "Órgano rector",
            "Defensoría del Pueblo (si aplica)"
        ],
        entregables=[
            "Guías para ciudadanos y empresas",
            "Portal web informativo",
            "Línea de atención al ciudadano"
        ],
        riesgos=[
            "Bajo alcance de la comunicación",
            "Desinformación o interpretaciones erróneas"
        ]
    ))

    # Phase 4: Pilot Implementation
    phases.append(ImplementationPhase(
        fase=4,
        nombre="Implementación Piloto",
        duracion_dias=int(90 * time_multiplier),
        descripcion="Aplicación gradual de la ley en áreas o regiones seleccionadas.",
        actividades=[
            "Seleccionar áreas piloto",
            "Aplicar procedimientos en casos reales",
            "Documentar lecciones aprendidas",
            "Ajustar procedimientos según resultados",
            "Evaluar indicadores de cumplimiento"
        ],
        responsables=[
            "Órgano rector",
            "Autoridades regionales/locales",
            "Equipos técnicos"
        ],
        entregables=[
            "Informe de resultados del piloto",
            "Procedimientos ajustados",
            "Indicadores de gestión"
        ],
        riesgos=[
            "Resistencia de actores afectados",
            "Inconsistencias en la aplicación"
        ]
    ))

    # Phase 5: Full Deployment
    phases.append(ImplementationPhase(
        fase=5,
        nombre="Despliegue Nacional",
        duracion_dias=int(120 * time_multiplier),
        descripcion="Aplicación plena de la ley en todo el territorio nacional.",
        actividades=[
            "Extender aplicación a todo el país",
            "Coordinar con autoridades regionales",
            "Activar régimen sancionatorio",
            "Monitorear cumplimiento",
            "Resolver casos conflictivos"
        ],
        responsables=[
            "Órgano rector",
            "Ministerios relacionados",
            "Gobernaciones y Alcaldías"
        ],
        entregables=[
            "Reportes periódicos de cumplimiento",
            "Base de datos de casos",
            "Estadísticas de aplicación"
        ],
        riesgos=[
            "Capacidad institucional insuficiente",
            "Litigios por aplicación de sanciones"
        ]
    ))

    # Phase 6: Evaluation and Adjustment
    phases.append(ImplementationPhase(
        fase=6,
        nombre="Evaluación y Ajuste",
        duracion_dias=int(60 * time_multiplier),
        descripcion="Evaluación de resultados y propuesta de ajustes normativos.",
        actividades=[
            "Evaluar cumplimiento de objetivos",
            "Identificar vacíos o inconsistencias",
            "Proponer reformas si es necesario",
            "Actualizar procedimientos",
            "Publicar informe de evaluación"
        ],
        responsables=[
            "Órgano rector",
            "Asamblea Nacional (para reformas)",
            "Contraloría (para auditoría)"
        ],
        entregables=[
            "Informe de evaluación integral",
            "Propuesta de reformas (si aplica)",
            "Plan de mejora continua"
        ],
        riesgos=[
            "Falta de datos para evaluación",
            "Resistencia a cambios"
        ]
    ))

    total_days = sum(p.duracion_dias for p in phases)

    return ImplementationRoadmap(
        instrument_title=instrument_title,
        total_phases=len(phases),
        total_days=total_days,
        phases=phases,
        dependencies=[
            "Publicación en Gaceta Oficial",
            "Asignación presupuestaria",
            "Designación de autoridades responsables",
            "Coordinación interministerial"
        ],
        budget_estimate="A determinar según estudio de impacto regulatorio",
        success_metrics=[
            "Porcentaje de destinatarios que conocen la ley",
            "Número de procedimientos aplicados",
            "Tiempo promedio de resolución de casos",
            "Nivel de cumplimiento de obligaciones",
            "Reducción de conflictos o problemas regulados"
        ],
        monitoring_mechanism="""Se establecerá un sistema de monitoreo que incluya:
1. Tablero de indicadores actualizado trimestralmente
2. Informes semestrales al órgano legislativo
3. Auditorías anuales de la Contraloría General
4. Consulta ciudadana anual sobre satisfacción"""
    )


# ═══════════════════════════════════════════════════════════════════════════════
#                         MAIN GENERATOR FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_legal_instrument(
    titulo: str,
    objeto: str,
    ambito: str,
    tipo: InstrumentType = InstrumentType.LEY_ORDINARIA,
    sector: str = "general",
    enforcement: EnforcementType = EnforcementType.ADMINISTRATIVE,
    definiciones: Optional[Dict[str, str]] = None,
    principios: Optional[List[str]] = None,
    derechos: Optional[List[str]] = None,
    obligaciones: Optional[List[str]] = None,
    prohibiciones: Optional[List[str]] = None,
    procedimientos: Optional[List[str]] = None,
    transitorias: Optional[List[str]] = None,
    exposicion_motivos: Optional[str] = None,
    considerandos: Optional[List[str]] = None,
    generate_roadmap: bool = True,
    urgency: str = "normal"
) -> Tuple[LegalInstrument, Optional[ImplementationRoadmap]]:
    """
    Generate a complete legal instrument with all components.

    Args:
        titulo: Title of the instrument
        objeto: Object/purpose of the law
        ambito: Scope of application
        tipo: Type of instrument
        sector: Sector (hydrocarbons, banking, etc.)
        enforcement: Type of enforcement mechanism
        definiciones: Dictionary of definitions
        principios: List of guiding principles
        derechos: List of rights to include
        obligaciones: List of obligations
        prohibiciones: List of prohibitions
        procedimientos: List of procedures
        transitorias: List of transitory provisions
        exposicion_motivos: Exposition of motives
        considerandos: List of considerandos
        generate_roadmap: Whether to generate implementation roadmap
        urgency: Urgency level (normal/emergency)

    Returns:
        Tuple of (LegalInstrument, ImplementationRoadmap or None)
    """

    # Default values
    definiciones = definiciones or {}
    principios = principios or [
        "Legalidad",
        "Transparencia",
        "Eficiencia",
        "Participación ciudadana",
        "Responsabilidad"
    ]

    # Generate default exposición de motivos if not provided
    if not exposicion_motivos:
        exposicion_motivos = f"""La presente {tipo.value} surge de la necesidad de {objeto.lower()}.

El marco constitucional venezolano, establecido en la Constitución de la República
Bolivariana de Venezuela de 1999, consagra los principios fundamentales que orientan
esta iniciativa legislativa.

La regulación propuesta busca llenar un vacío normativo existente, estableciendo
reglas claras y procedimientos eficientes que garanticen la seguridad jurídica
de todos los actores involucrados.

Se ha considerado la experiencia comparada y las mejores prácticas internacionales,
adaptándolas a la realidad venezolana y al marco constitucional vigente."""

    # Generate default considerandos if not provided
    if not considerandos:
        considerandos = [
            f"Que la Constitución de la República Bolivariana de Venezuela establece los principios fundamentales que rigen la materia de {sector}.",
            "Que es deber del Estado garantizar la seguridad jurídica y el bienestar de los ciudadanos.",
            "Que resulta necesario actualizar el marco normativo para adaptarlo a las nuevas realidades económicas y sociales.",
            "Que la Asamblea Nacional tiene la competencia exclusiva para legislar en esta materia, conforme al artículo 187 de la Constitución."
        ]

    # Generate articles
    articles = []

    # Standard articles (objeto, ámbito, definiciones, principios)
    articles.extend(generate_standard_articles(
        objeto=objeto,
        ambito=ambito,
        definiciones=definiciones,
        principios=principios,
        sector=sector,
        enforcement=enforcement
    ))

    article_num = len(articles) + 1

    # Rights articles
    if derechos:
        rights_text = "Son derechos de los sujetos regulados por esta Ley:\n\n"
        for i, derecho in enumerate(derechos, 1):
            rights_text += f"{i}. {derecho}\n"
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Derechos",
            contenido=rights_text,
            tipo=ArticleType.DERECHOS,
            crbv_fundamento=CRBV_BASIS.get("rights", [19, 20, 21])
        ))
        article_num += 1

    # Obligations articles
    if obligaciones:
        obl_text = "Son obligaciones de los sujetos regulados por esta Ley:\n\n"
        for i, obligacion in enumerate(obligaciones, 1):
            obl_text += f"{i}. {obligacion}\n"
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Obligaciones",
            contenido=obl_text,
            tipo=ArticleType.OBLIGACIONES
        ))
        article_num += 1

    # Prohibitions articles
    if prohibiciones:
        proh_text = "Quedan expresamente prohibidas las siguientes conductas:\n\n"
        for i, prohibicion in enumerate(prohibiciones, 1):
            proh_text += f"{i}. {prohibicion}\n"
        articles.append(LegalArticle(
            numero=article_num,
            titulo="Prohibiciones",
            contenido=proh_text,
            tipo=ArticleType.PROHIBICIONES
        ))
        article_num += 1

    # Procedure articles
    if procedimientos:
        for i, proc in enumerate(procedimientos, 1):
            articles.append(LegalArticle(
                numero=article_num,
                titulo=f"Procedimiento {i}",
                contenido=proc,
                tipo=ArticleType.PROCEDIMIENTO,
                crbv_fundamento=[49]  # Debido proceso
            ))
            article_num += 1

    # Sanction articles
    sanction_articles = generate_sanction_articles(enforcement, article_num, sector)
    articles.extend(sanction_articles)
    article_num += len(sanction_articles)

    # Órgano rector article
    articles.append(LegalArticle(
        numero=article_num,
        titulo="Órgano Rector",
        contenido=f"""El Ministerio del Poder Popular con competencia en la materia será
el órgano rector de esta Ley, con las siguientes atribuciones:

1. Formular y ejecutar las políticas públicas en la materia.
2. Dictar las normas técnicas y procedimientos complementarios.
3. Fiscalizar el cumplimiento de esta Ley y su Reglamento.
4. Imponer las sanciones previstas en esta Ley.
5. Llevar el registro de los sujetos regulados.
6. Emitir las autorizaciones, permisos y licencias que correspondan.
7. Coordinar con otros órganos del Estado la aplicación de esta Ley.""",
        tipo=ArticleType.ORGANO_RECTOR,
        crbv_fundamento=[141, 156, 178]
    ))

    # Default transitory provisions
    if not transitorias:
        transitorias = [
            f"Los sujetos regulados por esta Ley dispondrán de un plazo de ciento ochenta (180) días, contados a partir de su publicación en Gaceta Oficial, para adecuarse a sus disposiciones.",
            "El Ejecutivo Nacional dictará el Reglamento de esta Ley en un plazo de noventa (90) días contados a partir de su publicación.",
            "Los procedimientos iniciados antes de la entrada en vigencia de esta Ley se regirán por la normativa anterior."
        ]

    # Create instrument
    instrument = LegalInstrument(
        tipo=tipo,
        titulo=titulo,
        exposicion_motivos=exposicion_motivos,
        considerandos=considerandos,
        articulos=articles,
        disposiciones_transitorias=transitorias,
        disposicion_derogatoria="Se derogan todas las disposiciones que colidan con la presente Ley.",
        disposicion_final="Esta Ley entrará en vigencia a partir de su publicación en la Gaceta Oficial de la República Bolivariana de Venezuela.",
        organo_emisor=_get_emisor(tipo)
    )

    # Generate roadmap if requested
    roadmap = None
    if generate_roadmap:
        roadmap = generate_implementation_roadmap(titulo, tipo, sector, urgency)

    return instrument, roadmap


def _get_emisor(tipo: InstrumentType) -> str:
    """Get the issuing authority based on instrument type."""
    if tipo in [InstrumentType.LEY_ORDINARIA, InstrumentType.LEY_ORGANICA]:
        return "ASAMBLEA NACIONAL DE LA REPÚBLICA BOLIVARIANA DE VENEZUELA"
    elif tipo in [InstrumentType.DECRETO_LEY, InstrumentType.DECRETO]:
        return "PRESIDENCIA DE LA REPÚBLICA BOLIVARIANA DE VENEZUELA"
    elif tipo in [InstrumentType.RESOLUCION, InstrumentType.PROVIDENCIA]:
        return "MINISTERIO DEL PODER POPULAR"
    else:
        return "REPÚBLICA BOLIVARIANA DE VENEZUELA"


# ═══════════════════════════════════════════════════════════════════════════════
#                         SECTOR-SPECIFIC GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_hydrocarbons_instrument(
    titulo: str,
    objeto: str,
    ambito: str = "todas las actividades de exploración, explotación, refinación, industrialización, transporte, almacenamiento y comercialización de hidrocarburos en el territorio nacional",
    **kwargs
) -> Tuple[LegalInstrument, Optional[ImplementationRoadmap]]:
    """Generate legal instrument for hydrocarbons sector."""

    definiciones = {
        "Hidrocarburos": "Compuestos orgánicos constituidos por carbono e hidrógeno, en estado sólido, líquido o gaseoso.",
        "Actividades Primarias": "Exploración y explotación de yacimientos de hidrocarburos.",
        "Actividades Secundarias": "Refinación, industrialización, transporte, almacenamiento y comercialización.",
        "Empresa Mixta": "Sociedad anónima constituida con participación de PDVSA o sus filiales y empresas privadas.",
        "Canon de Superficie": "Contraprestación por el uso del suelo para actividades de hidrocarburos.",
        "Regalía": "Participación del Estado en los hidrocarburos extraídos, antes de cualquier deducción.",
        "PDVSA": "Petróleos de Venezuela, S.A., empresa estatal de hidrocarburos."
    }

    principios = [
        "Soberanía petrolera",
        "Propiedad estatal de los hidrocarburos",
        "Participación mayoritaria del Estado en las actividades primarias",
        "Desarrollo sustentable y protección ambiental",
        "Maximización de la renta petrolera para el beneficio social"
    ]

    obligaciones = [
        "Cumplir con los planes de inversión comprometidos",
        "Mantener niveles óptimos de producción según las cuotas OPEP",
        "Garantizar el abastecimiento del mercado interno",
        "Aplicar las mejores prácticas de seguridad y ambiente",
        "Contribuir al desarrollo de las comunidades aledañas",
        "Proporcionar información veraz a las autoridades competentes",
        "Mantener reservas probadas y certificadas actualizadas"
    ]

    prohibiciones = [
        "Exportar hidrocarburos sin autorización del Ministerio",
        "Disponer de reservas de hidrocarburos sin la debida autorización",
        "Incumplir las cuotas de producción establecidas",
        "Realizar actividades que comprometan la seguridad energética nacional",
        "Efectuar prácticas que afecten negativamente los yacimientos"
    ]

    return generate_legal_instrument(
        titulo=titulo,
        objeto=objeto,
        ambito=ambito,
        sector="hydrocarbons",
        enforcement=EnforcementType.MIXED,
        definiciones=definiciones,
        principios=principios,
        obligaciones=obligaciones,
        prohibiciones=prohibiciones,
        **kwargs
    )


def generate_banking_instrument(
    titulo: str,
    objeto: str,
    ambito: str = "las instituciones del sector bancario, las operaciones bancarias y los servicios financieros en el territorio nacional",
    **kwargs
) -> Tuple[LegalInstrument, Optional[ImplementationRoadmap]]:
    """Generate legal instrument for banking sector."""

    definiciones = {
        "Institución Bancaria": "Persona jurídica autorizada para captar recursos del público y otorgar créditos.",
        "SUDEBAN": "Superintendencia de las Instituciones del Sector Bancario.",
        "BCV": "Banco Central de Venezuela.",
        "Encaje Legal": "Porcentaje de depósitos que las instituciones deben mantener como reserva.",
        "Cartera de Crédito Obligatoria": "Porcentaje del patrimonio destinado a sectores prioritarios.",
        "Gavetas Crediticias": "Cuotas de crédito destinadas a sectores específicos."
    }

    principios = [
        "Estabilidad del sistema financiero",
        "Protección del ahorrista",
        "Transparencia en las operaciones",
        "Acceso inclusivo a los servicios bancarios",
        "Prevención del lavado de capitales"
    ]

    return generate_legal_instrument(
        titulo=titulo,
        objeto=objeto,
        ambito=ambito,
        sector="banking",
        enforcement=EnforcementType.ADMINISTRATIVE,
        definiciones=definiciones,
        principios=principios,
        **kwargs
    )


def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about the law generator module.

    Returns module capabilities and configuration.
    """
    return {
        "module": "Law Generator (Module 16)",
        "version": __version__,
        "instrument_types_supported": [t.value for t in InstrumentType],
        "enforcement_types_supported": [e.value for e in EnforcementType],
        "article_types_available": [a.value for a in ArticleType],
        "sector_generators": {
            "hydrocarbons": "generate_hydrocarbons_instrument()",
            "banking": "generate_banking_instrument()",
            "general": "generate_legal_instrument()"
        },
        "features": [
            "Complete legal instrument generation",
            "Proper Venezuelan legal format",
            "Implementation roadmap generation",
            "Sector-specific templates",
            "Multiple enforcement mechanisms"
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for law generator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Venezuela Super Lawyer - Law Generator (Module 16)"
    )
    parser.add_argument(
        "titulo",
        help="Title of the legal instrument"
    )
    parser.add_argument(
        "--objeto", "-o",
        required=True,
        help="Object/purpose of the law"
    )
    parser.add_argument(
        "--ambito", "-a",
        default="todo el territorio nacional",
        help="Scope of application"
    )
    parser.add_argument(
        "--tipo", "-t",
        choices=["LEY_ORDINARIA", "LEY_ORGANICA", "DECRETO_LEY", "DECRETO", "RESOLUCION"],
        default="LEY_ORDINARIA",
        help="Type of instrument"
    )
    parser.add_argument(
        "--sector", "-s",
        choices=["hydrocarbons", "banking", "labor", "telecom", "healthcare", "general"],
        default="general",
        help="Sector"
    )
    parser.add_argument(
        "--enforcement", "-e",
        choices=["criminal", "administrative", "civil", "incentives", "mixed"],
        default="administrative",
        help="Enforcement mechanism"
    )
    parser.add_argument(
        "--urgency", "-u",
        choices=["normal", "emergency"],
        default="normal",
        help="Urgency level"
    )
    parser.add_argument(
        "--output", "-O",
        choices=["json", "text", "both"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--save-to",
        help="Save output to file"
    )
    parser.add_argument(
        "--no-roadmap",
        action="store_true",
        help="Skip implementation roadmap generation"
    )

    args = parser.parse_args()

    # Map enums
    tipo_map = {
        "LEY_ORDINARIA": InstrumentType.LEY_ORDINARIA,
        "LEY_ORGANICA": InstrumentType.LEY_ORGANICA,
        "DECRETO_LEY": InstrumentType.DECRETO_LEY,
        "DECRETO": InstrumentType.DECRETO,
        "RESOLUCION": InstrumentType.RESOLUCION
    }

    enforcement_map = {
        "criminal": EnforcementType.CRIMINAL,
        "administrative": EnforcementType.ADMINISTRATIVE,
        "civil": EnforcementType.CIVIL,
        "incentives": EnforcementType.INCENTIVES,
        "mixed": EnforcementType.MIXED
    }

    # Generate based on sector
    if args.sector == "hydrocarbons":
        instrument, roadmap = generate_hydrocarbons_instrument(
            titulo=args.titulo,
            objeto=args.objeto,
            ambito=args.ambito,
            tipo=tipo_map[args.tipo],
            urgency=args.urgency,
            generate_roadmap=not args.no_roadmap
        )
    elif args.sector == "banking":
        instrument, roadmap = generate_banking_instrument(
            titulo=args.titulo,
            objeto=args.objeto,
            ambito=args.ambito,
            tipo=tipo_map[args.tipo],
            urgency=args.urgency,
            generate_roadmap=not args.no_roadmap
        )
    else:
        instrument, roadmap = generate_legal_instrument(
            titulo=args.titulo,
            objeto=args.objeto,
            ambito=args.ambito,
            tipo=tipo_map[args.tipo],
            sector=args.sector,
            enforcement=enforcement_map[args.enforcement],
            urgency=args.urgency,
            generate_roadmap=not args.no_roadmap
        )

    # Output
    if args.output in ["json", "both"]:
        output = {
            "instrument": instrument.to_dict(),
            "roadmap": roadmap.to_dict() if roadmap else None
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))

    if args.output in ["text", "both"]:
        if args.output == "both":
            print("\n" + "=" * 80 + "\n")
        print(instrument.to_full_text())
        if roadmap:
            print("\n" + "=" * 80 + "\n")
            print(roadmap.to_markdown())

    # Save to file
    if args.save_to:
        with open(args.save_to, 'w', encoding='utf-8') as f:
            f.write(instrument.to_full_text())
            if roadmap:
                f.write("\n\n" + "=" * 80 + "\n\n")
                f.write(roadmap.to_markdown())
        print(f"\nSaved to: {args.save_to}")


if __name__ == "__main__":
    main()
