#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Gaceta Oficial Verification Script
Verifies norm currency and generates Gaceta Oficial citations.

EXPANDED DATABASE: 45+ Major Venezuelan Laws and Codes

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import sys
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional
from enum import Enum


class NormStatus(Enum):
    VIGENTE = "Vigente"
    DEROGADA = "Derogada"
    MODIFICADA = "Modificada"
    PARCIALMENTE_DEROGADA = "Parcialmente Derogada"
    SUSPENDIDA = "Suspendida"
    DESCONOCIDO = "Desconocido"


class GacetaType(Enum):
    ORDINARIA = "Ordinaria"
    EXTRAORDINARIA = "Extraordinaria"


class NormType(Enum):
    CONSTITUCION = "Constitución"
    LEY_ORGANICA = "Ley Orgánica"
    LEY_ORDINARIA = "Ley Ordinaria"
    CODIGO = "Código"
    DECRETO_LEY = "Decreto con Rango, Valor y Fuerza de Ley"
    REGLAMENTO = "Reglamento"
    RESOLUCION = "Resolución"


@dataclass
class GacetaEntry:
    gaceta_number: str
    gaceta_type: GacetaType
    date: str
    description: str
    action: str  # "Publicación original", "Reforma", "Derogación", etc.


@dataclass
class NormVerification:
    norm_name: str
    norm_type: NormType
    verification_date: str
    status: NormStatus
    original_publication: Optional[GacetaEntry]
    reforms: List[GacetaEntry]
    current_text_source: Optional[GacetaEntry]
    notes: str
    citation: str
    warnings: List[str]
    keywords: List[str]


def format_gaceta_citation(
    norm_name: str,
    gaceta_number: str,
    gaceta_type: GacetaType,
    date: str,
    status: NormStatus,
    last_reform: Optional[GacetaEntry] = None
) -> str:
    """Format a proper Gaceta Oficial citation."""

    citation = f"{norm_name}, Gaceta Oficial {gaceta_type.value} No. {gaceta_number}, {date}\n"
    citation += f"Vigencia: {status.value}"

    if last_reform and status == NormStatus.MODIFICADA:
        citation += f"\nÚltima reforma: {last_reform.date}, Gaceta No. {last_reform.gaceta_number}"

    return citation


def create_verification_report(verification: NormVerification) -> str:
    """Generate a markdown verification report."""

    md = f"""# Gaceta Oficial Verification Report

**Norm:** {verification.norm_name}
**Type:** {verification.norm_type.value}
**Verification Date:** {verification.verification_date}
**Status:** {verification.status.value}

---

## Citation

```
{verification.citation}
```

---

## Publication History

### Original Publication
"""

    if verification.original_publication:
        op = verification.original_publication
        md += f"""
| Field | Value |
|-------|-------|
| Gaceta Number | {op.gaceta_number} |
| Type | {op.gaceta_type.value} |
| Date | {op.date} |
| Description | {op.description} |
"""
    else:
        md += "\n*Original publication data not available*\n"

    md += "\n### Reforms and Modifications\n"

    if verification.reforms:
        md += "\n| Date | Gaceta No. | Type | Action | Description |\n"
        md += "|------|------------|------|--------|-------------|\n"
        for reform in verification.reforms:
            md += f"| {reform.date} | {reform.gaceta_number} | {reform.gaceta_type.value} | {reform.action} | {reform.description} |\n"
    else:
        md += "\n*No reforms recorded*\n"

    md += "\n---\n\n## Current Text Source\n"

    if verification.current_text_source:
        cts = verification.current_text_source
        md += f"""
The current authoritative text can be found in:
- **Gaceta:** {cts.gaceta_type.value} No. {cts.gaceta_number}
- **Date:** {cts.date}
- **Description:** {cts.description}
"""
    else:
        md += "\n*Current text source not specified*\n"

    if verification.keywords:
        md += f"\n---\n\n## Keywords\n`{', '.join(verification.keywords)}`\n"

    if verification.warnings:
        md += "\n---\n\n## ⚠️ Warnings\n\n"
        for warning in verification.warnings:
            md += f"- {warning}\n"

    if verification.notes:
        md += f"\n---\n\n## Notes\n\n{verification.notes}\n"

    return md


def verify_norm(
    norm_name: str,
    norm_type: str = "Ley Ordinaria",
    gaceta_number: str = "",
    gaceta_type: str = "Ordinaria",
    publication_date: str = "",
    known_status: str = "Desconocido",
    reforms: List[dict] = None,
    notes: str = "",
    keywords: List[str] = None
) -> NormVerification:
    """Create a norm verification record."""

    reforms = reforms or []
    keywords = keywords or []

    # Parse norm type
    try:
        n_type = NormType(norm_type)
    except ValueError:
        n_type = NormType.LEY_ORDINARIA

    # Parse gaceta type
    try:
        g_type = GacetaType(gaceta_type)
    except ValueError:
        g_type = GacetaType.ORDINARIA

    # Parse status
    try:
        status = NormStatus(known_status)
    except ValueError:
        status = NormStatus.DESCONOCIDO

    # Create original publication entry if data provided
    original_pub = None
    if gaceta_number and publication_date:
        original_pub = GacetaEntry(
            gaceta_number=gaceta_number,
            gaceta_type=g_type,
            date=publication_date,
            description="Publicación original",
            action="Publicación original"
        )

    # Process reforms
    reform_entries = []
    for r in reforms:
        reform_entries.append(GacetaEntry(
            gaceta_number=r.get("gaceta_number", ""),
            gaceta_type=GacetaType(r.get("gaceta_type", "Ordinaria")),
            date=r.get("date", ""),
            description=r.get("description", ""),
            action=r.get("action", "Reforma")
        ))

    # Determine current text source
    current_source = reform_entries[-1] if reform_entries else original_pub

    # Generate warnings
    warnings = []
    if status == NormStatus.DESCONOCIDO:
        warnings.append("Status could not be verified. Manual verification required.")
    if not gaceta_number:
        warnings.append("Original Gaceta number not provided. Citation may be incomplete.")
    if not publication_date:
        warnings.append("Publication date not provided. Citation may be incomplete.")
    if status == NormStatus.MODIFICADA and not reform_entries:
        warnings.append("Norm marked as modified but no reforms listed.")

    # Generate citation
    citation = format_gaceta_citation(
        norm_name=norm_name,
        gaceta_number=gaceta_number if gaceta_number else "[No disponible]",
        gaceta_type=g_type,
        date=publication_date if publication_date else "[Fecha no disponible]",
        status=status,
        last_reform=reform_entries[-1] if reform_entries else None
    )

    return NormVerification(
        norm_name=norm_name,
        norm_type=n_type,
        verification_date=datetime.now().isoformat(),
        status=status,
        original_publication=original_pub,
        reforms=reform_entries,
        current_text_source=current_source,
        notes=notes,
        citation=citation,
        warnings=warnings,
        keywords=keywords
    )


# ═══════════════════════════════════════════════════════════════════════════════
#                    COMPREHENSIVE VENEZUELAN LAWS DATABASE
#                              45+ Major Laws
# ═══════════════════════════════════════════════════════════════════════════════

KNOWN_NORMS = {
    # ═══════════════════════════════════════════════════════════════════════════
    #                         CONSTITUTIONAL LAW
    # ═══════════════════════════════════════════════════════════════════════════

    "constitucion": {
        "name": "Constitución de la República Bolivariana de Venezuela",
        "norm_type": "Constitución",
        "gaceta_number": "36.860",
        "gaceta_type": "Extraordinaria",
        "publication_date": "30-12-1999",
        "status": "Modificada",
        "reforms": [
            {
                "gaceta_number": "5.908",
                "gaceta_type": "Extraordinaria",
                "date": "19-02-2009",
                "description": "Enmienda No. 1 - Elimina límites a reelección",
                "action": "Enmienda"
            }
        ],
        "notes": "Texto fundamental del ordenamiento jurídico venezolano. Establece el Estado Social de Derecho y Justicia.",
        "keywords": ["constitución", "CRBV", "derechos humanos", "Estado Social", "1999"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         PROCEDURAL CODES
    # ═══════════════════════════════════════════════════════════════════════════

    "codigo_civil": {
        "name": "Código Civil de Venezuela",
        "norm_type": "Código",
        "gaceta_number": "2.990",
        "gaceta_type": "Extraordinaria",
        "publication_date": "26-07-1982",
        "status": "Vigente",
        "reforms": [],
        "notes": "Última reforma integral 1982. Regula personas, familia, bienes, obligaciones, contratos y sucesiones.",
        "keywords": ["código civil", "contratos", "obligaciones", "familia", "sucesiones", "propiedad"]
    },

    "codigo_comercio": {
        "name": "Código de Comercio",
        "norm_type": "Código",
        "gaceta_number": "475",
        "gaceta_type": "Extraordinaria",
        "publication_date": "21-12-1955",
        "status": "Vigente",
        "reforms": [],
        "notes": "Reformas parciales posteriores en materias específicas. Regula actos de comercio y sociedades mercantiles.",
        "keywords": ["código de comercio", "comerciante", "sociedades mercantiles", "títulos valores"]
    },

    "codigo_procedimiento_civil": {
        "name": "Código de Procedimiento Civil",
        "norm_type": "Código",
        "gaceta_number": "4.209",
        "gaceta_type": "Extraordinaria",
        "publication_date": "18-09-1990",
        "status": "Vigente",
        "reforms": [],
        "notes": "Rige los procedimientos civiles y mercantiles ante tribunales ordinarios.",
        "keywords": ["CPC", "procedimiento civil", "demanda", "contestación", "pruebas", "sentencia"]
    },

    "codigo_organico_procesal_penal": {
        "name": "Código Orgánico Procesal Penal",
        "norm_type": "Código",
        "gaceta_number": "6.644",
        "gaceta_type": "Extraordinaria",
        "publication_date": "17-09-2021",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "6.644",
                "gaceta_type": "Extraordinaria",
                "date": "17-09-2021",
                "description": "Reforma integral del COPP",
                "action": "Reforma"
            }
        ],
        "notes": "Sistema acusatorio. Establece derechos del imputado, investigación, juicio oral y recursos.",
        "keywords": ["COPP", "proceso penal", "imputado", "juicio oral", "Ministerio Público", "acusatorio"]
    },

    "codigo_penal": {
        "name": "Código Penal",
        "norm_type": "Código",
        "gaceta_number": "5.768",
        "gaceta_type": "Extraordinaria",
        "publication_date": "13-04-2005",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "5.768",
                "gaceta_type": "Extraordinaria",
                "date": "13-04-2005",
                "description": "Reforma parcial",
                "action": "Reforma"
            }
        ],
        "notes": "Tipifica delitos y establece penas. Modificaciones parciales en diversas materias.",
        "keywords": ["código penal", "delitos", "penas", "homicidio", "robo", "corrupción"]
    },

    "codigo_organico_tributario": {
        "name": "Código Orgánico Tributario",
        "norm_type": "Código",
        "gaceta_number": "6.507",
        "gaceta_type": "Extraordinaria",
        "publication_date": "29-01-2020",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "6.507",
                "gaceta_type": "Extraordinaria",
                "date": "29-01-2020",
                "description": "Reforma integral COT",
                "action": "Reforma"
            }
        ],
        "notes": "Marco general del sistema tributario. Procedimientos, sanciones, recursos.",
        "keywords": ["COT", "tributario", "impuestos", "SENIAT", "procedimientos tributarios", "sanciones"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         ORGANIC LAWS - ADMINISTRATIVE
    # ═══════════════════════════════════════════════════════════════════════════

    "lopa": {
        "name": "Ley Orgánica de Procedimientos Administrativos",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "2.818",
        "gaceta_type": "Extraordinaria",
        "publication_date": "01-07-1981",
        "status": "Vigente",
        "reforms": [],
        "notes": "LOPA. Rige procedimientos ante la Administración Pública. Actos administrativos, recursos.",
        "keywords": ["LOPA", "procedimiento administrativo", "actos administrativos", "recursos", "silencio administrativo"]
    },

    "loap": {
        "name": "Ley Orgánica de la Administración Pública",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "6.147",
        "gaceta_type": "Extraordinaria",
        "publication_date": "17-11-2014",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "6.147",
                "gaceta_type": "Extraordinaria",
                "date": "17-11-2014",
                "description": "Reforma de la LOAP",
                "action": "Reforma"
            }
        ],
        "notes": "Organización de la Administración Pública Nacional. Ministerios, entes descentralizados.",
        "keywords": ["LOAP", "administración pública", "ministerios", "entes", "organización"]
    },

    "ley_contrataciones_publicas": {
        "name": "Ley de Contrataciones Públicas",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.154",
        "gaceta_type": "Extraordinaria",
        "publication_date": "19-11-2014",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "6.154",
                "gaceta_type": "Extraordinaria",
                "date": "19-11-2014",
                "description": "Decreto-Ley de Contrataciones Públicas",
                "action": "Reforma"
            }
        ],
        "notes": "Regula contratación de bienes, obras y servicios por el Estado.",
        "keywords": ["contrataciones públicas", "licitación", "compras", "Estado", "procedimientos"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         ORGANIC LAWS - JUDICIAL
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_amparo": {
        "name": "Ley Orgánica de Amparo sobre Derechos y Garantías Constitucionales",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "34.060",
        "gaceta_type": "Ordinaria",
        "publication_date": "27-09-1988",
        "status": "Vigente",
        "reforms": [],
        "notes": "Modificada jurisprudencialmente por TSJ. Procedimiento de amparo constitucional.",
        "keywords": ["amparo", "derechos constitucionales", "tutela judicial", "procedimiento"]
    },

    "ley_jurisdiccion_contencioso_administrativa": {
        "name": "Ley Orgánica de la Jurisdicción Contencioso Administrativa",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "39.451",
        "gaceta_type": "Ordinaria",
        "publication_date": "22-06-2010",
        "status": "Vigente",
        "reforms": [],
        "notes": "Regula tribunales contencioso-administrativos. Competencia, procedimientos, medidas cautelares.",
        "keywords": ["contencioso administrativo", "nulidad", "demandas contra el Estado", "SPA"]
    },

    "ley_tsj": {
        "name": "Ley Orgánica del Tribunal Supremo de Justicia",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "39.522",
        "gaceta_type": "Ordinaria",
        "publication_date": "01-10-2010",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "39.522",
                "gaceta_type": "Ordinaria",
                "date": "01-10-2010",
                "description": "Reforma de la LOTSJ",
                "action": "Reforma"
            }
        ],
        "notes": "Organización del TSJ. Salas, competencias, magistrados.",
        "keywords": ["TSJ", "Tribunal Supremo", "Salas", "magistrados", "competencias"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         LABOR AND SOCIAL SECURITY
    # ═══════════════════════════════════════════════════════════════════════════

    "lottt": {
        "name": "Ley Orgánica del Trabajo, los Trabajadores y las Trabajadoras",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "6.076",
        "gaceta_type": "Extraordinaria",
        "publication_date": "07-05-2012",
        "status": "Vigente",
        "reforms": [],
        "notes": "LOTTT. Derechos laborales, jornada, salario, prestaciones, estabilidad, inamovilidad.",
        "keywords": ["LOTTT", "trabajo", "laboral", "prestaciones", "despido", "salario", "trabajadores"]
    },

    "ley_procesal_trabajo": {
        "name": "Ley Orgánica Procesal del Trabajo",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "37.504",
        "gaceta_type": "Ordinaria",
        "publication_date": "13-08-2002",
        "status": "Vigente",
        "reforms": [],
        "notes": "Procedimiento laboral oral. Demanda, audiencias, sentencia.",
        "keywords": ["procedimiento laboral", "juicio oral", "demanda laboral", "audiencia"]
    },

    "lopcymat": {
        "name": "Ley Orgánica de Prevención, Condiciones y Medio Ambiente de Trabajo",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "38.236",
        "gaceta_type": "Ordinaria",
        "publication_date": "26-07-2005",
        "status": "Vigente",
        "reforms": [],
        "notes": "LOPCYMAT. Seguridad y salud ocupacional. INPSASEL. Accidentes de trabajo.",
        "keywords": ["LOPCYMAT", "seguridad laboral", "INPSASEL", "accidentes", "enfermedad ocupacional"]
    },

    "ley_seguro_social": {
        "name": "Ley del Seguro Social",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "5.976",
        "gaceta_type": "Extraordinaria",
        "publication_date": "24-05-2010",
        "status": "Vigente",
        "reforms": [],
        "notes": "IVSS. Pensiones, incapacidad, maternidad, enfermedad.",
        "keywords": ["seguro social", "IVSS", "pensiones", "jubilación", "cotizaciones"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         HYDROCARBONS AND ENERGY
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_hidrocarburos": {
        "name": "Ley Orgánica de Hidrocarburos",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "38.493",
        "gaceta_type": "Ordinaria",
        "publication_date": "04-08-2006",
        "status": "Vigente",
        "reforms": [],
        "notes": "LOH. Regula actividades de hidrocarburos líquidos. Empresas mixtas, regalías, fiscalización.",
        "keywords": ["LOH", "hidrocarburos", "petróleo", "PDVSA", "empresas mixtas", "regalías"]
    },

    "ley_hidrocarburos_gaseosos": {
        "name": "Ley Orgánica de Hidrocarburos Gaseosos",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "36.793",
        "gaceta_type": "Ordinaria",
        "publication_date": "23-09-1999",
        "status": "Vigente",
        "reforms": [],
        "notes": "Regula gas natural no asociado. Licencias, participación privada.",
        "keywords": ["gas natural", "hidrocarburos gaseosos", "licencias", "GNL"]
    },

    "ley_energia_electrica": {
        "name": "Ley Orgánica del Sistema y Servicio Eléctrico",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "39.573",
        "gaceta_type": "Ordinaria",
        "publication_date": "14-12-2010",
        "status": "Vigente",
        "reforms": [],
        "notes": "Sistema eléctrico nacional. CORPOELEC. Generación, transmisión, distribución.",
        "keywords": ["electricidad", "CORPOELEC", "servicio eléctrico", "generación"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         FINANCIAL AND BANKING
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_bancos": {
        "name": "Ley de Instituciones del Sector Bancario",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.154",
        "gaceta_type": "Extraordinaria",
        "publication_date": "19-11-2014",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "6.154",
                "gaceta_type": "Extraordinaria",
                "date": "19-11-2014",
                "description": "Decreto-Ley reforma",
                "action": "Reforma"
            }
        ],
        "notes": "Regula bancos e instituciones financieras. SUDEBAN. Operaciones bancarias.",
        "keywords": ["bancos", "SUDEBAN", "instituciones financieras", "operaciones bancarias"]
    },

    "ley_bcv": {
        "name": "Ley del Banco Central de Venezuela",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.155",
        "gaceta_type": "Extraordinaria",
        "publication_date": "19-11-2014",
        "status": "Vigente",
        "reforms": [],
        "notes": "BCV. Política monetaria, reservas internacionales, emisión de moneda.",
        "keywords": ["BCV", "Banco Central", "política monetaria", "bolívar", "reservas"]
    },

    "ley_mercado_valores": {
        "name": "Ley de Mercado de Valores",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.211",
        "gaceta_type": "Extraordinaria",
        "publication_date": "30-12-2015",
        "status": "Vigente",
        "reforms": [],
        "notes": "Superintendencia Nacional de Valores. Oferta pública, bolsa, emisores.",
        "keywords": ["mercado de valores", "bolsa", "valores", "acciones", "emisiones"]
    },

    "ley_seguros": {
        "name": "Ley de la Actividad Aseguradora",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.220",
        "gaceta_type": "Extraordinaria",
        "publication_date": "15-03-2016",
        "status": "Vigente",
        "reforms": [],
        "notes": "SUDEASEG. Empresas de seguros, reaseguros, corredores.",
        "keywords": ["seguros", "SUDEASEG", "pólizas", "aseguradoras", "reaseguro"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         TAX LAWS
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_islr": {
        "name": "Ley de Impuesto Sobre la Renta",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.210",
        "gaceta_type": "Extraordinaria",
        "publication_date": "30-12-2015",
        "status": "Vigente",
        "reforms": [],
        "notes": "ISLR. Impuesto sobre la renta de personas naturales y jurídicas.",
        "keywords": ["ISLR", "impuesto sobre la renta", "declaración", "retenciones"]
    },

    "ley_iva": {
        "name": "Ley de Impuesto al Valor Agregado",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.507",
        "gaceta_type": "Extraordinaria",
        "publication_date": "29-01-2020",
        "status": "Vigente",
        "reforms": [],
        "notes": "IVA. Impuesto al consumo. Alícuota general y reducida.",
        "keywords": ["IVA", "impuesto al valor agregado", "facturación", "crédito fiscal"]
    },

    "ley_igtf": {
        "name": "Ley de Impuesto a las Grandes Transacciones Financieras",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.687",
        "gaceta_type": "Extraordinaria",
        "publication_date": "25-02-2022",
        "status": "Vigente",
        "reforms": [],
        "notes": "IGTF. Impuesto a transacciones en divisas y criptoactivos.",
        "keywords": ["IGTF", "transacciones financieras", "divisas", "criptoactivos"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         PROPERTY AND HOUSING
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_arrendamiento_vivienda": {
        "name": "Ley para la Regularización y Control de los Arrendamientos de Vivienda",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.053",
        "gaceta_type": "Extraordinaria",
        "publication_date": "12-11-2011",
        "status": "Vigente",
        "reforms": [],
        "notes": "Arrendamiento de viviendas. SUNAVI. Procedimientos especiales, desalojo.",
        "keywords": ["arrendamiento", "vivienda", "SUNAVI", "desalojo", "alquiler"]
    },

    "ley_expropiacion": {
        "name": "Ley de Expropiación por Causa de Utilidad Pública o Social",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "37.475",
        "gaceta_type": "Ordinaria",
        "publication_date": "01-07-2002",
        "status": "Vigente",
        "reforms": [],
        "notes": "Procedimiento expropiatorio. Justiprecio, utilidad pública.",
        "keywords": ["expropiación", "utilidad pública", "justiprecio", "indemnización"]
    },

    "ley_registro_notaria": {
        "name": "Ley de Registros y del Notariado",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "6.668",
        "gaceta_type": "Extraordinaria",
        "publication_date": "16-12-2021",
        "status": "Vigente",
        "reforms": [],
        "notes": "SAREN. Registro inmobiliario, mercantil. Notarías públicas.",
        "keywords": ["registro", "notaría", "SAREN", "documentos públicos", "protocolización"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         CORPORATE AND COMMERCIAL
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_registros_mercantiles": {
        "name": "Ley de Registro Público y del Notariado (Mercantil)",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "6.668",
        "gaceta_type": "Extraordinaria",
        "publication_date": "16-12-2021",
        "status": "Vigente",
        "reforms": [],
        "notes": "Inscripción de sociedades mercantiles. Actas de asamblea, transformaciones.",
        "keywords": ["registro mercantil", "sociedades", "constitución", "actas"]
    },

    "ley_propiedad_industrial": {
        "name": "Ley de Propiedad Industrial",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "25.227",
        "gaceta_type": "Ordinaria",
        "publication_date": "10-12-1955",
        "status": "Vigente",
        "reforms": [],
        "notes": "SAPI. Patentes, marcas, denominaciones de origen.",
        "keywords": ["propiedad industrial", "SAPI", "patentes", "marcas", "invenciones"]
    },

    "ley_derecho_autor": {
        "name": "Ley sobre el Derecho de Autor",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "4.638",
        "gaceta_type": "Extraordinaria",
        "publication_date": "01-10-1993",
        "status": "Vigente",
        "reforms": [],
        "notes": "SENAPI/SAPI. Obras literarias, artísticas, software.",
        "keywords": ["derecho de autor", "copyright", "obras", "software", "creaciones"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         ENVIRONMENTAL
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_ambiente": {
        "name": "Ley Orgánica del Ambiente",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "5.833",
        "gaceta_type": "Extraordinaria",
        "publication_date": "22-12-2006",
        "status": "Vigente",
        "reforms": [],
        "notes": "Gestión del ambiente. Estudios de impacto ambiental. Sanciones.",
        "keywords": ["ambiente", "impacto ambiental", "conservación", "contaminación"]
    },

    "ley_aguas": {
        "name": "Ley de Aguas",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "38.595",
        "gaceta_type": "Ordinaria",
        "publication_date": "02-01-2007",
        "status": "Vigente",
        "reforms": [],
        "notes": "Gestión integral del agua. Cuencas, concesiones, uso.",
        "keywords": ["aguas", "recursos hídricos", "concesiones", "cuencas"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         CRIMINAL AND SPECIAL
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_corrupcion": {
        "name": "Ley Contra la Corrupción",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "6.155",
        "gaceta_type": "Extraordinaria",
        "publication_date": "19-11-2014",
        "status": "Vigente",
        "reforms": [],
        "notes": "Delitos de corrupción. Funcionarios públicos. Enriquecimiento ilícito.",
        "keywords": ["corrupción", "funcionarios", "peculado", "soborno", "enriquecimiento"]
    },

    "ley_delincuencia_organizada": {
        "name": "Ley Orgánica Contra la Delincuencia Organizada y Financiamiento al Terrorismo",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "39.912",
        "gaceta_type": "Ordinaria",
        "publication_date": "30-04-2012",
        "status": "Vigente",
        "reforms": [],
        "notes": "Delincuencia organizada, lavado de dinero, terrorismo.",
        "keywords": ["delincuencia organizada", "lavado de dinero", "terrorismo", "legitimación"]
    },

    "ley_drogas": {
        "name": "Ley Orgánica de Drogas",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "39.546",
        "gaceta_type": "Ordinaria",
        "publication_date": "05-11-2010",
        "status": "Vigente",
        "reforms": [],
        "notes": "Tráfico de drogas. ONA. Prevención, tratamiento, sanciones.",
        "keywords": ["drogas", "narcotráfico", "ONA", "estupefacientes"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         TELECOMMUNICATIONS AND TECHNOLOGY
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_telecomunicaciones": {
        "name": "Ley Orgánica de Telecomunicaciones",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "39.610",
        "gaceta_type": "Ordinaria",
        "publication_date": "07-02-2011",
        "status": "Vigente",
        "reforms": [],
        "notes": "CONATEL. Concesiones, espectro radioeléctrico, servicios.",
        "keywords": ["telecomunicaciones", "CONATEL", "espectro", "internet", "telefonía"]
    },

    "ley_infogobierno": {
        "name": "Ley de Infogobierno",
        "norm_type": "Ley Ordinaria",
        "gaceta_number": "40.274",
        "gaceta_type": "Ordinaria",
        "publication_date": "17-10-2013",
        "status": "Vigente",
        "reforms": [],
        "notes": "Gobierno electrónico. Software libre. Interoperabilidad.",
        "keywords": ["infogobierno", "gobierno electrónico", "software libre", "datos"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         CONSUMER AND COMMERCE
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_precios_justos": {
        "name": "Ley Orgánica de Precios Justos",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "40.340",
        "gaceta_type": "Ordinaria",
        "publication_date": "23-01-2014",
        "status": "Vigente",
        "reforms": [],
        "notes": "SUNDDE. Control de precios, márgenes de ganancia, especulación.",
        "keywords": ["precios justos", "SUNDDE", "control de precios", "especulación"]
    },

    "ley_defensa_consumidor": {
        "name": "Ley para la Defensa de las Personas en el Acceso a los Bienes y Servicios",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "39.358",
        "gaceta_type": "Ordinaria",
        "publication_date": "01-02-2010",
        "status": "Vigente",
        "reforms": [],
        "notes": "INDEPABIS/SUNDDE. Derechos del consumidor, garantías.",
        "keywords": ["consumidor", "INDEPABIS", "garantías", "derechos", "reclamos"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         ELECTORAL
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_procesos_electorales": {
        "name": "Ley Orgánica de Procesos Electorales",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "5.928",
        "gaceta_type": "Extraordinaria",
        "publication_date": "12-08-2009",
        "status": "Vigente",
        "reforms": [],
        "notes": "CNE. Elecciones, votación, escrutinio, proclamación.",
        "keywords": ["elecciones", "CNE", "votación", "candidatos", "partidos"]
    },

    "ley_poder_electoral": {
        "name": "Ley Orgánica del Poder Electoral",
        "norm_type": "Ley Orgánica",
        "gaceta_number": "37.573",
        "gaceta_type": "Ordinaria",
        "publication_date": "19-11-2002",
        "status": "Vigente",
        "reforms": [],
        "notes": "Organización del CNE. Rectores, Junta Nacional Electoral.",
        "keywords": ["poder electoral", "CNE", "rectores", "organización electoral"]
    },

    # ═══════════════════════════════════════════════════════════════════════════
    #                         FOREIGN INVESTMENT AND TRADE
    # ═══════════════════════════════════════════════════════════════════════════

    "ley_inversiones_extranjeras": {
        "name": "Ley de Promoción y Protección de Inversiones",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.152",
        "gaceta_type": "Extraordinaria",
        "publication_date": "18-11-2014",
        "status": "Vigente",
        "reforms": [],
        "notes": "Inversión extranjera. Tratamiento, garantías, registro.",
        "keywords": ["inversiones", "inversión extranjera", "garantías", "registro"]
    },

    "ley_ilicitos_cambiarios": {
        "name": "Ley del Régimen Cambiario y sus Ilícitos",
        "norm_type": "Decreto con Rango, Valor y Fuerza de Ley",
        "gaceta_number": "6.405",
        "gaceta_type": "Extraordinaria",
        "publication_date": "07-09-2018",
        "status": "Vigente",
        "reforms": [],
        "notes": "Control cambiario. Ilícitos, sanciones.",
        "keywords": ["régimen cambiario", "divisas", "ilícitos cambiarios", "control"]
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
#                         SEARCH AND LOOKUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def lookup_known_norm(search_term: str) -> Optional[NormVerification]:
    """Look up a norm in the known norms database."""

    search_lower = search_term.lower()

    for key, data in KNOWN_NORMS.items():
        # Check key, name, and keywords
        if (key in search_lower or
            search_lower in data["name"].lower() or
            any(search_lower in kw.lower() for kw in data.get("keywords", []))):
            return verify_norm(
                norm_name=data["name"],
                norm_type=data.get("norm_type", "Ley Ordinaria"),
                gaceta_number=data["gaceta_number"],
                gaceta_type=data["gaceta_type"],
                publication_date=data["publication_date"],
                known_status=data["status"],
                reforms=data.get("reforms", []),
                notes=data.get("notes", ""),
                keywords=data.get("keywords", [])
            )

    return None


def search_norms(query: str) -> List[dict]:
    """Search for norms matching the query."""
    results = []
    query_lower = query.lower()

    for key, data in KNOWN_NORMS.items():
        score = 0

        # Check various fields
        if query_lower in key:
            score += 10
        if query_lower in data["name"].lower():
            score += 8
        if any(query_lower in kw.lower() for kw in data.get("keywords", [])):
            score += 5
        if query_lower in data.get("notes", "").lower():
            score += 2

        if score > 0:
            results.append({
                "key": key,
                "name": data["name"],
                "type": data.get("norm_type", "Ley"),
                "status": data["status"],
                "gaceta": f"{data['gaceta_type']} No. {data['gaceta_number']}",
                "date": data["publication_date"],
                "score": score
            })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def get_norms_by_type(norm_type: str) -> List[dict]:
    """Get all norms of a specific type."""
    results = []
    type_lower = norm_type.lower()

    for key, data in KNOWN_NORMS.items():
        if type_lower in data.get("norm_type", "").lower():
            results.append({
                "key": key,
                "name": data["name"],
                "type": data.get("norm_type", "Ley"),
                "status": data["status"],
                "gaceta": f"{data['gaceta_type']} No. {data['gaceta_number']}",
                "date": data["publication_date"]
            })

    return results


def get_statistics() -> dict:
    """Get database statistics."""
    stats = {
        "total_norms": len(KNOWN_NORMS),
        "by_type": {},
        "by_status": {},
        "with_reforms": 0
    }

    for key, data in KNOWN_NORMS.items():
        # Count by type
        norm_type = data.get("norm_type", "Ley Ordinaria")
        stats["by_type"][norm_type] = stats["by_type"].get(norm_type, 0) + 1

        # Count by status
        status = data["status"]
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        # Count with reforms
        if data.get("reforms"):
            stats["with_reforms"] += 1

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main function for CLI usage."""

    if len(sys.argv) < 2:
        stats = get_statistics()
        print("Venezuela Super Lawyer - Gaceta Oficial Verification")
        print(f"\nDatabase: {stats['total_norms']} norms")
        print("\nNorms by Type:")
        for norm_type, count in stats["by_type"].items():
            print(f"  - {norm_type}: {count}")
        print(f"\nNorms with recorded reforms: {stats['with_reforms']}")
        print("\nUsage:")
        print("  python3 gaceta_verify.py <norm_name>")
        print("  python3 gaceta_verify.py --search <query>")
        print("  python3 gaceta_verify.py --type 'Ley Orgánica'")
        print("  python3 gaceta_verify.py --json <input_file.json>")
        print("  python3 gaceta_verify.py --list")
        print("  python3 gaceta_verify.py --stats")
        print("\nExamples:")
        print("  python3 gaceta_verify.py 'Constitución'")
        print("  python3 gaceta_verify.py 'LOTTT'")
        print("  python3 gaceta_verify.py --search 'hidrocarburos'")
        print("  python3 gaceta_verify.py --type 'Código'")
        sys.exit(0)

    if sys.argv[1] == "--list":
        print("Known Norms in Database:\n")
        for key, data in sorted(KNOWN_NORMS.items()):
            print(f"  {key}:")
            print(f"    {data['name']}")
            print(f"    Type: {data.get('norm_type', 'Ley')}")
            print(f"    Gaceta: {data['gaceta_type']} No. {data['gaceta_number']}, {data['publication_date']}")
            print(f"    Status: {data['status']}")
            print()
        sys.exit(0)

    if sys.argv[1] == "--stats":
        stats = get_statistics()
        print(json.dumps(stats, indent=2))
        sys.exit(0)

    if sys.argv[1] == "--search" and len(sys.argv) > 2:
        query = sys.argv[2]
        results = search_norms(query)
        if results:
            print(f"\nSearch Results for '{query}':\n")
            for r in results[:10]:
                print(f"  {r['name']}")
                print(f"    Key: {r['key']}")
                print(f"    Type: {r['type']}")
                print(f"    Gaceta: {r['gaceta']}, {r['date']}")
                print(f"    Status: {r['status']}")
                print()
        else:
            print(f"No results found for '{query}'")
        sys.exit(0)

    if sys.argv[1] == "--type" and len(sys.argv) > 2:
        norm_type = sys.argv[2]
        results = get_norms_by_type(norm_type)
        if results:
            print(f"\nNorms of type '{norm_type}':\n")
            for r in results:
                print(f"  {r['name']}")
                print(f"    Gaceta: {r['gaceta']}, {r['date']}")
                print(f"    Status: {r['status']}")
                print()
        else:
            print(f"No norms found of type '{norm_type}'")
        sys.exit(0)

    if sys.argv[1] == "--json" and len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            params = json.load(f)
        verification = verify_norm(**params)
        print(create_verification_report(verification))
        sys.exit(0)

    # Try to look up in known norms
    search_term = sys.argv[1]
    verification = lookup_known_norm(search_term)

    if not verification:
        # Try search
        results = search_norms(search_term)
        if results:
            print(f"\nDid you mean one of these?\n")
            for r in results[:5]:
                print(f"  - {r['key']}: {r['name']}")
            print(f"\nTry: python3 gaceta_verify.py '{results[0]['key']}'")
        else:
            # Create a basic verification request
            verification = verify_norm(
                norm_name=search_term,
                notes="Norm not found in local database. Manual Gaceta verification required."
            )
            print(create_verification_report(verification))
    else:
        print(create_verification_report(verification))


if __name__ == "__main__":
    main()
