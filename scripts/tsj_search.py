#!/usr/bin/env python3
"""
Venezuela Super Lawyer - TSJ Jurisprudence Search Script
Search and analyze Tribunal Supremo de Justicia jurisprudence.
"""

import sys
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class SalaTSJ(Enum):
    CONSTITUCIONAL = "Sala Constitucional"
    POLITICO_ADMINISTRATIVA = "Sala Político-Administrativa"
    CASACION_CIVIL = "Sala de Casación Civil"
    CASACION_PENAL = "Sala de Casación Penal"
    CASACION_SOCIAL = "Sala de Casación Social"
    ELECTORAL = "Sala Electoral"
    PLENA = "Sala Plena"


class TipoDecision(Enum):
    SENTENCIA = "Sentencia"
    AUTO = "Auto"
    ACLARATORIA = "Aclaratoria"
    AMPLIACION = "Ampliación"


@dataclass
class CasoTSJ:
    sala: SalaTSJ
    numero_expediente: str
    numero_sentencia: str
    fecha: str
    tipo: TipoDecision
    ponente: str
    partes: str
    materia: str
    resumen: str
    ratio_decidendi: str
    articulos_crbv: List[str]
    precedentes_citados: List[str]
    vinculante: bool
    url: str


@dataclass
class ResultadoBusqueda:
    query: str
    fecha_busqueda: str
    total_resultados: int
    casos: List[CasoTSJ]
    sugerencias: List[str]


# Sample jurisprudence database (expand with real cases)
JURISPRUDENCIA_SAMPLE = [
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="00-1529",
        numero_sentencia="1",
        fecha="20-01-2000",
        tipo=TipoDecision.SENTENCIA,
        ponente="Jesús Eduardo Cabrera Romero",
        partes="Emery Mata Millán",
        materia="Amparo constitucional",
        resumen="Sentencia pionera que interpreta el amparo constitucional bajo la CRBV 1999.",
        ratio_decidendi="El amparo constitucional procede cuando se vulneran derechos fundamentales, siendo la Sala Constitucional el máximo intérprete de la Constitución.",
        articulos_crbv=["Art. 27", "Art. 334", "Art. 335", "Art. 336"],
        precedentes_citados=[],
        vinculante=True,
        url="http://historico.tsj.gob.ve/decisiones/scon/enero/01-200100-1529.HTM"
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="00-1289",
        numero_sentencia="93",
        fecha="06-02-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="José M. Delgado Ocando",
        partes="Corpoturismo",
        materia="Control difuso de constitucionalidad",
        resumen="Establece alcance del control difuso de constitucionalidad por todos los jueces.",
        ratio_decidendi="Todo juez puede desaplicar normas inconstitucionales en casos concretos, sometiendo su decisión a revisión de la Sala Constitucional.",
        articulos_crbv=["Art. 334", "Art. 335"],
        precedentes_citados=["Sentencia 1/2000"],
        vinculante=True,
        url="http://historico.tsj.gob.ve/decisiones/scon/febrero/93-060201-001289.HTM"
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="01-2274",
        numero_sentencia="1942",
        fecha="15-07-2003",
        tipo=TipoDecision.SENTENCIA,
        ponente="Jesús Eduardo Cabrera Romero",
        partes="Interpretación Art. 334 CRBV",
        materia="Jurisdicción constitucional",
        resumen="Desarrolla la jurisdicción constitucional y competencias de la Sala Constitucional.",
        ratio_decidendi="La Sala Constitucional es garante de la supremacía y efectividad de las normas constitucionales.",
        articulos_crbv=["Art. 334", "Art. 335", "Art. 336"],
        precedentes_citados=["Sentencia 1/2000", "Sentencia 93/2001"],
        vinculante=True,
        url="http://historico.tsj.gob.ve/decisiones/scon/julio/1942-150703-01-2274.HTM"
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2008-0781",
        numero_sentencia="00647",
        fecha="16-06-2010",
        tipo=TipoDecision.SENTENCIA,
        ponente="Yolanda Jaimes Guerrero",
        partes="PDVSA vs. Ministerio del Poder Popular para la Energía",
        materia="Hidrocarburos",
        resumen="Caso sobre régimen de empresas mixtas en sector hidrocarburos.",
        ratio_decidendi="Las empresas mixtas deben cumplir con los requisitos constitucionales de participación estatal mayoritaria.",
        articulos_crbv=["Art. 302", "Art. 303"],
        precedentes_citados=[],
        vinculante=False,
        url=""
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2005-000456",
        numero_sentencia="RC.00315",
        fecha="21-09-2006",
        tipo=TipoDecision.SENTENCIA,
        ponente="Antonio Ramírez Jiménez",
        partes="Civil - Contratos",
        materia="Contratos",
        resumen="Interpretación de cláusulas contractuales y buena fe.",
        ratio_decidendi="Los contratos deben interpretarse conforme a la buena fe y la común intención de las partes.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url=""
    )
]


def buscar_por_sala(sala: SalaTSJ) -> List[CasoTSJ]:
    """Search cases by TSJ chamber."""
    return [c for c in JURISPRUDENCIA_SAMPLE if c.sala == sala]


def buscar_por_articulo_crbv(articulo: str) -> List[CasoTSJ]:
    """Search cases by CRBV article."""
    articulo_norm = articulo.replace("Art.", "").replace("Artículo", "").strip()
    return [c for c in JURISPRUDENCIA_SAMPLE if any(articulo_norm in art for art in c.articulos_crbv)]


def buscar_por_materia(materia: str) -> List[CasoTSJ]:
    """Search cases by legal matter."""
    materia_lower = materia.lower()
    return [c for c in JURISPRUDENCIA_SAMPLE if materia_lower in c.materia.lower() or materia_lower in c.resumen.lower()]


def buscar_por_texto(texto: str) -> List[CasoTSJ]:
    """Full text search across all fields."""
    texto_lower = texto.lower()
    resultados = []
    for caso in JURISPRUDENCIA_SAMPLE:
        campos = [
            caso.materia,
            caso.resumen,
            caso.ratio_decidendi,
            caso.partes,
            caso.ponente
        ]
        if any(texto_lower in campo.lower() for campo in campos):
            resultados.append(caso)
    return resultados


def buscar_vinculantes() -> List[CasoTSJ]:
    """Get all binding precedents."""
    return [c for c in JURISPRUDENCIA_SAMPLE if c.vinculante]


def generar_reporte_caso(caso: CasoTSJ) -> str:
    """Generate markdown report for a single case."""

    vinculante_str = "**SÍ - VINCULANTE**" if caso.vinculante else "No"

    md = f"""## {caso.sala.value}
### Sentencia No. {caso.numero_sentencia} - Expediente {caso.numero_expediente}

| Campo | Valor |
|-------|-------|
| **Fecha** | {caso.fecha} |
| **Tipo** | {caso.tipo.value} |
| **Ponente** | {caso.ponente} |
| **Partes** | {caso.partes} |
| **Materia** | {caso.materia} |
| **Vinculante** | {vinculante_str} |

### Resumen
{caso.resumen}

### Ratio Decidendi
> {caso.ratio_decidendi}

"""

    if caso.articulos_crbv:
        md += f"### Artículos CRBV Interpretados\n{', '.join(caso.articulos_crbv)}\n\n"

    if caso.precedentes_citados:
        md += f"### Precedentes Citados\n{', '.join(caso.precedentes_citados)}\n\n"

    if caso.url:
        md += f"### Fuente\n[Ver sentencia completa]({caso.url})\n\n"

    md += "---\n\n"

    return md


def generar_reporte_busqueda(resultado: ResultadoBusqueda) -> str:
    """Generate full search report."""

    md = f"""# TSJ Jurisprudence Search Results

**Query:** {resultado.query}
**Search Date:** {resultado.fecha_busqueda}
**Total Results:** {resultado.total_resultados}

---

"""

    if not resultado.casos:
        md += "*No cases found matching the search criteria.*\n\n"
        md += "### Search Suggestions\n"
        for sug in resultado.sugerencias:
            md += f"- {sug}\n"
        return md

    # Group by Sala
    casos_por_sala = {}
    for caso in resultado.casos:
        sala_name = caso.sala.value
        if sala_name not in casos_por_sala:
            casos_por_sala[sala_name] = []
        casos_por_sala[sala_name].append(caso)

    for sala_name, casos in casos_por_sala.items():
        md += f"# {sala_name}\n\n"
        for caso in casos:
            md += generar_reporte_caso(caso)

    if resultado.sugerencias:
        md += "## Related Search Suggestions\n\n"
        for sug in resultado.sugerencias:
            md += f"- {sug}\n"

    return md


def ejecutar_busqueda(
    query: str,
    sala: str = None,
    articulo_crbv: str = None,
    materia: str = None,
    solo_vinculantes: bool = False
) -> ResultadoBusqueda:
    """Execute a jurisprudence search."""

    resultados = []

    # Apply filters
    if sala:
        try:
            sala_enum = SalaTSJ(sala)
            resultados = buscar_por_sala(sala_enum)
        except ValueError:
            # Try to match partial name
            for s in SalaTSJ:
                if sala.lower() in s.value.lower():
                    resultados.extend(buscar_por_sala(s))
    elif articulo_crbv:
        resultados = buscar_por_articulo_crbv(articulo_crbv)
    elif materia:
        resultados = buscar_por_materia(materia)
    else:
        resultados = buscar_por_texto(query)

    # Filter vinculantes if requested
    if solo_vinculantes:
        resultados = [r for r in resultados if r.vinculante]

    # Remove duplicates
    seen = set()
    unique_results = []
    for r in resultados:
        key = (r.sala, r.numero_sentencia, r.fecha)
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    # Generate suggestions
    sugerencias = []
    if not unique_results:
        sugerencias = [
            "Try searching by Sala (e.g., 'Sala Constitucional')",
            "Try searching by CRBV article (e.g., 'Art. 334')",
            "Try searching by legal matter (e.g., 'amparo', 'hidrocarburos')",
            "Use broader search terms"
        ]
    else:
        # Suggest related searches
        materias = set(r.materia for r in unique_results)
        for mat in list(materias)[:3]:
            sugerencias.append(f"More cases on: {mat}")

    return ResultadoBusqueda(
        query=query,
        fecha_busqueda=datetime.now().isoformat(),
        total_resultados=len(unique_results),
        casos=unique_results,
        sugerencias=sugerencias
    )


def main():
    """Main function for CLI usage."""

    if len(sys.argv) < 2:
        print("Venezuela Super Lawyer - TSJ Jurisprudence Search")
        print("\nUsage:")
        print("  python3 tsj_search.py <search_query>")
        print("  python3 tsj_search.py --sala 'Sala Constitucional'")
        print("  python3 tsj_search.py --articulo 'Art. 334'")
        print("  python3 tsj_search.py --materia 'amparo'")
        print("  python3 tsj_search.py --vinculantes")
        print("  python3 tsj_search.py --salas")
        print("\nExamples:")
        print("  python3 tsj_search.py 'control difuso'")
        print("  python3 tsj_search.py --sala 'Sala Constitucional'")
        print("  python3 tsj_search.py --articulo '334'")
        sys.exit(0)

    if sys.argv[1] == "--salas":
        print("TSJ Chambers (Salas):\n")
        for sala in SalaTSJ:
            print(f"  - {sala.value}")
        sys.exit(0)

    if sys.argv[1] == "--vinculantes":
        resultado = ejecutar_busqueda("vinculantes", solo_vinculantes=True)
        print(generar_reporte_busqueda(resultado))
        sys.exit(0)

    # Parse arguments
    query = ""
    sala = None
    articulo = None
    materia = None
    solo_vinculantes = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--sala" and i + 1 < len(sys.argv):
            sala = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--articulo" and i + 1 < len(sys.argv):
            articulo = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--materia" and i + 1 < len(sys.argv):
            materia = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--vinculantes":
            solo_vinculantes = True
            i += 1
        else:
            query = sys.argv[i]
            i += 1

    resultado = ejecutar_busqueda(
        query=query,
        sala=sala,
        articulo_crbv=articulo,
        materia=materia,
        solo_vinculantes=solo_vinculantes
    )

    print(generar_reporte_busqueda(resultado))


if __name__ == "__main__":
    main()
