#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Case Initialization Script
Initializes the standardized case folder structure for legal case management.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Directory configuration
CASES_DIR = Path(__file__).parent.parent / "cases"
CASE_SUBDIRS = ["DRAFTS", "documentos", "evidencia", "investigacion", "reportes"]


def generate_case_header(case_name: str) -> str:
    """Generate a header for case documentation."""
    now = datetime.now()
    return f"""# CASO: {case_name}

═══════════════════════════════════════════════════════════════════════════════
                    VENEZUELA SUPER LAWYER - CASO LEGAL
═══════════════════════════════════════════════════════════════════════════════

**Caso:** {case_name}
**Creado:** {now.strftime("%Y-%m-%d %H:%M:%S")}
**Sistema:** Venezuela Super Lawyer v2.0

═══════════════════════════════════════════════════════════════════════════════
"""


def get_case_template(case_name: str) -> str:
    """Get the case template content."""
    header = generate_case_header(case_name)
    return header + """
## Resumen Ejecutivo

*Pendiente de análisis*

## Hechos del Caso

*Pendiente de verificación*

## Marco Legal Aplicable

*Pendiente de investigación*

## Análisis Constitucional

*Pendiente de evaluación*

## Estrategia Legal

*Pendiente de desarrollo*

## Próximos Pasos

- [ ] Completar intake del caso
- [ ] Recopilar documentos
- [ ] Análisis constitucional
- [ ] Investigación jurisprudencial
- [ ] Desarrollo de estrategia

"""


def create_case_structure(case_number: str, client_name: str = None, base_path: str = None):
    """Create the standardized case folder structure."""

    if base_path is None:
        base_path = os.getcwd()

    case_dir = Path(base_path) / "cases" / case_number

    if case_dir.exists():
        print(f"Error: Case directory already exists: {case_dir}")
        sys.exit(1)

    # Create main case directory
    case_dir.mkdir(parents=True)

    # Create DRAFTS subdirectory
    (case_dir / "DRAFTS").mkdir()

    # Create MANIFEST.md
    manifest_content = f"""# Case Manifest: {case_number}

## Case Information
- **Case Number:** {case_number}
- **Client:** {client_name}
- **Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Status:** Active

## Case Index

### Core Documents
- [INTAKE.json](./INTAKE.json) - Structured intake data
- [FACTS.md](./FACTS.md) - Verified facts
- [TIMELINE.md](./TIMELINE.md) - Chronological events

### Analysis Documents
- [BRAINSTORM.md](./BRAINSTORM.md) - Legal issues brainstorm
- [QUERY_EXPANSION.md](./QUERY_EXPANSION.md) - Search queries
- [RESEARCH_PLAN.md](./RESEARCH_PLAN.md) - Research strategy

### Research Results
- [RETRIEVAL_LOG.md](./RETRIEVAL_LOG.md) - Search results log
- [GOVERNING_LAW.md](./GOVERNING_LAW.md) - Applicable law
- [TSJ_JURISPRUDENCE.md](./TSJ_JURISPRUDENCE.md) - Relevant jurisprudence
- [GACETA_TIMELINE.md](./GACETA_TIMELINE.md) - Gaceta Oficial history

### Strategy Documents
- [CONSTITUTIONAL_TESTS.md](./CONSTITUTIONAL_TESTS.md) - Constitutionality analysis
- [RISK_ANALYSIS.md](./RISK_ANALYSIS.md) - Risk assessment
- [STRATEGY_GAMEPLAN.md](./STRATEGY_GAMEPLAN.md) - Legal strategy

### Drafts
- [DRAFTS/](./DRAFTS/) - Legal document drafts

## Change Log
See [UPDATES.log](./UPDATES.log) for detailed change history.
"""
    (case_dir / "MANIFEST.md").write_text(manifest_content)

    # Create INTAKE.json
    intake_data = {
        "case_number": case_number,
        "client_name": client_name,
        "created_at": datetime.now().isoformat(),
        "case_type": "",
        "jurisdiction": "Venezuela",
        "court": "",
        "opposing_party": "",
        "matter_description": "",
        "key_dates": [],
        "documents_received": [],
        "constitutional_issues": [],
        "hydrocarbons_related": False,
        "urgency": "normal",
        "notes": ""
    }
    (case_dir / "INTAKE.json").write_text(json.dumps(intake_data, indent=2, ensure_ascii=False))

    # Create placeholder files
    files_to_create = [
        ("BRAINSTORM.md", f"# Brainstorm: {case_number}\n\n## Legal Issues Identified\n\n*Pending analysis*\n"),
        ("QUERY_EXPANSION.md", f"# Query Expansion: {case_number}\n\n## Search Queries\n\n*Pending generation*\n"),
        ("RESEARCH_PLAN.md", f"# Research Plan: {case_number}\n\n## Research Strategy\n\n*Pending development*\n"),
        ("RETRIEVAL_LOG.md", f"# Retrieval Log: {case_number}\n\n## Search Results\n\n| Date | Source | Query | Results | Status |\n|------|--------|-------|---------|--------|\n"),
        ("FACTS.md", f"# Facts: {case_number}\n\n## Verified Facts\n\n*Pending verification*\n\n## Disputed Facts\n\n*Pending analysis*\n"),
        ("TIMELINE.md", f"# Timeline: {case_number}\n\n## Chronological Events\n\n| Date | Event | Source | Significance |\n|------|-------|--------|-------------|\n"),
        ("GOVERNING_LAW.md", f"# Governing Law: {case_number}\n\n## Constitutional Provisions\n\n*Pending research*\n\n## Organic Laws\n\n*Pending research*\n\n## Other Applicable Law\n\n*Pending research*\n"),
        ("TSJ_JURISPRUDENCE.md", f"# TSJ Jurisprudence: {case_number}\n\n## Relevant Cases\n\n*Pending research*\n"),
        ("CONSTITUTIONAL_TESTS.md", f"# Constitutional Tests: {case_number}\n\n## Test Results\n\n*Pending analysis*\n"),
        ("RISK_ANALYSIS.md", f"# Risk Analysis: {case_number}\n\n## Risk Assessment\n\n*Pending analysis*\n"),
        ("STRATEGY_GAMEPLAN.md", f"# Strategy Gameplan: {case_number}\n\n## Recommended Strategy\n\n*Pending development*\n"),
        ("GACETA_TIMELINE.md", f"# Gaceta Oficial Timeline: {case_number}\n\n## Applicable Norms History\n\n| Norm | Gaceta No. | Date | Status | Notes |\n|------|------------|------|--------|-------|\n"),
    ]

    for filename, content in files_to_create:
        (case_dir / filename).write_text(content)

    # Create UPDATES.log
    log_content = f"""# Updates Log: {case_number}

## Change History

### {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Case initialized
- Client: {client_name}
- Created by: Venezuela Super Lawyer

---
"""
    (case_dir / "UPDATES.log").write_text(log_content)

    print(f"✅ Case initialized successfully: {case_dir}")
    print(f"\nCase Structure:")
    print(f"  {case_dir}/")
    print(f"  ├── MANIFEST.md")
    print(f"  ├── INTAKE.json")
    print(f"  ├── BRAINSTORM.md")
    print(f"  ├── QUERY_EXPANSION.md")
    print(f"  ├── RESEARCH_PLAN.md")
    print(f"  ├── RETRIEVAL_LOG.md")
    print(f"  ├── FACTS.md")
    print(f"  ├── TIMELINE.md")
    print(f"  ├── GOVERNING_LAW.md")
    print(f"  ├── TSJ_JURISPRUDENCE.md")
    print(f"  ├── CONSTITUTIONAL_TESTS.md")
    print(f"  ├── RISK_ANALYSIS.md")
    print(f"  ├── STRATEGY_GAMEPLAN.md")
    print(f"  ├── GACETA_TIMELINE.md")
    print(f"  ├── UPDATES.log")
    print(f"  └── DRAFTS/")

    return str(case_dir)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog="init_case.py",
        description="Venezuela Super Lawyer - Case Initialization",
        epilog="Creates standardized legal case folder structure"
    )
    parser.add_argument(
        "case_number",
        help="Case number/identifier (e.g., 2024-001)"
    )
    parser.add_argument(
        "client_name",
        nargs="?",
        default="CONFIDENCIAL",
        help="Client name (default: CONFIDENCIAL)"
    )
    parser.add_argument(
        "--path", "-p",
        dest="base_path",
        help="Base path for cases directory"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    create_case_structure(args.case_number, args.client_name, args.base_path)


if __name__ == "__main__":
    main()
