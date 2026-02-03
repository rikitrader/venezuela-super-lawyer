#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Report Manager
Manages automatic generation and updating of legal research reports in Markdown format.
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Default reports directory
DEFAULT_REPORTS_DIR = "reportes_legales"


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
    """Return the ASCII art of Venezuela's Coat of Arms."""
    return """
            ╔══════════════════════════════════════════════════════════════╗
            ║         REPÚBLICA BOLIVARIANA DE VENEZUELA                   ║
            ╠══════════════════════════════════════════════════════════════╣
            ║                                                              ║
            ║                        .:::::::.                             ║
            ║                    ╔═══════════════╗                         ║
            ║               🌿   ║ ▓▓▓ ║ ### ║   ║   🌴                    ║
            ║              OLIVO ║ ROJO║AMARI║   ║ PALMA                   ║
            ║                    ╠═════╩═════════╣                         ║
            ║                    ║     AZUL      ║                         ║
            ║                    ║   ~~ 🐴 ~~    ║                         ║
            ║                    ║   CABALLO     ║                         ║
            ║                    ╚═══════════════╝                         ║
            ║          ══════════════════════════════                      ║
            ║           19 ABR 1810 • INDEPENDENCIA                        ║
            ║           20 FEB 1859 • FEDERACIÓN                           ║
            ╚══════════════════════════════════════════════════════════════╝
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


def main():
    """Main function for CLI usage."""

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
