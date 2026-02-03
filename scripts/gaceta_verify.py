#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Gaceta Oficial Verification Script
Verifies norm currency and generates Gaceta Oficial citations.
"""

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
    verification_date: str
    status: NormStatus
    original_publication: Optional[GacetaEntry]
    reforms: List[GacetaEntry]
    current_text_source: Optional[GacetaEntry]
    notes: str
    citation: str
    warnings: List[str]


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

    if verification.warnings:
        md += "\n---\n\n## ⚠️ Warnings\n\n"
        for warning in verification.warnings:
            md += f"- {warning}\n"

    if verification.notes:
        md += f"\n---\n\n## Notes\n\n{verification.notes}\n"

    return md


def verify_norm(
    norm_name: str,
    gaceta_number: str = "",
    gaceta_type: str = "Ordinaria",
    publication_date: str = "",
    known_status: str = "Desconocido",
    reforms: List[dict] = None,
    notes: str = ""
) -> NormVerification:
    """Create a norm verification record."""

    reforms = reforms or []

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
        verification_date=datetime.now().isoformat(),
        status=status,
        original_publication=original_pub,
        reforms=reform_entries,
        current_text_source=current_source,
        notes=notes,
        citation=citation,
        warnings=warnings
    )


# Common Venezuelan laws database (sample - expand as needed)
KNOWN_NORMS = {
    "constitucion": {
        "name": "Constitución de la República Bolivariana de Venezuela",
        "gaceta_number": "36.860",
        "gaceta_type": "Extraordinaria",
        "publication_date": "30-12-1999",
        "status": "Vigente",
        "reforms": [
            {
                "gaceta_number": "5.908",
                "gaceta_type": "Extraordinaria",
                "date": "19-02-2009",
                "description": "Enmienda No. 1",
                "action": "Enmienda"
            }
        ],
        "notes": "Texto fundamental. Enmienda de 2009 eliminó límites a reelección."
    },
    "codigo_civil": {
        "name": "Código Civil de Venezuela",
        "gaceta_number": "2.990",
        "gaceta_type": "Extraordinaria",
        "publication_date": "26-07-1982",
        "status": "Vigente",
        "reforms": [],
        "notes": "Última reforma integral 1982."
    },
    "codigo_comercio": {
        "name": "Código de Comercio",
        "gaceta_number": "475",
        "gaceta_type": "Extraordinaria",
        "publication_date": "21-12-1955",
        "status": "Vigente",
        "reforms": [],
        "notes": "Reformas parciales posteriores en materias específicas."
    },
    "ley_hidrocarburos": {
        "name": "Ley Orgánica de Hidrocarburos",
        "gaceta_number": "38.493",
        "gaceta_type": "Ordinaria",
        "publication_date": "04-08-2006",
        "status": "Vigente",
        "reforms": [],
        "notes": "Regula actividades de hidrocarburos líquidos."
    },
    "ley_amparo": {
        "name": "Ley Orgánica de Amparo sobre Derechos y Garantías Constitucionales",
        "gaceta_number": "34.060",
        "gaceta_type": "Ordinaria",
        "publication_date": "27-09-1988",
        "status": "Vigente",
        "reforms": [],
        "notes": "Modificada jurisprudencialmente por TSJ."
    },
    "lopa": {
        "name": "Ley Orgánica de Procedimientos Administrativos",
        "gaceta_number": "2.818",
        "gaceta_type": "Extraordinaria",
        "publication_date": "01-07-1981",
        "status": "Vigente",
        "reforms": [],
        "notes": "LOPA. Rige procedimientos ante la Administración Pública."
    }
}


def lookup_known_norm(search_term: str) -> Optional[NormVerification]:
    """Look up a norm in the known norms database."""

    search_lower = search_term.lower()

    for key, data in KNOWN_NORMS.items():
        if key in search_lower or search_lower in data["name"].lower():
            return verify_norm(
                norm_name=data["name"],
                gaceta_number=data["gaceta_number"],
                gaceta_type=data["gaceta_type"],
                publication_date=data["publication_date"],
                known_status=data["status"],
                reforms=data.get("reforms", []),
                notes=data.get("notes", "")
            )

    return None


def main():
    """Main function for CLI usage."""

    if len(sys.argv) < 2:
        print("Venezuela Super Lawyer - Gaceta Oficial Verification")
        print("\nUsage:")
        print("  python3 gaceta_verify.py <norm_name>")
        print("  python3 gaceta_verify.py --json <input_file.json>")
        print("  python3 gaceta_verify.py --list")
        print("\nExamples:")
        print("  python3 gaceta_verify.py 'Constitución'")
        print("  python3 gaceta_verify.py 'Código Civil'")
        print("  python3 gaceta_verify.py 'Ley Orgánica de Hidrocarburos'")
        sys.exit(0)

    if sys.argv[1] == "--list":
        print("Known Norms in Database:\n")
        for key, data in KNOWN_NORMS.items():
            print(f"  - {data['name']}")
            print(f"    Key: {key}")
            print(f"    Gaceta: {data['gaceta_type']} No. {data['gaceta_number']}, {data['publication_date']}")
            print(f"    Status: {data['status']}")
            print()
        sys.exit(0)

    if sys.argv[1] == "--json" and len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            params = json.load(f)
        verification = verify_norm(**params)
    else:
        # Try to look up in known norms
        search_term = sys.argv[1]
        verification = lookup_known_norm(search_term)

        if not verification:
            # Create a basic verification request
            verification = verify_norm(
                norm_name=search_term,
                notes="Norm not found in local database. Manual Gaceta verification required."
            )

    # Output markdown report
    print(create_verification_report(verification))


if __name__ == "__main__":
    main()
