#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Report Manager
Manages automatic generation and updating of legal research reports in Markdown format.

PROTECTED FILE - Requires authentication via VSL_ACCESS_KEY environment variable.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Import security module for authentication
try:
    from security import verify_access, require_auth
except ImportError:
    # If running from different directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from security import verify_access, require_auth

# Default reports directory
DEFAULT_REPORTS_DIR = "reportes_legales"
REPORTS_DIR = Path(__file__).parent.parent / DEFAULT_REPORTS_DIR

# Report templates
REPORT_TEMPLATES = {
    "analysis": "Análisis Legal Completo",
    "constitutional": "Análisis Constitucional",
    "opinion": "Opinión Legal",
    "research": "Investigación Jurídica",
    "strategy": "Estrategia Legal"
}


def generate_report_header(title: str, case_name: str) -> str:
    """Generate a simple report header."""
    now = datetime.now()
    return f"""# {title}

═══════════════════════════════════════════════════════════════════════════════
                    VENEZUELA SUPER LAWYER - REPORTE
═══════════════════════════════════════════════════════════════════════════════

**Caso:** {case_name}
**Fecha:** {now.strftime("%Y-%m-%d %H:%M:%S")}
**Sistema:** Venezuela Super Lawyer v2.0

═══════════════════════════════════════════════════════════════════════════════

"""


def format_section(title: str, content: str) -> str:
    """Format a section with title and content."""
    return f"""
## {title}

{content}

---
"""


class ReportManager:
    """Manager class for legal report generation."""

    def __init__(self, reports_dir: Path = None):
        """Initialize report manager."""
        self.reports_dir = reports_dir or REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _generate_risk_indicator(self, score: float) -> str:
        """Generate visual risk indicator."""
        if score >= 75:
            return "🔴 ALTO"
        elif score >= 50:
            return "🟠 MEDIO-ALTO"
        elif score >= 25:
            return "🟡 MEDIO"
        else:
            return "🟢 BAJO"

    def _generate_enriched_executive_summary(
        self,
        case_name: str,
        workflow_type: str = None,
        constitutional_analysis: dict = None,
        constitutional_tests: dict = None,
        gaceta_results: dict = None,
        tsj_results: dict = None,
        voting_map: dict = None,
        hydrocarbons_analysis: dict = None,
        contract_review: dict = None,
        law_generation: dict = None
    ) -> str:
        """Generate a comprehensive executive summary with actionable insights."""
        summary = "## Resumen Ejecutivo\n\n"

        # Overall Assessment Box
        risk_score = 0
        if constitutional_analysis:
            risk_score = constitutional_analysis.get('risk_score', 0)

        summary += "### Evaluación General\n\n"
        summary += "```\n"
        summary += f"┌{'─'*60}┐\n"
        summary += f"│ {'CASO:':<15} {case_name:<43} │\n"
        summary += f"│ {'WORKFLOW:':<15} {(workflow_type or 'CASE_ANALYSIS'):<43} │\n"
        summary += f"│ {'RIESGO:':<15} {self._generate_risk_indicator(risk_score):<43} │\n"
        summary += f"└{'─'*60}┘\n"
        summary += "```\n\n"

        # Key Findings
        summary += "### Hallazgos Clave\n\n"
        findings = []

        if constitutional_analysis:
            conflicts = constitutional_analysis.get('conflicts_found', 0)
            compliance = constitutional_analysis.get('compliance_percentage', 100)
            if conflicts > 0:
                findings.append(f"⚠️ **{conflicts} conflicto(s) constitucional(es)** detectado(s) que requieren atención")
            if compliance < 80:
                findings.append(f"📊 Nivel de cumplimiento constitucional: **{compliance}%**")
            else:
                findings.append(f"✅ Alto nivel de cumplimiento constitucional: **{compliance}%**")

        if constitutional_tests:
            passed = constitutional_tests.get('tests_passed', 0)
            total = constitutional_tests.get('total_tests', 0)
            if total > 0:
                rate = (passed / total) * 100
                if rate >= 80:
                    findings.append(f"✅ Pruebas constitucionales aprobadas: **{passed}/{total}** ({rate:.0f}%)")
                else:
                    findings.append(f"⚠️ Pruebas constitucionales aprobadas: **{passed}/{total}** ({rate:.0f}%) - Requiere revisión")

        if gaceta_results:
            norms = gaceta_results.get('norms_found', 0)
            if norms > 0:
                findings.append(f"📚 **{norms} norma(s)** relevante(s) identificada(s) en Gaceta Oficial")

        if tsj_results:
            cases = tsj_results.get('cases_found', 0)
            binding = tsj_results.get('binding_precedents', 0)
            if cases > 0:
                findings.append(f"⚖️ **{cases} sentencia(s)** del TSJ encontrada(s) ({binding} vinculante(s))")

        if voting_map:
            votes = voting_map.get('votes_needed', 0)
            feasibility = voting_map.get('feasibility', 'N/A')
            findings.append(f"🗳️ Requisito de votación: **{votes} votos** - Factibilidad: **{feasibility}**")

        if hydrocarbons_analysis:
            activity = hydrocarbons_analysis.get('activity_type', 'N/A')
            reserved = hydrocarbons_analysis.get('reserved_to_state', False)
            findings.append(f"🛢️ Actividad hidrocarburos: **{activity}** {'(Reservada al Estado)' if reserved else ''}")

        if contract_review:
            overall_risk = contract_review.get('overall_risk', 'N/A')
            compliance_score = contract_review.get('compliance_score', 0)
            findings.append(f"📋 Revisión contractual: Riesgo **{overall_risk}** - Cumplimiento **{compliance_score}%**")

        if law_generation:
            article_count = law_generation.get('article_count', 0)
            inst_type = law_generation.get('instrument_type', 'N/A')
            findings.append(f"📜 Instrumento legal generado: **{inst_type}** con **{article_count} artículos**")

        if not findings:
            findings.append("ℹ️ Análisis en proceso - No se han detectado hallazgos críticos")

        for finding in findings:
            summary += f"- {finding}\n"

        summary += "\n"

        # Recommendations Box
        summary += "### Recomendaciones Prioritarias\n\n"
        recommendations = []

        if constitutional_analysis and constitutional_analysis.get('conflicts_found', 0) > 0:
            recommendations.append("1. **Revisar conflictos constitucionales** antes de proceder")
            conflicts = constitutional_analysis.get('conflicts', [])
            if conflicts:
                for c in conflicts[:3]:
                    art = c.get('article', 'N/A')
                    recommendations.append(f"   - Artículo {art} CRBV: {c.get('recommendation', 'Revisar')[:80]}")

        if voting_map:
            feasibility = voting_map.get('feasibility', '').lower()
            if feasibility == 'baja':
                recommendations.append("2. **Considerar estrategia política** - Factibilidad legislativa baja")
            elif feasibility == 'media':
                recommendations.append("2. **Desarrollar alianzas políticas** para mejorar factibilidad")

        if hydrocarbons_analysis and hydrocarbons_analysis.get('reserved_to_state'):
            recommendations.append("3. **Verificar cumplimiento de Art. 9 LOH** - Participación estatal requerida")

        if not recommendations:
            recommendations.append("1. **Continuar con el proceso** - No se identifican obstáculos críticos")
            recommendations.append("2. **Monitorear cambios normativos** que puedan afectar el caso")

        for rec in recommendations:
            summary += f"{rec}\n"

        summary += "\n---\n\n"
        return summary

    def generate_analysis_report(
        self,
        case_name: str,
        workflow_type: str = None,
        constitutional_analysis: dict = None,
        constitutional_tests: dict = None,
        gaceta_results: dict = None,
        tsj_results: dict = None,
        voting_map: dict = None,
        hydrocarbons_analysis: dict = None,
        contract_review: dict = None,
        law_generation: dict = None,
        brainstorm: dict = None,
        intake_data: dict = None
    ) -> str:
        """Generate a comprehensive analysis report with enriched content."""
        now = datetime.now()

        content = generate_report_header("Análisis Legal Integral", case_name)

        # Enriched Executive Summary
        content += self._generate_enriched_executive_summary(
            case_name=case_name,
            workflow_type=workflow_type,
            constitutional_analysis=constitutional_analysis,
            constitutional_tests=constitutional_tests,
            gaceta_results=gaceta_results,
            tsj_results=tsj_results,
            voting_map=voting_map,
            hydrocarbons_analysis=hydrocarbons_analysis,
            contract_review=contract_review,
            law_generation=law_generation
        )

        # Intake Summary (if available)
        if intake_data:
            content += "## Datos del Caso\n\n"
            content += "| Campo | Valor |\n"
            content += "|-------|-------|\n"
            if intake_data.get('client_name'):
                content += f"| Cliente | {intake_data.get('client_name')} |\n"
            if intake_data.get('problem_statement'):
                content += f"| Problema | {intake_data.get('problem_statement')[:100]}... |\n"
            if intake_data.get('sector'):
                content += f"| Sector | {intake_data.get('sector')} |\n"
            if intake_data.get('norm_type'):
                content += f"| Tipo de Norma | {intake_data.get('norm_type')} |\n"
            content += "\n---\n\n"

        # Brainstorm Results (if available)
        if brainstorm:
            content += "## Análisis Preliminar (Brainstorm)\n\n"
            if brainstorm.get('legal_issues'):
                content += "### Cuestiones Jurídicas Identificadas\n\n"
                for issue in brainstorm.get('legal_issues', [])[:5]:
                    content += f"- {issue}\n"
                content += "\n"
            if brainstorm.get('applicable_laws'):
                content += "### Normativa Aplicable\n\n"
                for law in brainstorm.get('applicable_laws', [])[:5]:
                    content += f"- {law}\n"
                content += "\n"
            content += "---\n\n"

        # Constitutional Analysis (Enhanced)
        if constitutional_analysis:
            content += "## Análisis Constitucional\n\n"
            content += "### Métricas de Cumplimiento\n\n"
            content += "| Indicador | Valor | Estado |\n"
            content += "|-----------|-------|--------|\n"
            risk = constitutional_analysis.get('risk_score', 0)
            compliance = constitutional_analysis.get('compliance_percentage', 100)
            conflicts = constitutional_analysis.get('conflicts_found', 0)
            content += f"| Riesgo Constitucional | {risk}% | {self._generate_risk_indicator(risk)} |\n"
            content += f"| Cumplimiento | {compliance}% | {'✅' if compliance >= 80 else '⚠️'} |\n"
            content += f"| Conflictos Detectados | {conflicts} | {'✅' if conflicts == 0 else '⚠️'} |\n"
            content += "\n"

            if constitutional_analysis.get('conflicts'):
                content += "### Conflictos Identificados\n\n"
                for i, c in enumerate(constitutional_analysis.get('conflicts', [])[:5], 1):
                    content += f"#### Conflicto {i}: Artículo {c.get('article')} CRBV\n\n"
                    content += f"- **Tipo:** {c.get('conflict_type', 'N/A')}\n"
                    content += f"- **Descripción:** {c.get('description', 'N/A')}\n"
                    content += f"- **Severidad:** {c.get('severity', 'N/A')}\n"
                    content += f"- **Recomendación:** {c.get('recommendation', 'N/A')}\n\n"

            if constitutional_analysis.get('eternity_clause_violations'):
                content += "### ⚠️ Violaciones de Cláusulas Pétreas\n\n"
                for violation in constitutional_analysis.get('eternity_clause_violations', []):
                    content += f"- **CRÍTICO:** {violation}\n"
                content += "\n"

            content += "---\n\n"

        # Constitutional Tests (Enhanced)
        if constitutional_tests:
            content += "## Pruebas Constitucionales\n\n"
            passed = constitutional_tests.get('tests_passed', 0)
            total = constitutional_tests.get('total_tests', 0)
            score = constitutional_tests.get('overall_score', 0)

            content += f"**Resultado General:** {passed}/{total} pruebas aprobadas ({score:.1f}%)\n\n"
            content += "### Detalle de Pruebas\n\n"
            content += "| Prueba | Resultado | Puntuación |\n"
            content += "|--------|-----------|------------|\n"

            for test in constitutional_tests.get('tests', [])[:10]:
                status = "✅" if test.get('passed') else "❌"
                content += f"| {test.get('test_name', 'N/A')} | {status} | {test.get('score', 0):.0f}% |\n"

            content += "\n---\n\n"

        # Gaceta Results (Enhanced)
        if gaceta_results:
            content += "## Verificación Gaceta Oficial\n\n"
            norms = gaceta_results.get('norms_found', 0)
            content += f"**Normas Encontradas:** {norms}\n\n"

            if gaceta_results.get('norms'):
                content += "### Normas Relevantes\n\n"
                content += "| Gaceta | Fecha | Tipo | Título |\n"
                content += "|--------|-------|------|--------|\n"
                for norm in gaceta_results.get('norms', [])[:10]:
                    content += f"| {norm.get('gaceta_numero', 'N/A')} | {norm.get('fecha', 'N/A')} | {norm.get('tipo', 'N/A')} | {norm.get('titulo', 'N/A')[:40]}... |\n"
                content += "\n"

            content += "---\n\n"

        # TSJ Research (Enhanced)
        if tsj_results:
            content += "## Jurisprudencia TSJ\n\n"
            cases = tsj_results.get('cases_found', 0)
            binding = tsj_results.get('binding_precedents', 0)
            content += f"**Casos Encontrados:** {cases} ({binding} vinculantes)\n\n"

            if tsj_results.get('decisions'):
                content += "### Sentencias Relevantes\n\n"
                for decision in tsj_results.get('decisions', [])[:5]:
                    content += f"#### {decision.get('expediente', 'N/A')} - {decision.get('sala', 'N/A')}\n\n"
                    content += f"- **Fecha:** {decision.get('fecha', 'N/A')}\n"
                    content += f"- **Magistrado Ponente:** {decision.get('magistrado_ponente', 'N/A')}\n"
                    content += f"- **Materia:** {decision.get('materia', 'N/A')}\n"
                    content += f"- **Vinculante:** {'Sí' if decision.get('vinculante') else 'No'}\n"
                    if decision.get('resumen'):
                        content += f"- **Resumen:** {decision.get('resumen')[:200]}...\n"
                    content += "\n"

            content += "---\n\n"

        # Hydrocarbons Analysis (New)
        if hydrocarbons_analysis:
            content += "## Análisis de Hidrocarburos (LOH)\n\n"
            content += "### Clasificación de Actividad\n\n"
            content += "| Aspecto | Valor |\n"
            content += "|---------|-------|\n"
            content += f"| Tipo de Actividad | {hydrocarbons_analysis.get('activity_type', 'N/A')} |\n"
            content += f"| Reservada al Estado | {'Sí' if hydrocarbons_analysis.get('reserved_to_state') else 'No'} |\n"
            content += f"| Requiere Empresa Mixta | {'Sí' if hydrocarbons_analysis.get('empresa_mixta_required') else 'No'} |\n"
            content += f"| Participación Privada Permitida | {'Sí' if hydrocarbons_analysis.get('private_participation_allowed') else 'No'} |\n"
            content += "\n"

            if hydrocarbons_analysis.get('fiscal_obligations'):
                content += "### Obligaciones Fiscales\n\n"
                content += "| Obligación | Tasa | Base | Artículo LOH |\n"
                content += "|------------|------|------|-------------|\n"
                for obligation in hydrocarbons_analysis.get('fiscal_obligations', []):
                    content += f"| {obligation.get('name', 'N/A')} | {obligation.get('rate', 'N/A')} | {obligation.get('base', 'N/A')} | Art. {obligation.get('loh_article', 'N/A')} |\n"
                content += "\n"

            if hydrocarbons_analysis.get('empresa_mixta'):
                em = hydrocarbons_analysis.get('empresa_mixta')
                content += "### Análisis de Empresa Mixta\n\n"
                content += f"- **Participación PDVSA:** {em.get('pdvsa_participation', 0)}%\n"
                content += f"- **Participación Privada:** {em.get('private_participation', 0)}%\n"
                content += f"- **Cumplimiento Art. 9 LOH:** {'✅ Sí' if em.get('art_9_loh_compliant') else '❌ No'}\n"
                content += "\n"

            content += "---\n\n"

        # Contract Review (New)
        if contract_review:
            content += "## Revisión Contractual\n\n"
            content += f"**Tipo de Contrato:** {contract_review.get('contract_type', 'N/A')}\n"
            content += f"**Riesgo General:** {contract_review.get('overall_risk', 'N/A')}\n"
            content += f"**Puntuación de Cumplimiento:** {contract_review.get('compliance_score', 0)}%\n\n"

            if contract_review.get('risk_patterns'):
                content += "### Patrones de Riesgo Identificados\n\n"
                for pattern in contract_review.get('risk_patterns', [])[:5]:
                    content += f"- **{pattern.get('pattern_name', 'N/A')}** ({pattern.get('risk_level', 'N/A')}): {pattern.get('description', 'N/A')}\n"
                content += "\n"

            if contract_review.get('missing_clauses'):
                content += "### Cláusulas Faltantes\n\n"
                for clause in contract_review.get('missing_clauses', []):
                    content += f"- ⚠️ {clause}\n"
                content += "\n"

            content += "---\n\n"

        # Law Generation (New)
        if law_generation:
            content += "## Instrumento Legal Generado\n\n"
            content += f"**Tipo:** {law_generation.get('instrument_type', 'N/A')}\n"
            content += f"**Título:** {law_generation.get('title', 'N/A')}\n"
            content += f"**Artículos:** {law_generation.get('article_count', 0)}\n\n"

            if law_generation.get('roadmap'):
                roadmap = law_generation.get('roadmap')
                content += "### Hoja de Ruta de Implementación\n\n"
                content += f"**Duración Total:** {roadmap.get('total_days', 0)} días\n\n"
                content += "| Fase | Nombre | Duración |\n"
                content += "|------|--------|----------|\n"
                for phase in roadmap.get('phases', [])[:6]:
                    content += f"| {phase.get('phase_number', 'N/A')} | {phase.get('name', 'N/A')} | {phase.get('duration_days', 0)} días |\n"
                content += "\n"

            content += "---\n\n"

        # Voting Map (Enhanced)
        if voting_map:
            content += "## Mapa de Votación Legislativa\n\n"
            content += "### Requisitos de Aprobación\n\n"
            content += "| Aspecto | Valor |\n"
            content += "|---------|-------|\n"
            content += f"| Votos Necesarios | {voting_map.get('votes_needed', 'N/A')} |\n"
            content += f"| Total Diputados | {voting_map.get('total_deputies', 277)} |\n"
            content += f"| Tipo de Mayoría | {voting_map.get('majority_type', 'N/A')} |\n"
            content += f"| Factibilidad | {voting_map.get('feasibility', 'N/A')} |\n"
            content += "\n"

            if voting_map.get('procedural_steps'):
                content += "### Pasos Procedimentales\n\n"
                for i, step in enumerate(voting_map.get('procedural_steps', []), 1):
                    content += f"{i}. {step}\n"
                content += "\n"

            content += "---\n\n"

        # Footer
        content += f"""
═══════════════════════════════════════════════════════════════════════════════
                    VENEZUELA SUPER LAWYER v2.0
                    Generado: {now.strftime('%Y-%m-%d %H:%M:%S')}
                    Workflow: {workflow_type or 'CASE_ANALYSIS'}
═══════════════════════════════════════════════════════════════════════════════
"""
        return content

    def save_report(self, case_name: str, content: str) -> str:
        """Save report to file and return path."""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{date_str}_{sanitize_filename(case_name)}.md"
        report_path = self.reports_dir / filename
        report_path.write_text(content, encoding='utf-8')
        return str(report_path)


def sanitize_filename(name: str) -> str:
    """Convert a string to a valid filename."""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    sanitized = sanitized[:50]
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized


def generate_report_id(topic: str = None, case_number: str = None) -> str:
    """Generate a unique report identifier."""
    date_str = datetime.now().strftime("%Y%m%d")
    time_str = datetime.now().strftime("%H%M%S")

    if case_number:
        return f"{date_str}_{sanitize_filename(case_number)}"
    elif topic:
        return f"{date_str}_{sanitize_filename(topic)}"
    else:
        return f"{date_str}_{time_str}_consulta"


def get_report_path(report_id: str, base_dir: str = None) -> Path:
    """Get the full path for a report file."""
    if base_dir is None:
        base_dir = os.getcwd()

    reports_dir = Path(base_dir) / DEFAULT_REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)

    return reports_dir / f"{report_id}.md"


def get_escudo_ascii() -> str:
    """Return the ASCII art header for Venezuela Super Lawyer."""
    return """
        ██╗   ██╗███████╗███╗   ██╗███████╗███████╗██╗   ██╗███████╗██╗      █████╗
        ██║   ██║██╔════╝████╗  ██║██╔════╝╚══███╔╝██║   ██║██╔════╝██║     ██╔══██╗
        ██║   ██║█████╗  ██╔██╗ ██║█████╗    ███╔╝ ██║   ██║█████╗  ██║     ███████║
        ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██╔══╝   ███╔╝  ██║   ██║██╔══╝  ██║     ██╔══██║
         ╚████╔╝ ███████╗██║ ╚████║███████╗███████╗╚██████╔╝███████╗███████╗██║  ██║
          ╚═══╝  ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

        ███████╗██╗   ██╗██████╗ ███████╗██████╗     ██╗      █████╗ ██╗    ██╗██╗   ██╗███████╗██████╗
        ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗    ██║     ██╔══██╗██║    ██║╚██╗ ██╔╝██╔════╝██╔══██╗
        ███████╗██║   ██║██████╔╝█████╗  ██████╔╝    ██║     ███████║██║ █╗ ██║ ╚████╔╝ █████╗  ██████╔╝
        ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗    ██║     ██╔══██║██║███╗██║  ╚██╔╝  ██╔══╝  ██╔══██╗
        ███████║╚██████╔╝██║     ███████╗██║  ██║    ███████╗██║  ██║╚███╔███╔╝   ██║   ███████╗██║  ██║
        ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝    ╚═╝   ╚══════╝╚═╝  ╚═╝

    ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    ║                              AI LEGAL OPERATING SYSTEM v2.0                                         ║
    ═══════════════════════════════════════════════════════════════════════════════════════════════════════
"""


def create_report_header(
    report_id: str,
    topic: str,
    case_number: str = None,
    client: str = None,
    report_type: str = "Consulta Legal",
    file_path: str = None
) -> str:
    """Create the standard header for a legal report with ASCII Escudo."""

    now = datetime.now()

    # Get file path for display
    if file_path is None:
        file_path = f"./reportes_legales/{report_id}.md"

    header = get_escudo_ascii()

    header += f"""
═══════════════════════════════════════════════════════════════════════════════
                         VENEZUELA SUPER LAWYER
                    AI LEGAL OPERATING SYSTEM v2.0
═══════════════════════════════════════════════════════════════════════════════

# {topic}

┌──────────────────────────────────────────────────────────────────────────────┐
│                         INFORMACIÓN DEL REPORTE                              │
├─────────────────────────┬────────────────────────────────────────────────────┤
│ ID Reporte              │ {report_id:<50} │
│ Fecha de Creación       │ {now.strftime("%Y-%m-%d"):<50} │
│ Hora                    │ {now.strftime("%H:%M:%S"):<50} │
│ Tipo                    │ {report_type:<50} │
"""

    if case_number:
        header += f"│ Número de Caso          │ {case_number:<50} │\n"

    if client:
        header += f"│ Cliente                 │ {client:<50} │\n"
    else:
        header += f"│ Cliente                 │ {'CONFIDENCIAL':<50} │\n"

    header += f"""│ Autor                   │ {'VENEZUELA SUPER LAWYER — AI Legal OS':<50} │
│ Ubicación Archivo       │ {file_path:<50} │
│ Última Actualización    │ {now.strftime('%Y-%m-%d %H:%M:%S'):<50} │
└─────────────────────────┴────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

## Índice de Contenidos

<!-- TOC_START -->
*Índice generado automáticamente*
<!-- TOC_END -->

---

"""
    return header


def create_section(
    section_number: int,
    section_title: str,
    content: str,
    timestamp: bool = True
) -> str:
    """Create a new section for the report."""

    section = f"\n## {section_number}. {section_title}\n\n"

    if timestamp:
        now = datetime.now()
        section += f"*Agregado: {now.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

    section += content
    section += "\n\n---\n"

    return section


def append_to_report(
    report_path: Path,
    section_title: str,
    content: str,
    section_number: int = None
) -> int:
    """Append a new section to an existing report. Returns the section number."""

    if not report_path.exists():
        raise FileNotFoundError(f"Report not found: {report_path}")

    existing_content = report_path.read_text(encoding='utf-8')

    # Find the last section number
    section_pattern = r'^## (\d+)\.'
    matches = re.findall(section_pattern, existing_content, re.MULTILINE)

    if section_number is None:
        if matches:
            section_number = max(int(m) for m in matches) + 1
        else:
            section_number = 1

    # Update the "Última Actualización" field
    now = datetime.now()
    update_pattern = r'\| \*\*Última Actualización\*\* \| .+ \|'
    updated_content = re.sub(
        update_pattern,
        f"| **Última Actualización** | {now.strftime('%Y-%m-%d %H:%M:%S')} |",
        existing_content
    )

    # Add the new section
    new_section = create_section(section_number, section_title, content)
    updated_content += new_section

    # Write back
    report_path.write_text(updated_content, encoding='utf-8')

    return section_number


def create_new_report(
    topic: str,
    initial_content: str,
    case_number: str = None,
    client: str = None,
    report_type: str = "Consulta Legal",
    base_dir: str = None
) -> Path:
    """Create a new report file with initial content."""

    report_id = generate_report_id(topic=topic, case_number=case_number)
    report_path = get_report_path(report_id, base_dir)

    # Create header with file path
    content = create_report_header(
        report_id=report_id,
        topic=topic,
        case_number=case_number,
        client=client,
        report_type=report_type,
        file_path=str(report_path)
    )

    # Add initial content as first section
    content += create_section(1, "Consulta Inicial", initial_content)

    # Add footer
    content += create_report_footer()

    # Write file
    report_path.write_text(content, encoding='utf-8')

    print(f"✅ Reporte creado: {report_path}")
    return report_path


def create_report_footer() -> str:
    """Create the standard footer for a legal report."""

    now = datetime.now()

    return f"""
═══════════════════════════════════════════════════════════════════════════════

## Aviso Legal

Este documento fue generado por **VENEZUELA SUPER LAWYER**, un sistema de
inteligencia artificial legal especializado en derecho venezolano.

**La información contenida en este reporte:**

1. ⚖️ **No constituye asesoría legal formal** — Consulte con un abogado colegiado
2. 📚 **Se basa en fuentes públicas** — Verificar vigencia de normas citadas
3. 🔒 **Es confidencial** — Solo para uso del destinatario indicado

**Fuentes Primarias:**
- Constitución de la República Bolivariana de Venezuela (CRBV 1999)
- Gaceta Oficial de la República Bolivariana de Venezuela
- Jurisprudencia del Tribunal Supremo de Justicia (TSJ)
- Leyes Orgánicas y Ordinarias vigentes

**Jerarquía Normativa Aplicada:**
```
CRBV (Supremacía Constitucional)
    └── Leyes Orgánicas
        └── Leyes Ordinarias
            └── Decretos-Ley
                └── Reglamentos
                    └── Resoluciones
```

═══════════════════════════════════════════════════════════════════════════════
     VENEZUELA SUPER LAWYER — AI Legal Operating System v2.0
     "Supremacía Constitucional • Precisión Jurídica • Soluciones Reales"

     Generado: {now.strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════════════════════
"""


def update_toc(report_path: Path) -> None:
    """Update the table of contents in a report."""

    content = report_path.read_text(encoding='utf-8')

    # Find all section headers
    section_pattern = r'^## (\d+)\. (.+)$'
    matches = re.findall(section_pattern, content, re.MULTILINE)

    # Generate TOC
    toc_lines = []
    for num, title in matches:
        # Create anchor-friendly version of title
        anchor = title.lower().replace(' ', '-').replace('.', '')
        anchor = re.sub(r'[^a-z0-9-]', '', anchor)
        toc_lines.append(f"- [{num}. {title}](#{num}-{anchor})")

    toc_content = "\n".join(toc_lines) if toc_lines else "*No hay secciones aún*"

    # Replace TOC
    toc_pattern = r'<!-- TOC_START -->.*?<!-- TOC_END -->'
    new_toc = f"<!-- TOC_START -->\n{toc_content}\n<!-- TOC_END -->"

    updated_content = re.sub(toc_pattern, new_toc, content, flags=re.DOTALL)

    report_path.write_text(updated_content, encoding='utf-8')


def list_reports(base_dir: str = None) -> List[Dict]:
    """List all existing reports."""

    if base_dir is None:
        base_dir = os.getcwd()

    reports_dir = Path(base_dir) / DEFAULT_REPORTS_DIR

    if not reports_dir.exists():
        return []

    reports = []
    for report_file in reports_dir.glob("*.md"):
        content = report_file.read_text(encoding='utf-8')

        # Extract metadata
        id_match = re.search(r'\| \*\*ID Reporte\*\* \| `(.+?)` \|', content)
        date_match = re.search(r'\| \*\*Fecha de Creación\*\* \| (.+?) \|', content)
        type_match = re.search(r'\| \*\*Tipo\*\* \| (.+?) \|', content)
        update_match = re.search(r'\| \*\*Última Actualización\*\* \| (.+?) \|', content)

        # Extract title (first H1)
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)

        reports.append({
            'file': report_file.name,
            'path': str(report_file),
            'id': id_match.group(1) if id_match else report_file.stem,
            'title': title_match.group(1) if title_match else 'Sin título',
            'date': date_match.group(1) if date_match else 'Desconocida',
            'type': type_match.group(1) if type_match else 'Desconocido',
            'last_update': update_match.group(1) if update_match else 'Desconocida'
        })

    # Sort by date (newest first)
    reports.sort(key=lambda x: x['date'], reverse=True)

    return reports


def print_reports_index(base_dir: str = None) -> None:
    """Print a formatted index of all reports."""

    reports = list_reports(base_dir)

    if not reports:
        print("No hay reportes generados aún.")
        return

    print("\n" + "=" * 80)
    print("ÍNDICE DE REPORTES LEGALES — VENEZUELA SUPER LAWYER")
    print("=" * 80 + "\n")

    print(f"{'ID':<30} {'Fecha':<12} {'Tipo':<20} {'Título':<30}")
    print("-" * 92)

    for report in reports:
        title = report['title'][:28] + '..' if len(report['title']) > 30 else report['title']
        print(f"{report['id']:<30} {report['date']:<12} {report['type']:<20} {title:<30}")

    print("\n" + "=" * 80)
    print(f"Total: {len(reports)} reporte(s)")
    print("=" * 80 + "\n")


def get_latest_report(base_dir: str = None) -> Optional[Path]:
    """Get the path to the most recently updated report."""

    reports = list_reports(base_dir)

    if not reports:
        return None

    return Path(reports[0]['path'])


@require_auth
def main():
    """Main function for CLI usage. Requires authentication."""

    if len(sys.argv) < 2:
        print("Venezuela Super Lawyer - Report Manager")
        print("\nUsage:")
        print("  python3 report_manager.py new <topic> [--case <case_number>] [--client <client>]")
        print("  python3 report_manager.py append <report_id> <section_title> <content_file>")
        print("  python3 report_manager.py list")
        print("  python3 report_manager.py latest")
        print("  python3 report_manager.py toc <report_id>")
        print("\nExamples:")
        print("  python3 report_manager.py new 'Análisis Ley Hidrocarburos'")
        print("  python3 report_manager.py new 'Contrato PDVSA' --case '2026-001' --client 'Empresa XYZ'")
        print("  python3 report_manager.py list")
        sys.exit(0)

    command = sys.argv[1]

    if command == "new":
        if len(sys.argv) < 3:
            print("Error: Topic required")
            sys.exit(1)

        topic = sys.argv[2]
        case_number = None
        client = None

        # Parse optional arguments
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == "--case" and i + 1 < len(sys.argv):
                case_number = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--client" and i + 1 < len(sys.argv):
                client = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        report_path = create_new_report(
            topic=topic,
            initial_content="*Consulta iniciada. Contenido pendiente.*",
            case_number=case_number,
            client=client
        )
        print(f"Reporte creado en: {report_path}")

    elif command == "list":
        print_reports_index()

    elif command == "latest":
        latest = get_latest_report()
        if latest:
            print(f"Último reporte: {latest}")
        else:
            print("No hay reportes.")

    elif command == "toc":
        if len(sys.argv) < 3:
            print("Error: Report ID required")
            sys.exit(1)

        report_id = sys.argv[2]
        report_path = get_report_path(report_id)

        if report_path.exists():
            update_toc(report_path)
            print(f"TOC actualizado en: {report_path}")
        else:
            print(f"Error: Report not found: {report_path}")

    elif command == "append":
        if len(sys.argv) < 5:
            print("Error: report_id, section_title, and content_file required")
            sys.exit(1)

        report_id = sys.argv[2]
        section_title = sys.argv[3]
        content_file = sys.argv[4]

        report_path = get_report_path(report_id)

        if not report_path.exists():
            print(f"Error: Report not found: {report_path}")
            sys.exit(1)

        if not os.path.exists(content_file):
            print(f"Error: Content file not found: {content_file}")
            sys.exit(1)

        content = Path(content_file).read_text(encoding='utf-8')
        section_num = append_to_report(report_path, section_title, content)
        update_toc(report_path)

        print(f"Sección {section_num} agregada a: {report_path}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
