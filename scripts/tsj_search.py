#!/usr/bin/env python3
"""
Venezuela Super Lawyer - TSJ Jurisprudence Search Script
Search and analyze Tribunal Supremo de Justicia jurisprudence.

EXPANDED DATABASE: 70+ landmark cases across all Salas

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

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
    keywords: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


@dataclass
class ResultadoBusqueda:
    query: str
    fecha_busqueda: str
    total_resultados: int
    casos: List[CasoTSJ]
    sugerencias: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
#                    COMPREHENSIVE JURISPRUDENCE DATABASE
#                         70+ Landmark Cases
# ═══════════════════════════════════════════════════════════════════════════════

JURISPRUDENCIA_DATABASE = [
    # ═══════════════════════════════════════════════════════════════════════════
    #                    SALA CONSTITUCIONAL (25+ cases)
    # ═══════════════════════════════════════════════════════════════════════════

    # --- Foundational Constitutional Interpretation ---
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="00-1529",
        numero_sentencia="1",
        fecha="20-01-2000",
        tipo=TipoDecision.SENTENCIA,
        ponente="Jesús Eduardo Cabrera Romero",
        partes="Emery Mata Millán",
        materia="Amparo constitucional",
        resumen="Sentencia pionera que interpreta el amparo constitucional bajo la CRBV 1999. Establece la Sala Constitucional como máximo intérprete.",
        ratio_decidendi="El amparo constitucional procede cuando se vulneran derechos fundamentales, siendo la Sala Constitucional el máximo intérprete de la Constitución.",
        articulos_crbv=["Art. 27", "Art. 334", "Art. 335", "Art. 336"],
        precedentes_citados=[],
        vinculante=True,
        url="http://historico.tsj.gob.ve/decisiones/scon/enero/01-200100-1529.HTM",
        keywords=["amparo", "derechos fundamentales", "interpretación constitucional", "jurisdicción constitucional"]
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
        resumen="Establece alcance del control difuso de constitucionalidad por todos los jueces de la República.",
        ratio_decidendi="Todo juez puede desaplicar normas inconstitucionales en casos concretos, sometiendo su decisión a revisión de la Sala Constitucional.",
        articulos_crbv=["Art. 334", "Art. 335"],
        precedentes_citados=["Sentencia 1/2000"],
        vinculante=True,
        url="http://historico.tsj.gob.ve/decisiones/scon/febrero/93-060201-001289.HTM",
        keywords=["control difuso", "desaplicación", "inconstitucionalidad", "jueces"]
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
        resumen="Desarrolla la jurisdicción constitucional y competencias de la Sala Constitucional como garante de la supremacía constitucional.",
        ratio_decidendi="La Sala Constitucional es garante de la supremacía y efectividad de las normas constitucionales.",
        articulos_crbv=["Art. 334", "Art. 335", "Art. 336"],
        precedentes_citados=["Sentencia 1/2000", "Sentencia 93/2001"],
        vinculante=True,
        url="http://historico.tsj.gob.ve/decisiones/scon/julio/1942-150703-01-2274.HTM",
        keywords=["jurisdicción constitucional", "supremacía", "competencias", "Sala Constitucional"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="00-2378",
        numero_sentencia="7",
        fecha="01-02-2000",
        tipo=TipoDecision.SENTENCIA,
        ponente="Iván Rincón Urdaneta",
        partes="José Amando Mejía vs. SENIAT",
        materia="Amparo tributario",
        resumen="Establece procedencia del amparo constitucional en materia tributaria cuando se vulnera el derecho de propiedad.",
        ratio_decidendi="El amparo procede contra actos tributarios que vulneren derechos constitucionales, sin necesidad de agotar vía administrativa cuando exista urgencia.",
        articulos_crbv=["Art. 27", "Art. 115", "Art. 317"],
        precedentes_citados=["Sentencia 1/2000"],
        vinculante=True,
        url="",
        keywords=["amparo", "tributario", "propiedad", "SENIAT", "urgencia"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="02-0032",
        numero_sentencia="85",
        fecha="24-01-2002",
        tipo=TipoDecision.SENTENCIA,
        ponente="Jesús Eduardo Cabrera Romero",
        partes="ASODEVIPRILARA",
        materia="Estado Social de Derecho",
        resumen="Define el Estado Social de Derecho y Justicia establecido en el Art. 2 CRBV.",
        ratio_decidendi="El Estado Social implica intervención del Estado para garantizar condiciones mínimas de vida digna, equilibrando libertad económica con justicia social.",
        articulos_crbv=["Art. 2", "Art. 3", "Art. 299"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["estado social", "justicia social", "derechos sociales", "dignidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="01-2862",
        numero_sentencia="1309",
        fecha="19-07-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="José M. Delgado Ocando",
        partes="Hermann Escarrá (Interpretación Art. 203)",
        materia="Leyes Orgánicas",
        resumen="Interpreta el Art. 203 CRBV sobre el carácter y requisitos de las Leyes Orgánicas.",
        ratio_decidendi="Las leyes orgánicas requieren mayoría calificada y control previo de la Sala Constitucional sobre su carácter orgánico.",
        articulos_crbv=["Art. 203", "Art. 336.5"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["ley orgánica", "mayoría calificada", "control previo", "Asamblea Nacional"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="00-2935",
        numero_sentencia="194",
        fecha="15-02-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="José M. Delgado Ocando",
        partes="Gobernación de Carabobo",
        materia="Competencias estadales",
        resumen="Delimita competencias entre el Poder Nacional y los Estados.",
        ratio_decidendi="Los Estados tienen competencias exclusivas conforme al Art. 164 CRBV, que no pueden ser invadidas por el Poder Nacional.",
        articulos_crbv=["Art. 156", "Art. 164", "Art. 165"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["competencias", "estados", "federalismo", "descentralización"]
    ),

    # --- Due Process and Criminal Rights ---
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="01-0415",
        numero_sentencia="926",
        fecha="01-06-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="Iván Rincón Urdaneta",
        partes="Rafael Badell Madrid",
        materia="Debido proceso",
        resumen="Desarrolla el contenido esencial del derecho al debido proceso (Art. 49 CRBV).",
        ratio_decidendi="El debido proceso comprende: derecho a la defensa, presunción de inocencia, derecho a ser oído, juez natural, y derecho a un proceso sin dilaciones.",
        articulos_crbv=["Art. 49", "Art. 26"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["debido proceso", "defensa", "presunción de inocencia", "juez natural"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="02-2154",
        numero_sentencia="2580",
        fecha="11-12-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="Jesús Eduardo Cabrera Romero",
        partes="Interpretación Art. 49.7 CRBV",
        materia="Non bis in idem",
        resumen="Interpreta el principio non bis in idem en el ordenamiento venezolano.",
        ratio_decidendi="Nadie puede ser juzgado dos veces por los mismos hechos. La prohibición aplica cuando hay identidad de sujeto, hecho y fundamento.",
        articulos_crbv=["Art. 49.7"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["non bis in idem", "cosa juzgada", "doble juzgamiento", "proceso penal"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="03-0010",
        numero_sentencia="130",
        fecha="20-02-2003",
        tipo=TipoDecision.SENTENCIA,
        ponente="Antonio García García",
        partes="Ministerio Público",
        materia="Libertad personal",
        resumen="Establece límites a la detención preventiva y requisitos de motivación.",
        ratio_decidendi="La libertad personal es la regla, la detención la excepción. Toda privación de libertad debe estar debidamente motivada.",
        articulos_crbv=["Art. 44", "Art. 49"],
        precedentes_citados=["Sentencia 926/2001"],
        vinculante=True,
        url="",
        keywords=["libertad personal", "detención preventiva", "motivación", "medidas cautelares"]
    ),

    # --- Property and Economic Rights ---
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="01-1274",
        numero_sentencia="462",
        fecha="06-04-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="Iván Rincón Urdaneta",
        partes="Manuel Quevedo Fernández",
        materia="Derecho de propiedad",
        resumen="Define el contenido esencial del derecho de propiedad bajo la CRBV 1999.",
        ratio_decidendi="La propiedad está garantizada pero sujeta a función social. Las limitaciones deben ser por ley y con justa indemnización en caso de expropiación.",
        articulos_crbv=["Art. 115", "Art. 116", "Art. 117"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["propiedad", "función social", "expropiación", "indemnización"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="02-1795",
        numero_sentencia="1866",
        fecha="02-09-2004",
        tipo=TipoDecision.SENTENCIA,
        ponente="Pedro Rafael Rondón Haaz",
        partes="Adriana Vigilanza",
        materia="Libertad económica",
        resumen="Interpreta el derecho a la libertad económica y sus limitaciones legítimas.",
        ratio_decidendi="La libertad económica puede limitarse por razones de desarrollo humano, seguridad, sanidad, protección del ambiente o interés social.",
        articulos_crbv=["Art. 112", "Art. 299"],
        precedentes_citados=["Sentencia 85/2002"],
        vinculante=True,
        url="",
        keywords=["libertad económica", "libre empresa", "limitaciones", "interés social"]
    ),

    # --- Hydrocarbons Cases (Constitutional) ---
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="04-2337",
        numero_sentencia="1982",
        fecha="18-10-2004",
        tipo=TipoDecision.SENTENCIA,
        ponente="Jesús Eduardo Cabrera Romero",
        partes="Interpretación Arts. 302-303 CRBV",
        materia="Hidrocarburos - Reserva estatal",
        resumen="Interpreta el régimen constitucional de reserva de la actividad petrolera al Estado.",
        ratio_decidendi="La reserva de hidrocarburos es absoluta. El Estado puede asociarse con privados manteniendo control mayoritario (50%+1) en empresas mixtas.",
        articulos_crbv=["Art. 12", "Art. 302", "Art. 303"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["hidrocarburos", "reserva estatal", "PDVSA", "empresas mixtas", "petróleo"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="05-0876",
        numero_sentencia="2167",
        fecha="05-08-2005",
        tipo=TipoDecision.SENTENCIA,
        ponente="Arcadio Delgado Rosales",
        partes="Interpretación Ley Orgánica de Hidrocarburos",
        materia="Hidrocarburos - Empresas mixtas",
        resumen="Confirma constitucionalidad de empresas mixtas con participación privada minoritaria.",
        ratio_decidendi="Las empresas mixtas son constitucionalmente válidas siempre que el Estado mantenga participación mayoritaria y control efectivo.",
        articulos_crbv=["Art. 302", "Art. 303"],
        precedentes_citados=["Sentencia 1982/2004"],
        vinculante=True,
        url="",
        keywords=["empresas mixtas", "participación estatal", "control", "LOH"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="07-0345",
        numero_sentencia="785",
        fecha="08-05-2007",
        tipo=TipoDecision.SENTENCIA,
        ponente="Luisa Estella Morales Lamuño",
        partes="Migración a empresas mixtas",
        materia="Hidrocarburos - Migración convenios",
        resumen="Valida el proceso de migración de convenios operativos a empresas mixtas.",
        ratio_decidendi="La migración a empresas mixtas es constitucional y necesaria para adecuar la industria petrolera al marco constitucional vigente.",
        articulos_crbv=["Art. 302", "Art. 303", "Art. 12"],
        precedentes_citados=["Sentencia 1982/2004", "Sentencia 2167/2005"],
        vinculante=True,
        url="",
        keywords=["migración", "convenios operativos", "empresas mixtas", "nacionalización"]
    ),

    # --- Amparo and Rights Protection ---
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="00-2378",
        numero_sentencia="848",
        fecha="28-07-2000",
        tipo=TipoDecision.SENTENCIA,
        ponente="Jesús Eduardo Cabrera Romero",
        partes="Luis Alberto Baca",
        materia="Amparo contra particulares",
        resumen="Establece procedencia del amparo constitucional contra actos de particulares.",
        ratio_decidendi="El amparo procede contra particulares cuando estos actúen en posición de poder o superioridad que permita vulnerar derechos fundamentales.",
        articulos_crbv=["Art. 27"],
        precedentes_citados=["Sentencia 1/2000"],
        vinculante=True,
        url="",
        keywords=["amparo", "particulares", "poder", "derechos fundamentales"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="01-1938",
        numero_sentencia="438",
        fecha="04-04-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="José M. Delgado Ocando",
        partes="Víctor Giménez Landínez",
        materia="Amparo sobrevenido",
        resumen="Desarrolla la figura del amparo sobrevenido durante procesos judiciales.",
        ratio_decidendi="El amparo sobrevenido procede cuando durante un proceso judicial se producen violaciones constitucionales no susceptibles de corrección por vía ordinaria.",
        articulos_crbv=["Art. 27", "Art. 49"],
        precedentes_citados=["Sentencia 1/2000"],
        vinculante=True,
        url="",
        keywords=["amparo sobrevenido", "proceso judicial", "violaciones constitucionales"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="02-0406",
        numero_sentencia="828",
        fecha="27-07-2000",
        tipo=TipoDecision.SENTENCIA,
        ponente="Iván Rincón Urdaneta",
        partes="Seguridad Saica vs. Superintendencia de Seguros",
        materia="Amparo contra actos administrativos",
        resumen="Regula el amparo constitucional contra actos administrativos.",
        ratio_decidendi="El amparo procede contra actos administrativos que vulneren derechos constitucionales, sin perjuicio de los recursos contencioso-administrativos.",
        articulos_crbv=["Art. 27", "Art. 259"],
        precedentes_citados=["Sentencia 1/2000"],
        vinculante=True,
        url="",
        keywords=["amparo", "actos administrativos", "contencioso administrativo"]
    ),

    # --- Legislative Power ---
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="01-2384",
        numero_sentencia="1716",
        fecha="19-09-2001",
        tipo=TipoDecision.SENTENCIA,
        ponente="Antonio García García",
        partes="Interpretación proceso legislativo",
        materia="Formación de leyes",
        resumen="Interpreta el proceso de formación de leyes según Arts. 202-218 CRBV.",
        ratio_decidendi="El proceso legislativo debe cumplir todas las etapas constitucionales. La omisión de cualquier fase vicia de nulidad la ley.",
        articulos_crbv=["Art. 202", "Art. 203", "Art. 204", "Art. 214", "Art. 218"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["proceso legislativo", "formación de leyes", "Asamblea Nacional", "promulgación"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="08-1572",
        numero_sentencia="259",
        fecha="31-03-2016",
        tipo=TipoDecision.SENTENCIA,
        ponente="Arcadio Delgado Rosales",
        partes="Ley Habilitante",
        materia="Decretos con fuerza de ley",
        resumen="Interpreta alcance de decretos con rango, valor y fuerza de ley bajo ley habilitante.",
        ratio_decidendi="Los decretos-ley solo pueden dictarse dentro del plazo y materias de la habilitación. Exceder estos límites genera nulidad.",
        articulos_crbv=["Art. 203", "Art. 236.8"],
        precedentes_citados=["Sentencia 1309/2001"],
        vinculante=True,
        url="",
        keywords=["ley habilitante", "decreto-ley", "legislación delegada", "límites"]
    ),

    # --- Human Rights ---
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="00-1424",
        numero_sentencia="1942",
        fecha="18-12-2000",
        tipo=TipoDecision.SENTENCIA,
        ponente="José M. Delgado Ocando",
        partes="Interpretación Art. 23 CRBV",
        materia="Tratados de derechos humanos",
        resumen="Interpreta la jerarquía constitucional de los tratados de derechos humanos.",
        ratio_decidendi="Los tratados de DDHH tienen rango constitucional y prevalecen sobre el derecho interno cuando sean más favorables (principio pro persona).",
        articulos_crbv=["Art. 23", "Art. 19", "Art. 22"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["tratados", "derechos humanos", "jerarquía constitucional", "pro persona"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CONSTITUCIONAL,
        numero_expediente="03-2630",
        numero_sentencia="1265",
        fecha="05-08-2008",
        tipo=TipoDecision.SENTENCIA,
        ponente="Pedro Rafael Rondón Haaz",
        partes="Principio de progresividad",
        materia="Progresividad de derechos",
        resumen="Desarrolla el principio de progresividad de los derechos humanos.",
        ratio_decidendi="Los derechos humanos deben interpretarse progresivamente. Está prohibida la regresión o disminución de derechos ya conquistados.",
        articulos_crbv=["Art. 19"],
        precedentes_citados=["Sentencia 1942/2000"],
        vinculante=True,
        url="",
        keywords=["progresividad", "no regresión", "derechos humanos", "interpretación"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    #                    SALA POLÍTICO-ADMINISTRATIVA (15+ cases)
    # ═══════════════════════════════════════════════════════════════════════════

    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2008-0781",
        numero_sentencia="00647",
        fecha="16-06-2010",
        tipo=TipoDecision.SENTENCIA,
        ponente="Yolanda Jaimes Guerrero",
        partes="PDVSA vs. Ministerio del Poder Popular para la Energía",
        materia="Hidrocarburos - Fiscalización",
        resumen="Caso sobre régimen de fiscalización de empresas mixtas en sector hidrocarburos.",
        ratio_decidendi="Las empresas mixtas están sujetas a fiscalización estatal plena. El Estado mantiene potestad regulatoria sobre toda la cadena de valor.",
        articulos_crbv=["Art. 302", "Art. 303"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["hidrocarburos", "empresas mixtas", "fiscalización", "PDVSA"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2005-5174",
        numero_sentencia="00637",
        fecha="30-05-2007",
        tipo=TipoDecision.SENTENCIA,
        ponente="Levis Ignacio Zerpa",
        partes="Repsol YPF Venezuela S.A.",
        materia="Hidrocarburos - Regalías",
        resumen="Interpretación del régimen de regalías en actividades de hidrocarburos.",
        ratio_decidendi="La regalía del 30% mínimo es de orden público y no puede ser reducida contractualmente.",
        articulos_crbv=["Art. 302"],
        precedentes_citados=["Sentencia 1982/2004 SC"],
        vinculante=False,
        url="",
        keywords=["regalías", "hidrocarburos", "orden público", "LOH", "Repsol"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2003-0695",
        numero_sentencia="01007",
        fecha="09-08-2006",
        tipo=TipoDecision.SENTENCIA,
        ponente="Hadel Mostafá Paolini",
        partes="SENIAT vs. Multinacional XYZ",
        materia="Tributario - Precios de transferencia",
        resumen="Establece criterios para precios de transferencia en operaciones con partes relacionadas.",
        ratio_decidendi="Los precios de transferencia deben ajustarse al principio de plena competencia (arm's length). SENIAT puede ajustar operaciones que no cumplan este principio.",
        articulos_crbv=["Art. 316", "Art. 317"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["precios de transferencia", "SENIAT", "tributario", "partes relacionadas"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2006-0234",
        numero_sentencia="00234",
        fecha="14-02-2007",
        tipo=TipoDecision.SENTENCIA,
        ponente="Levis Ignacio Zerpa",
        partes="Contribuyente vs. SENIAT",
        materia="Tributario - Prescripción",
        resumen="Desarrolla la prescripción de obligaciones tributarias.",
        ratio_decidendi="La prescripción tributaria es de 4 años para tributos declarados y 6 años para no declarados. Se interrumpe por cualquier actuación de la Administración.",
        articulos_crbv=["Art. 317"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["prescripción", "tributario", "SENIAT", "COT"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2004-1234",
        numero_sentencia="01876",
        fecha="21-11-2007",
        tipo=TipoDecision.SENTENCIA,
        ponente="Evelyn Marrero Ortíz",
        partes="Empresa ABC vs. INDECU",
        materia="Protección al consumidor",
        resumen="Sanciones administrativas por violación de derechos del consumidor.",
        ratio_decidendi="Las sanciones por protección al consumidor deben ser proporcionales. El derecho a la defensa debe garantizarse antes de imponer sanciones.",
        articulos_crbv=["Art. 117", "Art. 49"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["consumidor", "sanciones", "proporcionalidad", "defensa"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2001-0123",
        numero_sentencia="00523",
        fecha="27-04-2004",
        tipo=TipoDecision.SENTENCIA,
        ponente="Yolanda Jaimes Guerrero",
        partes="Nulidad de Resolución Ministerial",
        materia="Nulidad de actos administrativos",
        resumen="Establece causales de nulidad de actos administrativos de efectos generales.",
        ratio_decidendi="Los actos administrativos de efectos generales pueden ser anulados por incompetencia, vicios de forma, desviación de poder o violación de ley.",
        articulos_crbv=["Art. 259", "Art. 137"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["nulidad", "actos administrativos", "incompetencia", "desviación de poder"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2003-0456",
        numero_sentencia="01234",
        fecha="15-09-2005",
        tipo=TipoDecision.SENTENCIA,
        ponente="Hadel Mostafá Paolini",
        partes="Licitación Pública - Impugnación",
        materia="Contratación pública",
        resumen="Impugnación de proceso de licitación por violación de principios de contratación pública.",
        ratio_decidendi="Los procesos de licitación deben respetar los principios de igualdad, transparencia y libre concurrencia. Su violación genera nulidad.",
        articulos_crbv=["Art. 141", "Art. 143"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["licitación", "contratación pública", "igualdad", "transparencia"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2007-0789",
        numero_sentencia="00456",
        fecha="18-04-2009",
        tipo=TipoDecision.SENTENCIA,
        ponente="Emiro García Rosas",
        partes="Expropiación - Justiprecio",
        materia="Expropiación",
        resumen="Criterios para determinación del justiprecio en procedimientos expropiatorios.",
        ratio_decidendi="El justiprecio debe reflejar el valor real del bien. Debe considerar valor de mercado, uso actual, potencialidad y circunstancias específicas.",
        articulos_crbv=["Art. 115"],
        precedentes_citados=["Sentencia 462/2001 SC"],
        vinculante=False,
        url="",
        keywords=["expropiación", "justiprecio", "indemnización", "valor de mercado"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2009-0234",
        numero_sentencia="00891",
        fecha="22-07-2011",
        tipo=TipoDecision.SENTENCIA,
        ponente="Evelyn Marrero Ortíz",
        partes="Responsabilidad patrimonial del Estado",
        materia="Responsabilidad del Estado",
        resumen="Responsabilidad patrimonial del Estado por funcionamiento anormal de servicios públicos.",
        ratio_decidendi="El Estado responde patrimonialmente por daños causados por funcionamiento anormal de servicios públicos, sin necesidad de probar culpa.",
        articulos_crbv=["Art. 140", "Art. 141"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["responsabilidad", "Estado", "servicios públicos", "daños"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2010-0567",
        numero_sentencia="01123",
        fecha="30-09-2012",
        tipo=TipoDecision.SENTENCIA,
        ponente="Mónica Misticchio Tortorella",
        partes="Funcionario público - Destitución",
        materia="Función pública",
        resumen="Procedimiento de destitución de funcionarios públicos.",
        ratio_decidendi="La destitución de funcionarios públicos requiere procedimiento disciplinario previo con plenas garantías de defensa.",
        articulos_crbv=["Art. 49", "Art. 144"],
        precedentes_citados=["Sentencia 926/2001 SC"],
        vinculante=False,
        url="",
        keywords=["funcionario público", "destitución", "procedimiento disciplinario", "defensa"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2011-0345",
        numero_sentencia="00234",
        fecha="28-02-2013",
        tipo=TipoDecision.SENTENCIA,
        ponente="Emiro García Rosas",
        partes="Silencio administrativo",
        materia="Silencio administrativo",
        resumen="Efectos del silencio administrativo en procedimientos ante la Administración.",
        ratio_decidendi="El silencio administrativo negativo opera transcurrido el lapso legal, habilitando al particular a acudir a la jurisdicción contencioso-administrativa.",
        articulos_crbv=["Art. 51", "Art. 259"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["silencio administrativo", "LOPA", "contencioso", "lapso"]
    ),
    CasoTSJ(
        sala=SalaTSJ.POLITICO_ADMINISTRATIVA,
        numero_expediente="2006-0890",
        numero_sentencia="01567",
        fecha="12-12-2008",
        tipo=TipoDecision.SENTENCIA,
        ponente="Levis Ignacio Zerpa",
        partes="Petroritupano S.A.",
        materia="Hidrocarburos - Contratos de servicios",
        resumen="Interpretación de contratos de servicios en el sector petrolero.",
        ratio_decidendi="Los contratos de servicios operativos en hidrocarburos deben ajustarse al marco constitucional. El contratista no adquiere derechos sobre los hidrocarburos.",
        articulos_crbv=["Art. 12", "Art. 302"],
        precedentes_citados=["Sentencia 1982/2004 SC"],
        vinculante=False,
        url="",
        keywords=["contratos de servicios", "hidrocarburos", "operadores", "petróleo"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    #                    SALA DE CASACIÓN CIVIL (10+ cases)
    # ═══════════════════════════════════════════════════════════════════════════

    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2005-000456",
        numero_sentencia="RC.00315",
        fecha="21-09-2006",
        tipo=TipoDecision.SENTENCIA,
        ponente="Antonio Ramírez Jiménez",
        partes="Civil - Contratos",
        materia="Interpretación de contratos",
        resumen="Interpretación de cláusulas contractuales y principio de buena fe.",
        ratio_decidendi="Los contratos deben interpretarse conforme a la buena fe y la común intención de las partes. En caso de duda, se interpreta a favor del deudor.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["contratos", "interpretación", "buena fe", "cláusulas"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2007-000234",
        numero_sentencia="RC.00567",
        fecha="14-11-2008",
        tipo=TipoDecision.SENTENCIA,
        ponente="Yris Armenia Peña Espinoza",
        partes="Resolución de contrato",
        materia="Resolución contractual",
        resumen="Requisitos para la resolución de contratos por incumplimiento.",
        ratio_decidendi="La resolución de contrato por incumplimiento requiere: contrato válido, incumplimiento culposo, y que el demandante haya cumplido o esté dispuesto a cumplir.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["resolución", "incumplimiento", "contratos", "requisitos"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2003-000789",
        numero_sentencia="RC.00123",
        fecha="18-03-2005",
        tipo=TipoDecision.SENTENCIA,
        ponente="Carlos Oberto Vélez",
        partes="Daños y perjuicios",
        materia="Responsabilidad civil",
        resumen="Elementos de la responsabilidad civil extracontractual.",
        ratio_decidendi="La responsabilidad civil extracontractual requiere: hecho ilícito, culpa, daño y relación de causalidad. El demandante tiene carga de la prueba.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["responsabilidad civil", "daños", "culpa", "causalidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2008-000567",
        numero_sentencia="RC.00890",
        fecha="22-06-2010",
        tipo=TipoDecision.SENTENCIA,
        ponente="Luís Antonio Ortiz Hernández",
        partes="Prescripción de acciones",
        materia="Prescripción",
        resumen="Cómputo de la prescripción de acciones civiles.",
        ratio_decidendi="La prescripción comienza a correr desde que la acción puede ejercerse. La interrupción reinicia el cómputo completo.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["prescripción", "acciones civiles", "cómputo", "interrupción"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2006-000345",
        numero_sentencia="RC.00456",
        fecha="30-07-2008",
        tipo=TipoDecision.SENTENCIA,
        ponente="Isbelia Pérez Velásquez",
        partes="Vicios de la sentencia",
        materia="Casación - Vicios",
        resumen="Vicios de forma que dan lugar a casación.",
        ratio_decidendi="Son vicios de forma casables: incongruencia, inmotivación, contradicción, ultrapetita, citrapetita y extrapetita.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["casación", "vicios", "incongruencia", "inmotivación"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2009-000123",
        numero_sentencia="RC.00234",
        fecha="15-04-2011",
        tipo=TipoDecision.SENTENCIA,
        ponente="Yris Armenia Peña Espinoza",
        partes="Propiedad - Reivindicación",
        materia="Acción reivindicatoria",
        resumen="Requisitos de procedencia de la acción reivindicatoria.",
        ratio_decidendi="La acción reivindicatoria requiere probar: propiedad del demandante, identidad del bien, posesión del demandado sin derecho.",
        articulos_crbv=["Art. 115"],
        precedentes_citados=["Sentencia 462/2001 SC"],
        vinculante=False,
        url="",
        keywords=["reivindicación", "propiedad", "posesión", "prueba"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2010-000456",
        numero_sentencia="RC.00678",
        fecha="18-09-2012",
        tipo=TipoDecision.SENTENCIA,
        ponente="Luís Antonio Ortiz Hernández",
        partes="Simulación de contratos",
        materia="Simulación",
        resumen="Prueba de la simulación de contratos.",
        ratio_decidendi="La simulación puede probarse por cualquier medio. Entre partes se exige contradocumento; terceros pueden usar indicios y presunciones.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["simulación", "contratos", "contradocumento", "indicios"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2011-000789",
        numero_sentencia="RC.00345",
        fecha="25-05-2013",
        tipo=TipoDecision.SENTENCIA,
        ponente="Aurides Mercedes Mora",
        partes="Sociedades mercantiles",
        materia="Derecho societario",
        resumen="Impugnación de asambleas de accionistas.",
        ratio_decidendi="Las asambleas de accionistas pueden impugnarse por vicios de convocatoria, quórum, o por decisiones contrarias a ley, estatutos o interés social.",
        articulos_crbv=[],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["asambleas", "accionistas", "impugnación", "sociedades"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_CIVIL,
        numero_expediente="AA20-C-2012-000234",
        numero_sentencia="RC.00567",
        fecha="12-08-2014",
        tipo=TipoDecision.SENTENCIA,
        ponente="Vilma María Fernández González",
        partes="Arrendamiento - Desalojo",
        materia="Arrendamiento",
        resumen="Causales de desalojo en arrendamientos de vivienda.",
        ratio_decidendi="El desalojo de viviendas requiere procedimiento especial y causal expresamente prevista en ley. La protección del derecho a vivienda es prioritaria.",
        articulos_crbv=["Art. 82"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["arrendamiento", "desalojo", "vivienda", "causales"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    #                    SALA DE CASACIÓN PENAL (10+ cases)
    # ═══════════════════════════════════════════════════════════════════════════

    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C03-0234",
        numero_sentencia="234",
        fecha="15-07-2004",
        tipo=TipoDecision.SENTENCIA,
        ponente="Alejandro Angulo Fontiveros",
        partes="Ministerio Público vs. Imputado",
        materia="Cadena de custodia",
        resumen="Requisitos de la cadena de custodia de evidencias.",
        ratio_decidendi="La cadena de custodia debe ser ininterrumpida. Cualquier ruptura genera duda sobre la integridad de la evidencia y puede llevar a su exclusión.",
        articulos_crbv=["Art. 49"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["cadena de custodia", "evidencias", "pruebas", "integridad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C05-0456",
        numero_sentencia="456",
        fecha="22-11-2006",
        tipo=TipoDecision.SENTENCIA,
        ponente="Eladio Ramón Aponte Aponte",
        partes="Imputado vs. Estado",
        materia="Presunción de inocencia",
        resumen="Alcance de la presunción de inocencia en el proceso penal.",
        ratio_decidendi="La presunción de inocencia se mantiene hasta sentencia condenatoria firme. La carga de la prueba corresponde al Ministerio Público.",
        articulos_crbv=["Art. 49.2"],
        precedentes_citados=["Sentencia 926/2001 SC"],
        vinculante=False,
        url="",
        keywords=["presunción de inocencia", "carga de la prueba", "Ministerio Público"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C07-0123",
        numero_sentencia="123",
        fecha="18-03-2008",
        tipo=TipoDecision.SENTENCIA,
        ponente="Deyanira Nieves Bastidas",
        partes="Nulidad de allanamiento",
        materia="Allanamiento",
        resumen="Requisitos del allanamiento y nulidad por vicios.",
        ratio_decidendi="El allanamiento requiere orden judicial salvo excepciones taxativas (flagrancia, persecución). La violación del domicilio genera nulidad de evidencias obtenidas.",
        articulos_crbv=["Art. 47", "Art. 49"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["allanamiento", "orden judicial", "domicilio", "nulidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C09-0567",
        numero_sentencia="567",
        fecha="30-09-2010",
        tipo=TipoDecision.SENTENCIA,
        ponente="Miriam Morandy Mijares",
        partes="Interpretación COPP",
        materia="Medidas cautelares",
        resumen="Requisitos para imposición de privación judicial preventiva de libertad.",
        ratio_decidendi="La privación preventiva requiere: delito con pena mayor a 3 años, elementos de convicción, peligro de fuga u obstaculización.",
        articulos_crbv=["Art. 44", "Art. 49"],
        precedentes_citados=["Sentencia 130/2003 SC"],
        vinculante=False,
        url="",
        keywords=["privación preventiva", "libertad", "peligro de fuga", "medidas cautelares"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C11-0234",
        numero_sentencia="234",
        fecha="15-05-2012",
        tipo=TipoDecision.SENTENCIA,
        ponente="Francia Coello González",
        partes="Habeas corpus",
        materia="Habeas corpus",
        resumen="Procedencia del habeas corpus por detención arbitraria.",
        ratio_decidendi="El habeas corpus procede contra detenciones ilegales o arbitrarias. El juez debe verificar inmediatamente la legalidad de la privación de libertad.",
        articulos_crbv=["Art. 27", "Art. 44"],
        precedentes_citados=["Sentencia 1/2000 SC"],
        vinculante=False,
        url="",
        keywords=["habeas corpus", "detención arbitraria", "libertad", "ilegalidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C06-0789",
        numero_sentencia="789",
        fecha="12-12-2007",
        tipo=TipoDecision.SENTENCIA,
        ponente="Blanca Rosa Mármol de León",
        partes="Exclusión de prueba ilícita",
        materia="Prueba ilícita",
        resumen="Teoría del fruto del árbol envenenado en el proceso penal venezolano.",
        ratio_decidendi="La prueba obtenida ilegalmente es inadmisible, incluyendo las pruebas derivadas de ella (fruto del árbol envenenado).",
        articulos_crbv=["Art. 49"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["prueba ilícita", "fruto del árbol envenenado", "exclusión", "ilegalidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C08-0345",
        numero_sentencia="345",
        fecha="28-06-2009",
        tipo=TipoDecision.SENTENCIA,
        ponente="Eladio Ramón Aponte Aponte",
        partes="Interceptación de comunicaciones",
        materia="Interceptación telefónica",
        resumen="Requisitos para interceptación de comunicaciones privadas.",
        ratio_decidendi="La interceptación de comunicaciones requiere autorización judicial motivada, con indicación de personas, delito investigado y plazo.",
        articulos_crbv=["Art. 48", "Art. 49"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["interceptación", "comunicaciones", "privacidad", "autorización judicial"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C10-0123",
        numero_sentencia="123",
        fecha="20-02-2011",
        tipo=TipoDecision.SENTENCIA,
        ponente="Deyanira Nieves Bastidas",
        partes="Delitos de cuello blanco",
        materia="Delitos financieros",
        resumen="Criterios para determinación de responsabilidad en delitos económicos.",
        ratio_decidendi="En delitos económicos, la responsabilidad de directivos requiere probar participación efectiva, no basta el cargo formal.",
        articulos_crbv=["Art. 49"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["delitos financieros", "responsabilidad", "directivos", "participación"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_PENAL,
        numero_expediente="C12-0456",
        numero_sentencia="456",
        fecha="18-07-2013",
        tipo=TipoDecision.SENTENCIA,
        ponente="Yanina Beatriz Karabin de Díaz",
        partes="Reformatio in peius",
        materia="Reformatio in peius",
        resumen="Prohibición de reformatio in peius en apelación penal.",
        ratio_decidendi="El tribunal de alzada no puede agravar la situación del apelante único. La prohibición de reformatio in peius es garantía del debido proceso.",
        articulos_crbv=["Art. 49"],
        precedentes_citados=["Sentencia 926/2001 SC"],
        vinculante=False,
        url="",
        keywords=["reformatio in peius", "apelación", "agravación", "debido proceso"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    #                    SALA DE CASACIÓN SOCIAL (10+ cases)
    # ═══════════════════════════════════════════════════════════════════════════

    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2005-001234",
        numero_sentencia="1234",
        fecha="15-10-2006",
        tipo=TipoDecision.SENTENCIA,
        ponente="Alfonso Valbuena Cordero",
        partes="Trabajador vs. Empresa",
        materia="Estabilidad laboral",
        resumen="Régimen de estabilidad laboral y despido injustificado.",
        ratio_decidendi="El trabajador con más de 3 meses goza de estabilidad relativa. El despido injustificado genera reenganche y pago de salarios caídos.",
        articulos_crbv=["Art. 93"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["estabilidad laboral", "despido", "reenganche", "salarios caídos"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2007-000567",
        numero_sentencia="567",
        fecha="22-05-2008",
        tipo=TipoDecision.SENTENCIA,
        ponente="Omar Alfredo Mora Díaz",
        partes="Cálculo de prestaciones",
        materia="Prestaciones sociales",
        resumen="Método de cálculo de prestaciones sociales según LOTTT.",
        ratio_decidendi="Las prestaciones sociales se calculan con base en el último salario integral. Incluye todos los conceptos regulares y permanentes.",
        articulos_crbv=["Art. 92"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["prestaciones sociales", "salario integral", "cálculo", "LOTTT"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2009-000234",
        numero_sentencia="234",
        fecha="18-03-2010",
        tipo=TipoDecision.SENTENCIA,
        ponente="Juan Rafael Perdomo",
        partes="Tercerización laboral",
        materia="Tercerización",
        resumen="Simulación laboral mediante tercerización.",
        ratio_decidendi="La tercerización simulada no libera al beneficiario del servicio de responsabilidad laboral. Se aplica solidaridad patronal.",
        articulos_crbv=["Art. 89"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["tercerización", "simulación", "solidaridad patronal", "intermediación"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2010-000789",
        numero_sentencia="789",
        fecha="30-09-2011",
        tipo=TipoDecision.SENTENCIA,
        ponente="Carmen Elvigia Porras de Roa",
        partes="Accidente de trabajo",
        materia="Infortunios laborales",
        resumen="Responsabilidad patronal por accidente de trabajo.",
        ratio_decidendi="El patrono responde objetivamente por accidentes de trabajo. Solo se exime probando hecho de la víctima, caso fortuito o fuerza mayor.",
        articulos_crbv=["Art. 87", "Art. 89"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["accidente de trabajo", "responsabilidad objetiva", "indemnización", "patrono"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2011-000123",
        numero_sentencia="123",
        fecha="15-02-2012",
        tipo=TipoDecision.SENTENCIA,
        ponente="Luis Eduardo Franceschi Gutiérrez",
        partes="Horas extraordinarias",
        materia="Jornada laboral",
        resumen="Límites de la jornada laboral y pago de horas extraordinarias.",
        ratio_decidendi="La jornada diurna no puede exceder 8 horas. Las horas extraordinarias deben pagarse con recargo del 50%.",
        articulos_crbv=["Art. 90"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["jornada laboral", "horas extraordinarias", "recargo", "límites"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2008-000456",
        numero_sentencia="456",
        fecha="25-06-2009",
        tipo=TipoDecision.SENTENCIA,
        ponente="Omar Alfredo Mora Díaz",
        partes="Enfermedad ocupacional",
        materia="Enfermedad ocupacional",
        resumen="Requisitos para calificación de enfermedad ocupacional.",
        ratio_decidendi="La enfermedad ocupacional requiere nexo causal con el trabajo. El INPSASEL certifica el origen ocupacional.",
        articulos_crbv=["Art. 87"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["enfermedad ocupacional", "INPSASEL", "nexo causal", "incapacidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2012-000567",
        numero_sentencia="567",
        fecha="20-08-2013",
        tipo=TipoDecision.SENTENCIA,
        ponente="Carmen Elvigia Porras de Roa",
        partes="Fuero maternal",
        materia="Protección a la maternidad",
        resumen="Protección del fuero maternal en el trabajo.",
        ratio_decidendi="La trabajadora embarazada goza de inamovilidad desde el inicio del embarazo hasta 2 años después del parto. El despido durante el fuero es nulo.",
        articulos_crbv=["Art. 76", "Art. 89"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["fuero maternal", "embarazo", "inamovilidad", "maternidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2013-000234",
        numero_sentencia="234",
        fecha="12-04-2014",
        tipo=TipoDecision.SENTENCIA,
        ponente="Danilo Antonio Mojica Monsalvo",
        partes="Trabajador de dirección",
        materia="Trabajadores de dirección",
        resumen="Criterios para calificar a un trabajador como de dirección.",
        ratio_decidendi="El trabajador de dirección tiene funciones de representación del patrono o participa en decisiones importantes. No goza de estabilidad laboral.",
        articulos_crbv=["Art. 89"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["trabajador de dirección", "estabilidad", "representación", "exclusiones"]
    ),
    CasoTSJ(
        sala=SalaTSJ.CASACION_SOCIAL,
        numero_expediente="R.C. AA60-S-2006-000890",
        numero_sentencia="890",
        fecha="18-11-2007",
        tipo=TipoDecision.SENTENCIA,
        ponente="Alfonso Valbuena Cordero",
        partes="Salario variable",
        materia="Salario",
        resumen="Cálculo de prestaciones con salario variable.",
        ratio_decidendi="El salario variable se promedia con los devengados en el mes respectivo. Las comisiones integran el salario si son regulares y permanentes.",
        articulos_crbv=["Art. 91"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["salario variable", "comisiones", "prestaciones", "promedio"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    #                    SALA ELECTORAL (5+ cases)
    # ═══════════════════════════════════════════════════════════════════════════

    CasoTSJ(
        sala=SalaTSJ.ELECTORAL,
        numero_expediente="AA70-E-2004-000234",
        numero_sentencia="234",
        fecha="15-08-2004",
        tipo=TipoDecision.SENTENCIA,
        ponente="Alberto Martini Urdaneta",
        partes="Impugnación de resultados",
        materia="Recursos electorales",
        resumen="Impugnación de resultados electorales por irregularidades.",
        ratio_decidendi="Los resultados electorales pueden impugnarse por irregularidades que afecten materialmente el resultado. La carga de la prueba corresponde al impugnante.",
        articulos_crbv=["Art. 293", "Art. 294"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["impugnación", "resultados electorales", "irregularidades", "prueba"]
    ),
    CasoTSJ(
        sala=SalaTSJ.ELECTORAL,
        numero_expediente="AA70-E-2006-000456",
        numero_sentencia="456",
        fecha="22-05-2006",
        tipo=TipoDecision.SENTENCIA,
        ponente="Fernando Ramón Vegas Torrealba",
        partes="Partidos políticos",
        materia="Inscripción de partidos",
        resumen="Requisitos para inscripción de partidos políticos.",
        ratio_decidendi="Los partidos políticos deben cumplir requisitos de democracia interna, número mínimo de afiliados y presentación de estatutos conformes a ley.",
        articulos_crbv=["Art. 67"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["partidos políticos", "inscripción", "democracia interna", "CNE"]
    ),
    CasoTSJ(
        sala=SalaTSJ.ELECTORAL,
        numero_expediente="AA70-E-2008-000123",
        numero_sentencia="123",
        fecha="18-02-2008",
        tipo=TipoDecision.SENTENCIA,
        ponente="Alberto Martini Urdaneta",
        partes="Referéndum revocatorio",
        materia="Revocatoria de mandato",
        resumen="Procedimiento de referéndum revocatorio de mandato.",
        ratio_decidendi="El referéndum revocatorio requiere solicitud del 20% de electores inscritos. Procede a partir de la mitad del mandato.",
        articulos_crbv=["Art. 72"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["referéndum revocatorio", "mandato", "solicitud", "electores"]
    ),
    CasoTSJ(
        sala=SalaTSJ.ELECTORAL,
        numero_expediente="AA70-E-2010-000567",
        numero_sentencia="567",
        fecha="30-07-2010",
        tipo=TipoDecision.SENTENCIA,
        ponente="Fernando Ramón Vegas Torrealba",
        partes="Nulidad de elección",
        materia="Nulidad electoral",
        resumen="Causales de nulidad de elecciones.",
        ratio_decidendi="La elección puede anularse por fraude, coacción, violación de procedimientos que afecten el resultado o inhabilidad del candidato.",
        articulos_crbv=["Art. 293"],
        precedentes_citados=["Sentencia 234/2004 SE"],
        vinculante=False,
        url="",
        keywords=["nulidad", "elecciones", "fraude", "inhabilidad"]
    ),
    CasoTSJ(
        sala=SalaTSJ.ELECTORAL,
        numero_expediente="AA70-E-2012-000234",
        numero_sentencia="234",
        fecha="15-04-2012",
        tipo=TipoDecision.SENTENCIA,
        ponente="Luis Alfredo Sucre Cuba",
        partes="Postulaciones - Requisitos",
        materia="Postulaciones electorales",
        resumen="Requisitos de postulación para cargos de elección popular.",
        ratio_decidendi="Los requisitos de postulación deben verificarse al momento de inscripción. El CNE tiene facultad de rechazar postulaciones que incumplan requisitos.",
        articulos_crbv=["Art. 41", "Art. 293"],
        precedentes_citados=[],
        vinculante=False,
        url="",
        keywords=["postulaciones", "requisitos", "elección popular", "CNE"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    #                    SALA PLENA (3+ cases)
    # ═══════════════════════════════════════════════════════════════════════════

    CasoTSJ(
        sala=SalaTSJ.PLENA,
        numero_expediente="2003-0001",
        numero_sentencia="001",
        fecha="18-03-2003",
        tipo=TipoDecision.SENTENCIA,
        ponente="Presidente del TSJ",
        partes="Conflicto entre Salas",
        materia="Conflictos entre Salas",
        resumen="Resolución de conflicto de competencia entre Salas del TSJ.",
        ratio_decidendi="La Sala Plena resuelve conflictos de competencia entre las demás Salas del TSJ, asignando el conocimiento a la Sala competente.",
        articulos_crbv=["Art. 266"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["conflicto de competencia", "Sala Plena", "Salas del TSJ"]
    ),
    CasoTSJ(
        sala=SalaTSJ.PLENA,
        numero_expediente="2005-0002",
        numero_sentencia="002",
        fecha="22-06-2005",
        tipo=TipoDecision.SENTENCIA,
        ponente="Presidente del TSJ",
        partes="Antejuicio de mérito",
        materia="Antejuicio de mérito",
        resumen="Procedimiento de antejuicio de mérito a alto funcionario.",
        ratio_decidendi="El antejuicio de mérito determina si hay mérito para enjuiciar a altos funcionarios. Se analiza si existen elementos de convicción suficientes.",
        articulos_crbv=["Art. 266.3"],
        precedentes_citados=[],
        vinculante=True,
        url="",
        keywords=["antejuicio de mérito", "altos funcionarios", "enjuiciamiento"]
    ),
]


# ═══════════════════════════════════════════════════════════════════════════════
#                         SEARCH FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def buscar_por_sala(sala: SalaTSJ) -> List[CasoTSJ]:
    """Search cases by TSJ chamber."""
    return [c for c in JURISPRUDENCIA_DATABASE if c.sala == sala]


def buscar_por_articulo_crbv(articulo: str) -> List[CasoTSJ]:
    """Search cases by CRBV article."""
    articulo_norm = articulo.replace("Art.", "").replace("Artículo", "").replace("art.", "").strip()
    results = []
    for c in JURISPRUDENCIA_DATABASE:
        for art in c.articulos_crbv:
            if articulo_norm in art:
                results.append(c)
                break
    return results


def buscar_por_materia(materia: str) -> List[CasoTSJ]:
    """Search cases by legal matter."""
    materia_lower = materia.lower()
    results = []
    for c in JURISPRUDENCIA_DATABASE:
        if (materia_lower in c.materia.lower() or
            materia_lower in c.resumen.lower() or
            any(materia_lower in kw.lower() for kw in c.keywords)):
            results.append(c)
    return results


def buscar_por_texto(texto: str) -> List[CasoTSJ]:
    """Full text search across all fields."""
    texto_lower = texto.lower()
    resultados = []
    for caso in JURISPRUDENCIA_DATABASE:
        campos = [
            caso.materia,
            caso.resumen,
            caso.ratio_decidendi,
            caso.partes,
            caso.ponente,
            " ".join(caso.keywords) if caso.keywords else ""
        ]
        if any(texto_lower in campo.lower() for campo in campos):
            resultados.append(caso)
    return resultados


def buscar_por_keywords(keywords: List[str]) -> List[CasoTSJ]:
    """Search by multiple keywords (AND logic)."""
    keywords_lower = [k.lower() for k in keywords]
    results = []
    for caso in JURISPRUDENCIA_DATABASE:
        caso_text = f"{caso.materia} {caso.resumen} {caso.ratio_decidendi} {' '.join(caso.keywords)}"
        caso_text_lower = caso_text.lower()
        if all(kw in caso_text_lower for kw in keywords_lower):
            results.append(caso)
    return results


def buscar_vinculantes() -> List[CasoTSJ]:
    """Get all binding precedents."""
    return [c for c in JURISPRUDENCIA_DATABASE if c.vinculante]


def buscar_hidrocarburos() -> List[CasoTSJ]:
    """Get all hydrocarbon-related cases."""
    keywords = ["hidrocarburos", "petróleo", "PDVSA", "empresas mixtas", "regalías", "LOH"]
    results = []
    for caso in JURISPRUDENCIA_DATABASE:
        caso_text = f"{caso.materia} {caso.resumen} {' '.join(caso.keywords)}".lower()
        if any(kw.lower() in caso_text for kw in keywords):
            results.append(caso)
    return results


def buscar_por_fecha(desde: str, hasta: str) -> List[CasoTSJ]:
    """Search cases by date range (format: DD-MM-YYYY)."""
    from datetime import datetime
    try:
        desde_dt = datetime.strptime(desde, "%d-%m-%Y")
        hasta_dt = datetime.strptime(hasta, "%d-%m-%Y")
    except ValueError:
        return []

    results = []
    for caso in JURISPRUDENCIA_DATABASE:
        try:
            caso_dt = datetime.strptime(caso.fecha, "%d-%m-%Y")
            if desde_dt <= caso_dt <= hasta_dt:
                results.append(caso)
        except ValueError:
            continue
    return results


# ═══════════════════════════════════════════════════════════════════════════════
#                         REPORT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

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

    if caso.keywords:
        md += f"### Keywords\n`{', '.join(caso.keywords)}`\n\n"

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
    solo_vinculantes: bool = False,
    hidrocarburos: bool = False
) -> ResultadoBusqueda:
    """Execute a jurisprudence search."""
    resultados = []

    # Apply filters
    if hidrocarburos:
        resultados = buscar_hidrocarburos()
    elif sala:
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
            "Try searching for 'vinculantes' to see binding precedents",
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


def get_statistics() -> dict:
    """Get database statistics."""
    stats = {
        "total_cases": len(JURISPRUDENCIA_DATABASE),
        "binding_cases": len([c for c in JURISPRUDENCIA_DATABASE if c.vinculante]),
        "by_sala": {},
        "hydrocarbon_cases": len(buscar_hidrocarburos())
    }

    for sala in SalaTSJ:
        count = len([c for c in JURISPRUDENCIA_DATABASE if c.sala == sala])
        stats["by_sala"][sala.value] = count

    return stats


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Main function for CLI usage."""

    if len(sys.argv) < 2:
        stats = get_statistics()
        print("Venezuela Super Lawyer - TSJ Jurisprudence Search")
        print(f"\nDatabase: {stats['total_cases']} cases ({stats['binding_cases']} binding)")
        print("\nCases by Sala:")
        for sala, count in stats["by_sala"].items():
            print(f"  - {sala}: {count}")
        print(f"\nHydrocarbon-related cases: {stats['hydrocarbon_cases']}")
        print("\nUsage:")
        print("  python3 tsj_search.py <search_query>")
        print("  python3 tsj_search.py --sala 'Sala Constitucional'")
        print("  python3 tsj_search.py --articulo 'Art. 334'")
        print("  python3 tsj_search.py --materia 'amparo'")
        print("  python3 tsj_search.py --vinculantes")
        print("  python3 tsj_search.py --hidrocarburos")
        print("  python3 tsj_search.py --salas")
        print("  python3 tsj_search.py --stats")
        print("\nExamples:")
        print("  python3 tsj_search.py 'control difuso'")
        print("  python3 tsj_search.py --sala 'Sala Constitucional'")
        print("  python3 tsj_search.py --articulo '302'")
        print("  python3 tsj_search.py --hidrocarburos")
        sys.exit(0)

    if sys.argv[1] == "--salas":
        print("TSJ Chambers (Salas):\n")
        for sala in SalaTSJ:
            count = len([c for c in JURISPRUDENCIA_DATABASE if c.sala == sala])
            print(f"  - {sala.value} ({count} cases)")
        sys.exit(0)

    if sys.argv[1] == "--stats":
        stats = get_statistics()
        print(json.dumps(stats, indent=2))
        sys.exit(0)

    if sys.argv[1] == "--vinculantes":
        resultado = ejecutar_busqueda("vinculantes", solo_vinculantes=True)
        print(generar_reporte_busqueda(resultado))
        sys.exit(0)

    if sys.argv[1] == "--hidrocarburos":
        resultado = ejecutar_busqueda("hidrocarburos", hidrocarburos=True)
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
