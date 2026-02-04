#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Constitution Diff Engine
Compares proposed legislation against the Venezuelan Constitution (CRBV)
to identify potential conflicts, required amendments, and compliance issues.

CRBV: Constitución de la República Bolivariana de Venezuela (1999)
Published in Gaceta Oficial Extraordinaria N° 5.908 del 19 de febrero de 2009
(Enmienda N° 1)

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import sys
import json
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
#                         CONSTITUTIONAL FRAMEWORK
# ═══════════════════════════════════════════════════════════════════════════════

class ConflictSeverity(Enum):
    """Severity levels for constitutional conflicts."""
    CRITICAL = "Crítico"           # Direct violation of constitutional right
    HIGH = "Alto"                  # Significant conflict requiring amendment
    MEDIUM = "Medio"               # Potential conflict, interpretation needed
    LOW = "Bajo"                   # Minor concern, possible workaround
    INFO = "Informativo"           # FYI - related article but no conflict


class ConflictType(Enum):
    """Types of constitutional conflicts."""
    RIGHTS_VIOLATION = "Violación de Derechos"
    COMPETENCY_CONFLICT = "Conflicto de Competencias"
    PROCEDURAL_VIOLATION = "Violación Procedimental"
    ORGANIC_LAW_REQUIRED = "Requiere Ley Orgánica"
    RESERVED_TO_CONSTITUTION = "Materia Reservada a la Constitución"
    INTERNATIONAL_TREATY = "Conflicto con Tratado Internacional"
    ETERNITY_CLAUSE = "Cláusula Pétrea"
    SEPARATION_OF_POWERS = "Separación de Poderes"
    FEDERALISM = "Competencia Federal/Estadal/Municipal"
    RETROACTIVITY = "Principio de Irretroactividad"


class ConstitutionalArea(Enum):
    """Main areas of constitutional law."""
    DERECHOS_FUNDAMENTALES = "Derechos Fundamentales"
    DERECHOS_CIVILES = "Derechos Civiles"
    DERECHOS_POLITICOS = "Derechos Políticos"
    DERECHOS_SOCIALES = "Derechos Sociales y Familias"
    DERECHOS_CULTURALES = "Derechos Culturales y Educativos"
    DERECHOS_ECONOMICOS = "Derechos Económicos"
    DERECHOS_AMBIENTALES = "Derechos Ambientales"
    DERECHOS_PUEBLOS_INDIGENAS = "Derechos Pueblos Indígenas"
    PODER_PUBLICO = "Poder Público"
    PODER_LEGISLATIVO = "Poder Legislativo"
    PODER_EJECUTIVO = "Poder Ejecutivo"
    PODER_JUDICIAL = "Poder Judicial"
    PODER_CIUDADANO = "Poder Ciudadano"
    PODER_ELECTORAL = "Poder Electoral"
    SISTEMA_SOCIOECONOMICO = "Sistema Socioeconómico"
    SEGURIDAD_NACION = "Seguridad de la Nación"
    REFORMA_CONSTITUCIONAL = "Reforma Constitucional"


@dataclass
class ConstitutionalArticle:
    """Represents an article of the Constitution."""
    numero: int
    titulo: str
    capitulo: str
    contenido: str
    area: ConstitutionalArea
    keywords: List[str] = field(default_factory=list)
    related_articles: List[int] = field(default_factory=list)
    is_eternity_clause: bool = False
    requires_organic_law: bool = False


@dataclass
class ConflictAnalysis:
    """Represents a potential constitutional conflict."""
    articulo: int
    conflict_type: ConflictType
    severity: ConflictSeverity
    area: ConstitutionalArea
    descripcion: str
    texto_constitucional: str
    texto_propuesto: str
    recomendacion: str
    requires_amendment: bool = False
    amendment_type: Optional[str] = None  # "Enmienda", "Reforma", "Constituyente"


@dataclass
class DiffReport:
    """Complete constitutional diff report."""
    titulo_proyecto: str
    fecha_analisis: str
    resumen_ejecutivo: str
    total_conflicts: int
    conflicts_by_severity: Dict[str, int]
    conflicts_by_type: Dict[str, int]
    conflicts: List[ConflictAnalysis]
    related_articles: List[int]
    requires_constitutional_change: bool
    amendment_recommendation: Optional[str]
    risk_score: float  # 0.0 to 1.0
    compliance_percentage: float


# ═══════════════════════════════════════════════════════════════════════════════
#                         CONSTITUTIONAL DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

# Key constitutional articles with their metadata
# This is a curated selection of the most relevant articles for legal analysis
CONSTITUTIONAL_ARTICLES: Dict[int, ConstitutionalArticle] = {
    # ═══════════════════════════════════════════════════════════════════════════
    # TÍTULO I - PRINCIPIOS FUNDAMENTALES (Arts. 1-9)
    # ═══════════════════════════════════════════════════════════════════════════
    1: ConstitutionalArticle(
        numero=1,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="La República Bolivariana de Venezuela es irrevocablemente libre e independiente y fundamenta su patrimonio moral y sus valores de libertad, igualdad, justicia y paz internacional en la doctrina de Simón Bolívar, el Libertador. Son derechos irrenunciables de la Nación la independencia, la libertad, la soberanía, la inmunidad, la integridad territorial y la autodeterminación nacional.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["soberanía", "independencia", "libertad", "autodeterminación"],
        is_eternity_clause=True
    ),
    2: ConstitutionalArticle(
        numero=2,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="Venezuela se constituye en un Estado democrático y social de Derecho y de Justicia, que propugna como valores superiores de su ordenamiento jurídico y de su actuación, la vida, la libertad, la justicia, la igualdad, la solidaridad, la democracia, la responsabilidad social y, en general, la preeminencia de los derechos humanos, la ética y el pluralismo político.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["Estado de Derecho", "democracia", "derechos humanos", "justicia", "igualdad"],
        is_eternity_clause=True
    ),
    3: ConstitutionalArticle(
        numero=3,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="El Estado tiene como fines esenciales la defensa y el desarrollo de la persona y el respeto a su dignidad, el ejercicio democrático de la voluntad popular, la construcción de una sociedad justa y amante de la paz, la promoción de la prosperidad y bienestar del pueblo y la garantía del cumplimiento de los principios, derechos y deberes reconocidos y consagrados en esta Constitución. La educación y el trabajo son los procesos fundamentales para alcanzar dichos fines.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["dignidad", "democracia", "educación", "trabajo"],
        is_eternity_clause=True
    ),
    7: ConstitutionalArticle(
        numero=7,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="La Constitución es la norma suprema y el fundamento del ordenamiento jurídico. Todas las personas y los órganos que ejercen el Poder Público están sujetos a esta Constitución.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["supremacía constitucional", "jerarquía normativa"],
        is_eternity_clause=True
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # TÍTULO III - DERECHOS HUMANOS Y GARANTÍAS
    # ═══════════════════════════════════════════════════════════════════════════
    19: ConstitutionalArticle(
        numero=19,
        titulo="Derechos Humanos",
        capitulo="Disposiciones Generales",
        contenido="El Estado garantizará a toda persona, conforme al principio de progresividad y sin discriminación alguna, el goce y ejercicio irrenunciable, indivisible e interdependiente de los derechos humanos.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["progresividad", "no discriminación", "derechos humanos"],
        is_eternity_clause=True
    ),
    21: ConstitutionalArticle(
        numero=21,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Todas las personas son iguales ante la ley; en consecuencia: 1. No se permitirán discriminaciones fundadas en la raza, el sexo, el credo, la condición social o aquellas que, en general, tengan por objeto o por resultado anular o menoscabar el reconocimiento, goce o ejercicio en condiciones de igualdad, de los derechos y libertades de toda persona.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["igualdad", "no discriminación", "derechos civiles"]
    ),
    22: ConstitutionalArticle(
        numero=22,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="La enunciación de los derechos y garantías contenidos en esta Constitución y en los instrumentos internacionales sobre derechos humanos no debe entenderse como negación de otros que, siendo inherentes a la persona, no figuren expresamente en ellos. La falta de ley reglamentaria de estos derechos no menoscaba el ejercicio de los mismos.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["derechos innominados", "cláusula abierta", "derechos inherentes"]
    ),
    24: ConstitutionalArticle(
        numero=24,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Ninguna disposición legislativa tendrá efecto retroactivo, excepto cuando imponga menor pena. Las leyes de procedimiento se aplicarán desde el momento mismo de entrar en vigencia, aun en los procesos que se hallaren en curso; pero en los procesos penales, las pruebas ya evacuadas se estimarán en cuanto beneficien al reo o rea, conforme a la ley vigente para la fecha en que se promovieron.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["irretroactividad", "ley penal más favorable", "debido proceso"]
    ),
    25: ConstitutionalArticle(
        numero=25,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Todo acto dictado en ejercicio del Poder Público que viole o menoscabe los derechos garantizados por esta Constitución y la ley es nulo; y los funcionarios públicos y funcionarias públicas que lo ordenen o ejecuten incurren en responsabilidad penal, civil y administrativa, según los casos, sin que les sirvan de excusa órdenes superiores.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["nulidad", "responsabilidad", "derechos constitucionales"]
    ),
    26: ConstitutionalArticle(
        numero=26,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho de acceso a los órganos de administración de justicia para hacer valer sus derechos e intereses, incluso los colectivos o difusos; a la tutela efectiva de los mismos y a obtener con prontitud la decisión correspondiente.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["tutela judicial efectiva", "acceso a la justicia", "debido proceso"]
    ),
    27: ConstitutionalArticle(
        numero=27,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho a ser amparada por los tribunales en el goce y ejercicio de los derechos y garantías constitucionales, aun de aquellos inherentes a la persona que no figuren expresamente en esta Constitución o en los instrumentos internacionales sobre derechos humanos.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["amparo constitucional", "protección judicial", "derechos fundamentales"]
    ),
    43: ConstitutionalArticle(
        numero=43,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="El derecho a la vida es inviolable. Ninguna ley podrá establecer la pena de muerte, ni autoridad alguna aplicarla. El Estado protegerá la vida de las personas que se encuentren privadas de su libertad, prestando el servicio militar o civil, o sometidas a su autoridad en cualquier otra forma.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["derecho a la vida", "pena de muerte", "prohibición"],
        is_eternity_clause=True
    ),
    44: ConstitutionalArticle(
        numero=44,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="La libertad personal es inviolable, en consecuencia: 1. Ninguna persona puede ser arrestada o detenida sino en virtud de una orden judicial, a menos que sea sorprendida in fraganti.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libertad personal", "detención", "orden judicial", "flagrancia"]
    ),
    46: ConstitutionalArticle(
        numero=46,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho a que se respete su integridad física, psíquica y moral, en consecuencia: 1. Ninguna persona puede ser sometida a penas, torturas o tratos crueles, inhumanos o degradantes.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["integridad personal", "tortura", "tratos crueles"],
        is_eternity_clause=True
    ),
    49: ConstitutionalArticle(
        numero=49,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="El debido proceso se aplicará a todas las actuaciones judiciales y administrativas; en consecuencia: 1. La defensa y la asistencia jurídica son derechos inviolables en todo estado y grado de la investigación y del proceso. 2. Toda persona se presume inocente mientras no se pruebe lo contrario. 3. Toda persona tiene derecho a ser oída en cualquier clase de proceso.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["debido proceso", "derecho a la defensa", "presunción de inocencia", "derecho a ser oído"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # DERECHOS POLÍTICOS (Arts. 62-74)
    # ═══════════════════════════════════════════════════════════════════════════
    62: ConstitutionalArticle(
        numero=62,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Todos los ciudadanos y ciudadanas tienen el derecho de participar libremente en los asuntos públicos, directamente o por medio de sus representantes elegidos o elegidas.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["participación política", "democracia", "representación"]
    ),
    63: ConstitutionalArticle(
        numero=63,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="El sufragio es un derecho. Se ejercerá mediante votaciones libres, universales, directas y secretas. La ley garantizará el principio de la personalización del sufragio y la representación proporcional.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["sufragio", "voto", "elecciones", "representación proporcional"]
    ),
    70: ConstitutionalArticle(
        numero=70,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Son medios de participación y protagonismo del pueblo en ejercicio de su soberanía, en lo político: la elección de cargos públicos, el referendo, la consulta popular, la revocatoria del mandato, las iniciativas legislativa, constitucional y constituyente, el cabildo abierto y la asamblea de ciudadanos y ciudadanas cuyas decisiones serán de carácter vinculante.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["referendo", "consulta popular", "revocatoria", "iniciativa legislativa"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # DERECHOS SOCIALES Y DE LAS FAMILIAS (Arts. 75-97)
    # ═══════════════════════════════════════════════════════════════════════════
    83: ConstitutionalArticle(
        numero=83,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="La salud es un derecho social fundamental, obligación del Estado, que lo garantizará como parte del derecho a la vida. El Estado promoverá y desarrollará políticas orientadas a elevar la calidad de vida, el bienestar colectivo y el acceso a los servicios.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["salud", "derecho social", "calidad de vida"]
    ),
    87: ConstitutionalArticle(
        numero=87,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Toda persona tiene derecho al trabajo y el deber de trabajar. El Estado garantizará la adopción de las medidas necesarias a los fines de que toda persona pueda obtener ocupación productiva, que le proporcione una existencia digna y decorosa y le garantice el pleno ejercicio de este derecho.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["trabajo", "empleo", "ocupación productiva"]
    ),
    89: ConstitutionalArticle(
        numero=89,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="El trabajo es un hecho social y gozará de la protección del Estado. La ley dispondrá lo necesario para mejorar las condiciones materiales, morales e intelectuales de los trabajadores y trabajadoras.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["protección laboral", "condiciones de trabajo"],
        requires_organic_law=True
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # DERECHOS ECONÓMICOS (Arts. 112-118)
    # ═══════════════════════════════════════════════════════════════════════════
    112: ConstitutionalArticle(
        numero=112,
        titulo="Derechos Económicos",
        capitulo="De los Derechos Económicos",
        contenido="Todas las personas pueden dedicarse libremente a la actividad económica de su preferencia, sin más limitaciones que las previstas en esta Constitución y las que establezcan las leyes, por razones de desarrollo humano, seguridad, sanidad, protección del ambiente u otras de interés social.",
        area=ConstitutionalArea.DERECHOS_ECONOMICOS,
        keywords=["libertad económica", "libre empresa", "limitaciones"]
    ),
    113: ConstitutionalArticle(
        numero=113,
        titulo="Derechos Económicos",
        capitulo="De los Derechos Económicos",
        contenido="No se permitirán monopolios. Se declaran contrarios a los principios fundamentales de esta Constitución cualesquier acto, actividad, conducta o acuerdo de los y las particulares que tengan por objeto el establecimiento de un monopolio.",
        area=ConstitutionalArea.DERECHOS_ECONOMICOS,
        keywords=["monopolio", "competencia", "prohibición"]
    ),
    115: ConstitutionalArticle(
        numero=115,
        titulo="Derechos Económicos",
        capitulo="De los Derechos Económicos",
        contenido="Se garantiza el derecho de propiedad. Toda persona tiene derecho al uso, goce, disfrute y disposición de sus bienes. La propiedad estará sometida a las contribuciones, restricciones y obligaciones que establezca la ley con fines de utilidad pública o de interés general.",
        area=ConstitutionalArea.DERECHOS_ECONOMICOS,
        keywords=["propiedad", "expropiación", "utilidad pública"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # SISTEMA SOCIOECONÓMICO (Arts. 299-321)
    # ═══════════════════════════════════════════════════════════════════════════
    299: ConstitutionalArticle(
        numero=299,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico y de la Función del Estado",
        contenido="El régimen socioeconómico de la República Bolivariana de Venezuela se fundamenta en los principios de justicia social, democracia, eficiencia, libre competencia, protección del ambiente, productividad y solidaridad, a los fines de asegurar el desarrollo humano integral y una existencia digna y provechosa para la colectividad.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["régimen económico", "justicia social", "libre competencia"]
    ),
    302: ConstitutionalArticle(
        numero=302,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico y de la Función del Estado",
        contenido="El Estado se reserva, mediante la ley orgánica respectiva, y por razones de conveniencia nacional, la actividad petrolera y otras industrias, explotaciones, servicios y bienes de interés público y de carácter estratégico.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["hidrocarburos", "petróleo", "reserva estatal", "industria estratégica"],
        requires_organic_law=True
    ),
    303: ConstitutionalArticle(
        numero=303,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico y de la Función del Estado",
        contenido="Por razones de soberanía económica, política y de estrategia nacional, el Estado conservará la totalidad de las acciones de Petróleos de Venezuela, S.A., o del ente creado para el manejo de la industria petrolera, exceptuando las de las filiales, asociaciones estratégicas, empresas y cualquier otra que se haya constituido o se constituya como consecuencia del desarrollo de negocios de Petróleos de Venezuela, S.A.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["PDVSA", "petróleo", "soberanía", "propiedad estatal"],
        is_eternity_clause=True
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # PODER PÚBLICO (Arts. 136-185)
    # ═══════════════════════════════════════════════════════════════════════════
    136: ConstitutionalArticle(
        numero=136,
        titulo="Poder Público",
        capitulo="Disposiciones Fundamentales",
        contenido="El Poder Público se distribuye entre el Poder Municipal, el Poder Estadal y el Poder Nacional. El Poder Público Nacional se divide en Legislativo, Ejecutivo, Judicial, Ciudadano y Electoral.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["separación de poderes", "poder público", "distribución territorial"]
    ),
    137: ConstitutionalArticle(
        numero=137,
        titulo="Poder Público",
        capitulo="Disposiciones Fundamentales",
        contenido="La Constitución y la ley definirán las atribuciones de los órganos que ejercen el Poder Público, a las cuales deben sujetarse las actividades que realicen.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["principio de legalidad", "competencias", "atribuciones"]
    ),
    156: ConstitutionalArticle(
        numero=156,
        titulo="Poder Público Nacional",
        capitulo="De la Competencia del Poder Público Nacional",
        contenido="Es de la competencia del Poder Público Nacional: [lista de 33 competencias exclusivas incluyendo] 16. El régimen y administración de las minas e hidrocarburos; el régimen de las tierras baldías; y la conservación, fomento y aprovechamiento de los bosques, suelos, aguas y otras riquezas naturales del país.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["competencia nacional", "minas", "hidrocarburos", "recursos naturales"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # PODER LEGISLATIVO (Arts. 186-224)
    # ═══════════════════════════════════════════════════════════════════════════
    187: ConstitutionalArticle(
        numero=187,
        titulo="Poder Legislativo",
        capitulo="De la Asamblea Nacional",
        contenido="Corresponde a la Asamblea Nacional: 1. Legislar en las materias de la competencia nacional y sobre el funcionamiento de las distintas ramas del Poder Nacional.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["función legislativa", "Asamblea Nacional", "leyes"],
        requires_organic_law=True
    ),
    202: ConstitutionalArticle(
        numero=202,
        titulo="Poder Legislativo",
        capitulo="De la Formación de las Leyes",
        contenido="La ley es el acto sancionado por la Asamblea Nacional como cuerpo legislador. Las leyes que reúnan sistemáticamente las normas relativas a determinada materia se podrán denominar códigos.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["ley", "código", "sanción legislativa"]
    ),
    203: ConstitutionalArticle(
        numero=203,
        titulo="Poder Legislativo",
        capitulo="De la Formación de las Leyes",
        contenido="Son leyes orgánicas las que así denomina esta Constitución; las que se dicten para organizar los poderes públicos o para desarrollar los derechos constitucionales y las que sirvan de marco normativo a otras leyes.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["ley orgánica", "desarrollo constitucional", "marco normativo"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # REFORMA CONSTITUCIONAL (Arts. 340-350)
    # ═══════════════════════════════════════════════════════════════════════════
    340: ConstitutionalArticle(
        numero=340,
        titulo="Reforma Constitucional",
        capitulo="De las Enmiendas",
        contenido="La enmienda tiene por objeto la adición o modificación de uno o varios artículos de esta Constitución, sin alterar su estructura fundamental.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["enmienda", "modificación constitucional"]
    ),
    342: ConstitutionalArticle(
        numero=342,
        titulo="Reforma Constitucional",
        capitulo="De la Reforma Constitucional",
        contenido="La Reforma Constitucional tiene por objeto una revisión parcial de esta Constitución y la sustitución de una o varias de sus normas que no modifiquen la estructura y principios fundamentales del texto Constitucional.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["reforma constitucional", "revisión parcial"]
    ),
    347: ConstitutionalArticle(
        numero=347,
        titulo="Reforma Constitucional",
        capitulo="De la Asamblea Nacional Constituyente",
        contenido="El pueblo de Venezuela es el depositario del poder constituyente originario. En ejercicio de dicho poder, puede convocar una Asamblea Nacional Constituyente con el objeto de transformar el Estado, crear un nuevo ordenamiento jurídico y redactar una nueva Constitución.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["poder constituyente", "Asamblea Constituyente", "nueva Constitución"]
    ),
    350: ConstitutionalArticle(
        numero=350,
        titulo="Reforma Constitucional",
        capitulo="De la Asamblea Nacional Constituyente",
        contenido="El pueblo de Venezuela, fiel a su tradición republicana, a su lucha por la independencia, la paz y la libertad, desconocerá cualquier régimen, legislación o autoridad que contraríe los valores, principios y garantías democráticos o menoscabe los derechos humanos.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["desobediencia", "valores democráticos", "derechos humanos"],
        is_eternity_clause=True
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL FUNDAMENTAL PRINCIPLES (Arts. 4-9)
    # ═══════════════════════════════════════════════════════════════════════════
    4: ConstitutionalArticle(
        numero=4,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="La República Bolivariana de Venezuela es un Estado Federal descentralizado en los términos consagrados en esta Constitución, y se rige por los principios de integridad territorial, cooperación, solidaridad, concurrencia y corresponsabilidad.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["federalismo", "descentralización", "integridad territorial"],
        is_eternity_clause=True
    ),
    5: ConstitutionalArticle(
        numero=5,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="La soberanía reside intransferiblemente en el pueblo, quien la ejerce directamente en la forma prevista en esta Constitución y en la ley, e indirectamente, mediante el sufragio, por los órganos que ejercen el Poder Público. Los órganos del Estado emanan de la soberanía popular y a ella están sometidos.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["soberanía popular", "sufragio", "poder público"],
        is_eternity_clause=True
    ),
    6: ConstitutionalArticle(
        numero=6,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="El gobierno de la República Bolivariana de Venezuela y de las entidades políticas que la componen es y será siempre democrático, participativo, electivo, descentralizado, alternativo, responsable, pluralista y de mandatos revocables.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["democracia", "participación", "alternabilidad", "revocatoria"],
        is_eternity_clause=True
    ),
    8: ConstitutionalArticle(
        numero=8,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="La bandera nacional con los colores amarillo, azul y rojo; el himno nacional Gloria al bravo pueblo y el escudo de armas de la República son los símbolos de la patria. La ley regulará sus características, significados y usos.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["símbolos patrios", "bandera", "himno", "escudo"]
    ),
    9: ConstitutionalArticle(
        numero=9,
        titulo="Principios Fundamentales",
        capitulo="Disposiciones Fundamentales",
        contenido="El idioma oficial es el castellano. Los idiomas indígenas también son de uso oficial para los pueblos indígenas y deben ser respetados en todo el territorio de la República, por constituir patrimonio cultural de la Nación y de la humanidad.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["idioma oficial", "castellano", "idiomas indígenas", "patrimonio cultural"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # TÍTULO II - DEL ESPACIO GEOGRÁFICO (Arts. 10-18)
    # ═══════════════════════════════════════════════════════════════════════════
    10: ConstitutionalArticle(
        numero=10,
        titulo="Del Espacio Geográfico",
        capitulo="Del Territorio y demás Espacios Geográficos",
        contenido="El territorio y demás espacios geográficos de la República son los que correspondían a la Capitanía General de Venezuela antes de la transformación política iniciada el 19 de abril de 1810, con las modificaciones resultantes de los tratados y laudos arbitrales no viciados de nulidad.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["territorio", "espacio geográfico", "Capitanía General"]
    ),
    11: ConstitutionalArticle(
        numero=11,
        titulo="Del Espacio Geográfico",
        capitulo="Del Territorio y demás Espacios Geográficos",
        contenido="La soberanía plena de la República se ejerce en los espacios continental e insular, lacustre y fluvial, mar territorial, áreas marinas interiores, históricas y vitales y las comprendidas dentro de las líneas de base rectas que ha adoptado o adopte la República.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["soberanía territorial", "mar territorial", "espacio aéreo"]
    ),
    13: ConstitutionalArticle(
        numero=13,
        titulo="Del Espacio Geográfico",
        capitulo="Del Territorio y demás Espacios Geográficos",
        contenido="El territorio no podrá ser jamás cedido, traspasado, arrendado, ni en forma alguna enajenado, ni aun temporal o parcialmente, a Estados extranjeros u otros sujetos de derecho internacional.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["integridad territorial", "inalienabilidad", "soberanía"],
        is_eternity_clause=True
    ),
    14: ConstitutionalArticle(
        numero=14,
        titulo="Del Espacio Geográfico",
        capitulo="De la División Política",
        contenido="La ley establecerá un régimen jurídico especial para aquellos territorios que por libre determinación de sus habitantes y con aceptación de la Asamblea Nacional, se incorporen al de la República.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["incorporación territorial", "autodeterminación"]
    ),
    15: ConstitutionalArticle(
        numero=15,
        titulo="Del Espacio Geográfico",
        capitulo="De la División Política",
        contenido="El Estado tiene la responsabilidad de establecer una política integral en los espacios fronterizos terrestres, insulares y marítimos, preservando la integridad territorial, la soberanía, la seguridad, la defensa, la identidad nacional, la diversidad y el ambiente.",
        area=ConstitutionalArea.DERECHOS_FUNDAMENTALES,
        keywords=["fronteras", "seguridad fronteriza", "integridad territorial"]
    ),
    16: ConstitutionalArticle(
        numero=16,
        titulo="Del Espacio Geográfico",
        capitulo="De la División Política",
        contenido="Con el fin de organizar políticamente la República, el territorio nacional se divide en el de los Estados, el del Distrito Capital, el de las dependencias federales y el de los territorios federales. El territorio se organiza en Municipios.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["división política", "estados", "municipios", "Distrito Capital"]
    ),
    17: ConstitutionalArticle(
        numero=17,
        titulo="Del Espacio Geográfico",
        capitulo="De la División Política",
        contenido="Las dependencias federales son las islas marítimas no integradas en el territorio de un Estado, así como las islas que se formen o aparezcan en el mar territorial o en el que cubra la plataforma continental. Su régimen y administración estarán señalados en la ley.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["dependencias federales", "islas", "plataforma continental"]
    ),
    18: ConstitutionalArticle(
        numero=18,
        titulo="Del Espacio Geográfico",
        capitulo="De la División Política",
        contenido="La ciudad de Caracas es la capital de la República y el asiento de los órganos del Poder Nacional. Lo dispuesto en este artículo no impide el ejercicio del Poder Nacional en otros lugares de la República.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["Caracas", "capital", "sede del gobierno"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL CIVIL RIGHTS (Arts. 28-60)
    # ═══════════════════════════════════════════════════════════════════════════
    20: ConstitutionalArticle(
        numero=20,
        titulo="Derechos Civiles",
        capitulo="Disposiciones Generales",
        contenido="Toda persona tiene derecho al libre desenvolvimiento de su personalidad, sin más limitaciones que las que derivan del derecho de las demás y del orden público y social.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libre desarrollo", "personalidad", "limitaciones"]
    ),
    23: ConstitutionalArticle(
        numero=23,
        titulo="Derechos Civiles",
        capitulo="Disposiciones Generales",
        contenido="Los tratados, pactos y convenciones relativos a derechos humanos, suscritos y ratificados por Venezuela, tienen jerarquía constitucional y prevalecen en el orden interno, en la medida en que contengan normas sobre su goce y ejercicio más favorables a las establecidas en esta Constitución.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["tratados internacionales", "derechos humanos", "jerarquía constitucional", "pro homine"],
        is_eternity_clause=True
    ),
    28: ConstitutionalArticle(
        numero=28,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho de acceder a la información y a los datos que sobre sí misma o sobre sus bienes consten en registros oficiales o privados, así como de conocer el uso que se haga de los mismos y su finalidad.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["habeas data", "protección de datos", "información personal"]
    ),
    29: ConstitutionalArticle(
        numero=29,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="El Estado estará obligado a investigar y sancionar legalmente los delitos contra los derechos humanos cometidos por sus autoridades. Las acciones para sancionar los delitos de lesa humanidad, violaciones graves de los derechos humanos y los crímenes de guerra son imprescriptibles.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["imprescriptibilidad", "lesa humanidad", "crímenes de guerra"],
        is_eternity_clause=True
    ),
    30: ConstitutionalArticle(
        numero=30,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="El Estado tendrá la obligación de indemnizar integralmente a las víctimas de violaciones de los derechos humanos que le sean imputables, o a sus derechohabientes, incluido el pago de daños y perjuicios.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["indemnización", "víctimas", "responsabilidad del Estado"]
    ),
    31: ConstitutionalArticle(
        numero=31,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho, en los términos establecidos por los tratados, pactos y convenciones sobre derechos humanos ratificados por la República, a dirigir peticiones o quejas ante los órganos internacionales creados para tales fines.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["órganos internacionales", "peticiones", "CIDH", "Corte IDH"]
    ),
    45: ConstitutionalArticle(
        numero=45,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Se prohíbe a la autoridad pública, sea civil o militar, aun en estado de emergencia, excepción o restricción de garantías, practicar, permitir o tolerar la desaparición forzada de personas.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["desaparición forzada", "prohibición absoluta"],
        is_eternity_clause=True
    ),
    47: ConstitutionalArticle(
        numero=47,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="El hogar doméstico y todo recinto privado de persona son inviolables. No podrán ser allanados sino mediante orden judicial, para impedir la perpetración de un delito o para cumplir, de acuerdo con la ley, las decisiones que dicten los tribunales.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["inviolabilidad del hogar", "allanamiento", "orden judicial"]
    ),
    48: ConstitutionalArticle(
        numero=48,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Se garantiza el secreto e inviolabilidad de las comunicaciones privadas en todas sus formas. No podrán ser interferidas sino por orden de un tribunal competente, con el cumplimiento de las disposiciones legales y preservándose el secreto de lo privado.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["secreto de comunicaciones", "privacidad", "intervención telefónica"]
    ),
    50: ConstitutionalArticle(
        numero=50,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona puede transitar libremente y por cualquier medio por el territorio nacional, cambiar de domicilio y residencia, ausentarse de la República y volver, trasladar sus bienes y pertenencias en el país.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libre tránsito", "libertad de movimiento", "domicilio"]
    ),
    51: ConstitutionalArticle(
        numero=51,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene el derecho de representar o dirigir peticiones ante cualquier autoridad, funcionario público o funcionaria pública sobre los asuntos que sean de la competencia de éstos o éstas, y de obtener oportuna y adecuada respuesta.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["derecho de petición", "respuesta oportuna"]
    ),
    52: ConstitutionalArticle(
        numero=52,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho de asociarse con fines lícitos, de conformidad con la ley. El Estado estará obligado a facilitar el ejercicio de este derecho.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libertad de asociación", "asociaciones"]
    ),
    53: ConstitutionalArticle(
        numero=53,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene el derecho de reunirse, pública o privadamente, sin permiso previo, con fines lícitos y sin armas. Las reuniones en lugares públicos se regirán por la ley.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libertad de reunión", "manifestación", "reuniones públicas"]
    ),
    54: ConstitutionalArticle(
        numero=54,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Ninguna persona podrá ser sometida a esclavitud o servidumbre. La trata de personas y, en particular, la de mujeres, niños, niñas y adolescentes en todas sus formas, estará sujeta a las penas previstas en la ley.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["esclavitud", "servidumbre", "trata de personas"],
        is_eternity_clause=True
    ),
    55: ConstitutionalArticle(
        numero=55,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho a la protección por parte del Estado, a través de los órganos de seguridad ciudadana regulados por ley, frente a situaciones que constituyan amenaza, vulnerabilidad o riesgo para la integridad física de las personas.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["seguridad ciudadana", "protección", "integridad física"]
    ),
    56: ConstitutionalArticle(
        numero=56,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho a un nombre propio, al apellido del padre y al de la madre, y a conocer la identidad de los mismos. El Estado garantizará el derecho a investigar la maternidad y la paternidad.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["derecho al nombre", "identidad", "filiación"]
    ),
    57: ConstitutionalArticle(
        numero=57,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho a expresar libremente sus pensamientos, sus ideas u opiniones de viva voz, por escrito o mediante cualquier otra forma de expresión y de hacer uso para ello de cualquier medio de comunicación y difusión, sin que pueda establecerse censura.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libertad de expresión", "libertad de prensa", "censura"]
    ),
    58: ConstitutionalArticle(
        numero=58,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="La comunicación es libre y plural y comporta los deberes y responsabilidades que indique la ley. Toda persona tiene derecho a la información oportuna, veraz e imparcial, sin censura, de acuerdo con los principios de esta Constitución.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["derecho a la información", "comunicación", "veracidad"]
    ),
    59: ConstitutionalArticle(
        numero=59,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="El Estado garantizará la libertad de religión y de culto. Toda persona tiene derecho a profesar su fe religiosa y cultos y a manifestar sus creencias en privado o en público.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libertad religiosa", "libertad de culto", "creencias"]
    ),
    60: ConstitutionalArticle(
        numero=60,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho a la protección de su honor, vida privada, intimidad, propia imagen, confidencialidad y reputación. La ley limitará el uso de la informática para garantizar el honor y la intimidad personal y familiar.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["honor", "intimidad", "privacidad", "protección de datos"]
    ),
    61: ConstitutionalArticle(
        numero=61,
        titulo="Derechos Civiles",
        capitulo="De los Derechos Civiles",
        contenido="Toda persona tiene derecho a la libertad de conciencia y a manifestarla, salvo que su práctica afecte la personalidad o constituya delito. La objeción de conciencia no puede invocarse para eludir el cumplimiento de la ley o impedir a otros su cumplimiento.",
        area=ConstitutionalArea.DERECHOS_CIVILES,
        keywords=["libertad de conciencia", "objeción de conciencia"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL POLITICAL RIGHTS (Arts. 64-74)
    # ═══════════════════════════════════════════════════════════════════════════
    64: ConstitutionalArticle(
        numero=64,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Son electores o electoras todos los venezolanos y venezolanas que hayan cumplido dieciocho años de edad y que no estén sujetos a interdicción civil o inhabilitación política.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["derecho al voto", "electores", "mayoría de edad"]
    ),
    65: ConstitutionalArticle(
        numero=65,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="No podrán optar a cargo alguno de elección popular quienes hayan sido condenados o condenadas por delitos cometidos durante el ejercicio de sus funciones y otros que afecten el patrimonio público, dentro del tiempo que fije la ley.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["inhabilitación política", "corrupción", "patrimonio público"]
    ),
    66: ConstitutionalArticle(
        numero=66,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Los electores y electoras tienen derecho a que sus representantes rindan cuentas públicas, transparentes y periódicas sobre su gestión, de acuerdo con el programa presentado.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["rendición de cuentas", "transparencia", "gestión pública"]
    ),
    67: ConstitutionalArticle(
        numero=67,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Todos los ciudadanos y ciudadanas tienen el derecho de asociarse con fines políticos, mediante métodos democráticos de organización, funcionamiento y dirección. Sus organismos de dirección y sus candidatos o candidatas a cargos de elección popular serán seleccionados en elecciones internas con la participación de sus integrantes.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["partidos políticos", "asociación política", "democracia interna"]
    ),
    68: ConstitutionalArticle(
        numero=68,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Los ciudadanos y ciudadanas tienen derecho a manifestar, pacíficamente y sin armas, sin otros requisitos que los que establezca la ley. Se prohíbe el uso de armas de fuego y sustancias tóxicas en el control de manifestaciones pacíficas.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["manifestación", "protesta pacífica", "uso de armas"]
    ),
    69: ConstitutionalArticle(
        numero=69,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="La República Bolivariana de Venezuela reconoce y garantiza el derecho de asilo y refugio. Se prohíbe la extradición de venezolanos y venezolanas.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["asilo", "refugio", "extradición"]
    ),
    71: ConstitutionalArticle(
        numero=71,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Las materias de especial trascendencia nacional podrán ser sometidas a referendo consultivo por iniciativa del Presidente de la República en Consejo de Ministros; por acuerdo de la Asamblea Nacional aprobado por el voto de la mayoría de sus integrantes; o a solicitud de un número no menor del diez por ciento de los electores.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["referendo consultivo", "democracia directa", "consulta popular"]
    ),
    72: ConstitutionalArticle(
        numero=72,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Todos los cargos y magistraturas de elección popular son revocables. Transcurrida la mitad del período para el cual fue elegido el funcionario o funcionaria, un número no menor del veinte por ciento de los electores inscritos podrá solicitar la convocatoria de un referendo para revocar su mandato.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["revocatoria de mandato", "referendo revocatorio", "control popular"]
    ),
    73: ConstitutionalArticle(
        numero=73,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Serán sometidos a referendo aquellos proyectos de ley en discusión por la Asamblea Nacional, cuando así lo decidan por lo menos las dos terceras partes de los integrantes de la Asamblea.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["referendo legislativo", "democracia directa"]
    ),
    74: ConstitutionalArticle(
        numero=74,
        titulo="Derechos Políticos",
        capitulo="De los Derechos Políticos",
        contenido="Serán sometidos a referendo, para ser abrogados total o parcialmente, los decretos con fuerza de ley que dicte el Presidente de la República en uso de la atribución prescrita en el numeral 8 del artículo 236 de esta Constitución, cuando fuere solicitado por un número no menor del cinco por ciento de los electores.",
        area=ConstitutionalArea.DERECHOS_POLITICOS,
        keywords=["referendo abrogatorio", "decretos ley", "control popular"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL SOCIAL RIGHTS (Arts. 75-97)
    # ═══════════════════════════════════════════════════════════════════════════
    75: ConstitutionalArticle(
        numero=75,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="El Estado protegerá a las familias como asociación natural de la sociedad y como el espacio fundamental para el desarrollo integral de las personas. Las relaciones familiares se basan en la igualdad de derechos y deberes, la solidaridad, el esfuerzo común, la comprensión mutua y el respeto recíproco entre sus integrantes.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["familia", "protección familiar", "desarrollo integral"]
    ),
    76: ConstitutionalArticle(
        numero=76,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="La maternidad y la paternidad son protegidas integralmente, sea cual fuere el estado civil de la madre o del padre. Las parejas tienen derecho a decidir libre y responsablemente el número de hijos o hijas que deseen concebir.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["maternidad", "paternidad", "planificación familiar"]
    ),
    77: ConstitutionalArticle(
        numero=77,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Se protege el matrimonio entre un hombre y una mujer, fundado en el libre consentimiento y en la igualdad absoluta de los derechos y deberes de los cónyuges. Las uniones estables de hecho entre un hombre y una mujer que cumplan los requisitos establecidos en la ley producirán los mismos efectos que el matrimonio.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["matrimonio", "uniones de hecho", "cónyuges"]
    ),
    78: ConstitutionalArticle(
        numero=78,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Los niños, niñas y adolescentes son sujetos plenos de derecho y estarán protegidos por la legislación, órganos y tribunales especializados, los cuales respetarán, garantizarán y desarrollarán los contenidos de esta Constitución, la Convención sobre los Derechos del Niño y demás tratados internacionales.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["niños", "adolescentes", "protección especial", "interés superior"],
        requires_organic_law=True
    ),
    79: ConstitutionalArticle(
        numero=79,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Los jóvenes y las jóvenes tienen el derecho y el deber de ser sujetos activos del proceso de desarrollo. El Estado, con la participación solidaria de las familias y la sociedad, creará oportunidades para estimular su tránsito productivo hacia la vida adulta.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["juventud", "desarrollo", "participación"]
    ),
    80: ConstitutionalArticle(
        numero=80,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="El Estado garantizará a los ancianos y ancianas el pleno ejercicio de sus derechos y garantías. El Estado, con la participación solidaria de las familias y la sociedad, está obligado a respetar su dignidad humana, su autonomía y les garantizará atención integral y los beneficios de la seguridad social.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["ancianos", "tercera edad", "seguridad social"]
    ),
    81: ConstitutionalArticle(
        numero=81,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Toda persona con discapacidad o necesidades especiales tiene derecho al ejercicio pleno y autónomo de sus capacidades y a su integración familiar y comunitaria. El Estado, con la participación solidaria de las familias y la sociedad, les garantizará el respeto a su dignidad humana.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["discapacidad", "necesidades especiales", "integración"]
    ),
    82: ConstitutionalArticle(
        numero=82,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Toda persona tiene derecho a una vivienda adecuada, segura, cómoda, higiénica, con servicios básicos esenciales que incluyan un hábitat que humanice las relaciones familiares, vecinales y comunitarias.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["vivienda", "hábitat", "servicios básicos"]
    ),
    84: ConstitutionalArticle(
        numero=84,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Para garantizar el derecho a la salud, el Estado creará, ejercerá la rectoría y gestionará un sistema público nacional de salud, de carácter intersectorial, descentralizado y participativo, integrado al sistema de seguridad social, regido por los principios de gratuidad, universalidad, integralidad, equidad, integración social y solidaridad.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["sistema de salud", "gratuidad", "universalidad"]
    ),
    85: ConstitutionalArticle(
        numero=85,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="El financiamiento del sistema público nacional de salud es obligación del Estado, que integrará los recursos fiscales, las cotizaciones obligatorias de la seguridad social y cualquier otra fuente de financiamiento que determine la ley.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["financiamiento salud", "seguridad social"]
    ),
    86: ConstitutionalArticle(
        numero=86,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Toda persona tiene derecho a la seguridad social como servicio público de carácter no lucrativo, que garantice la salud y asegure protección en contingencias de maternidad, paternidad, enfermedad, invalidez, enfermedades catastróficas, discapacidad, necesidades especiales, riesgos laborales, pérdida de empleo, desempleo, vejez, viudedad, orfandad, vivienda, cargas derivadas de la vida familiar.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["seguridad social", "pensiones", "protección social"],
        requires_organic_law=True
    ),
    88: ConstitutionalArticle(
        numero=88,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="El Estado garantizará la igualdad y equidad de hombres y mujeres en el ejercicio del derecho al trabajo. El Estado reconocerá el trabajo del hogar como actividad económica que crea valor agregado y produce riqueza y bienestar social. Las amas de casa tienen derecho a la seguridad social de conformidad con la ley.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["igualdad laboral", "trabajo del hogar", "amas de casa"]
    ),
    90: ConstitutionalArticle(
        numero=90,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="La jornada de trabajo diurna no excederá de ocho horas diarias ni de cuarenta y cuatro horas semanales. En los casos en que la ley lo permita, la jornada de trabajo nocturna no excederá de siete horas diarias ni de treinta y cinco semanales. Ningún patrono podrá obligar a los trabajadores a laborar horas extraordinarias.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["jornada laboral", "horas de trabajo", "horas extraordinarias"]
    ),
    91: ConstitutionalArticle(
        numero=91,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Todo trabajador o trabajadora tiene derecho a un salario suficiente que le permita vivir con dignidad y cubrir para sí y su familia las necesidades básicas materiales, sociales e intelectuales. Se garantizará el pago de igual salario por igual trabajo.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["salario", "remuneración", "salario mínimo", "igualdad salarial"]
    ),
    92: ConstitutionalArticle(
        numero=92,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Todos los trabajadores y trabajadoras tienen derecho a prestaciones sociales que les recompensen la antigüedad en el servicio y los amparen en caso de cesantía. El salario y las prestaciones sociales son créditos laborales de exigibilidad inmediata.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["prestaciones sociales", "antigüedad", "cesantía"]
    ),
    93: ConstitutionalArticle(
        numero=93,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="La ley garantizará la estabilidad en el trabajo y dispondrá lo conducente para limitar toda forma de despido no justificado. Los despidos contrarios a esta Constitución son nulos.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["estabilidad laboral", "despido", "inamovilidad"]
    ),
    95: ConstitutionalArticle(
        numero=95,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Los trabajadores y las trabajadoras, sin distinción alguna y sin necesidad de autorización previa, tienen derecho a constituir libremente las organizaciones sindicales que estimen convenientes para la mejor defensa de sus derechos e intereses, así como a afiliarse o no a ellas, de conformidad con la Ley.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["sindicatos", "libertad sindical", "organización"]
    ),
    96: ConstitutionalArticle(
        numero=96,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Todos los trabajadores y las trabajadoras del sector público y del privado tienen derecho a la negociación colectiva voluntaria y a celebrar convenciones colectivas de trabajo, sin más requisitos que los que establezca la ley.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["negociación colectiva", "convención colectiva"]
    ),
    97: ConstitutionalArticle(
        numero=97,
        titulo="Derechos Sociales",
        capitulo="De los Derechos Sociales y de las Familias",
        contenido="Todos los trabajadores y trabajadoras del sector público y del privado tienen derecho a la huelga, dentro de las condiciones que establezca la ley.",
        area=ConstitutionalArea.DERECHOS_SOCIALES,
        keywords=["huelga", "derecho de huelga", "conflicto colectivo"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # CULTURAL AND EDUCATIONAL RIGHTS (Arts. 98-111)
    # ═══════════════════════════════════════════════════════════════════════════
    98: ConstitutionalArticle(
        numero=98,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="La creación cultural es libre. Esta libertad comprende el derecho a la inversión, producción y divulgación de la obra creativa, científica, tecnológica y humanística, incluyendo la protección legal de los derechos del autor o de la autora sobre sus obras.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["creación cultural", "derechos de autor", "propiedad intelectual"]
    ),
    99: ConstitutionalArticle(
        numero=99,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="Los valores de la cultura constituyen un bien irrenunciable del pueblo venezolano y un derecho fundamental que el Estado fomentará y garantizará. El Estado garantizará la protección y preservación, enriquecimiento, conservación y restauración del patrimonio cultural, tangible e intangible.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["patrimonio cultural", "valores culturales", "preservación"]
    ),
    100: ConstitutionalArticle(
        numero=100,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="Las culturas populares constitutivas de la venezolanidad gozan de atención especial, reconociéndose y respetándose la interculturalidad bajo el principio de igualdad de las culturas. La ley establecerá incentivos y estímulos para las personas, instituciones y comunidades que promuevan, apoyen, desarrollen o financien planes, programas y actividades culturales.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["culturas populares", "interculturalidad", "incentivos culturales"]
    ),
    102: ConstitutionalArticle(
        numero=102,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="La educación es un derecho humano y un deber social fundamental, es democrática, gratuita y obligatoria. El Estado la asumirá como función indeclinable y de máximo interés en todos sus niveles y modalidades.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["educación", "gratuidad", "obligatoriedad"],
        requires_organic_law=True
    ),
    103: ConstitutionalArticle(
        numero=103,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="Toda persona tiene derecho a una educación integral de calidad, permanente, en igualdad de condiciones y oportunidades, sin más limitaciones que las derivadas de sus aptitudes, vocación y aspiraciones. La educación es obligatoria en todos sus niveles, desde el maternal hasta el nivel medio diversificado.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["educación integral", "calidad educativa", "igualdad de oportunidades"]
    ),
    104: ConstitutionalArticle(
        numero=104,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="La educación estará a cargo de personas de reconocida moralidad y de comprobada idoneidad académica. El Estado estimulará su actualización permanente y les garantizará la estabilidad en el ejercicio de la carrera docente, bien sea pública o privada.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["docentes", "carrera docente", "estabilidad"]
    ),
    109: ConstitutionalArticle(
        numero=109,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="El Estado reconocerá la autonomía universitaria como principio y jerarquía que permite a los profesores, profesoras, estudiantes, egresados y egresadas de su comunidad dedicarse a la búsqueda del conocimiento a través de la investigación científica, humanística y tecnológica.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["autonomía universitaria", "universidades", "investigación"]
    ),
    110: ConstitutionalArticle(
        numero=110,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="El Estado reconocerá el interés público de la ciencia, la tecnología, el conocimiento, la innovación y sus aplicaciones y los servicios de información necesarios por ser instrumentos fundamentales para el desarrollo económico, social y político del país.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["ciencia", "tecnología", "innovación", "desarrollo"]
    ),
    111: ConstitutionalArticle(
        numero=111,
        titulo="Derechos Culturales y Educativos",
        capitulo="De los Derechos Culturales y Educativos",
        contenido="Todas las personas tienen derecho al deporte y a la recreación como actividades que benefician la calidad de vida individual y colectiva. El Estado asumirá el deporte y la recreación como política de educación y salud pública y garantizará los recursos para su promoción.",
        area=ConstitutionalArea.DERECHOS_CULTURALES,
        keywords=["deporte", "recreación", "calidad de vida"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL ECONOMIC RIGHTS (Arts. 114-118)
    # ═══════════════════════════════════════════════════════════════════════════
    114: ConstitutionalArticle(
        numero=114,
        titulo="Derechos Económicos",
        capitulo="De los Derechos Económicos",
        contenido="El ilícito económico, la especulación, el acaparamiento, la usura, la cartelización y otros delitos conexos, serán penados severamente de acuerdo con la ley.",
        area=ConstitutionalArea.DERECHOS_ECONOMICOS,
        keywords=["ilícitos económicos", "especulación", "acaparamiento", "usura"]
    ),
    116: ConstitutionalArticle(
        numero=116,
        titulo="Derechos Económicos",
        capitulo="De los Derechos Económicos",
        contenido="No se decretarán ni ejecutarán confiscaciones de bienes sino en los casos permitidos por esta Constitución. Por vía de excepción podrán ser objeto de confiscación, mediante sentencia firme, los bienes de personas naturales o jurídicas, nacionales o extranjeras, responsables de delitos cometidos contra el patrimonio público.",
        area=ConstitutionalArea.DERECHOS_ECONOMICOS,
        keywords=["confiscación", "patrimonio público", "corrupción"]
    ),
    117: ConstitutionalArticle(
        numero=117,
        titulo="Derechos Económicos",
        capitulo="De los Derechos Económicos",
        contenido="Todas las personas tendrán derecho a disponer de bienes y servicios de calidad, así como a una información adecuada y no engañosa sobre el contenido y características de los productos y servicios que consumen.",
        area=ConstitutionalArea.DERECHOS_ECONOMICOS,
        keywords=["derechos del consumidor", "calidad", "información"]
    ),
    118: ConstitutionalArticle(
        numero=118,
        titulo="Derechos Económicos",
        capitulo="De los Derechos Económicos",
        contenido="Se reconoce el derecho de los trabajadores y trabajadoras, así como de la comunidad, para desarrollar asociaciones de carácter social y participativo, como las cooperativas, cajas de ahorro, mutuales y otras formas asociativas.",
        area=ConstitutionalArea.DERECHOS_ECONOMICOS,
        keywords=["cooperativas", "economía social", "asociaciones"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # INDIGENOUS PEOPLES' RIGHTS (Arts. 119-126)
    # ═══════════════════════════════════════════════════════════════════════════
    119: ConstitutionalArticle(
        numero=119,
        titulo="Derechos de los Pueblos Indígenas",
        capitulo="De los Derechos de los Pueblos Indígenas",
        contenido="El Estado reconocerá la existencia de los pueblos y comunidades indígenas, su organización social, política y económica, sus culturas, usos y costumbres, idiomas y religiones, así como su hábitat y derechos originarios sobre las tierras que ancestral y tradicionalmente ocupan.",
        area=ConstitutionalArea.DERECHOS_PUEBLOS_INDIGENAS,
        keywords=["pueblos indígenas", "tierras ancestrales", "derechos originarios"],
        requires_organic_law=True
    ),
    120: ConstitutionalArticle(
        numero=120,
        titulo="Derechos de los Pueblos Indígenas",
        capitulo="De los Derechos de los Pueblos Indígenas",
        contenido="El aprovechamiento de los recursos naturales en los hábitats indígenas por parte del Estado se hará sin lesionar la integridad cultural, social y económica de los mismos e, igualmente, está sujeto a previa información y consulta a las comunidades indígenas respectivas.",
        area=ConstitutionalArea.DERECHOS_PUEBLOS_INDIGENAS,
        keywords=["consulta previa", "recursos naturales", "hábitats indígenas"]
    ),
    121: ConstitutionalArticle(
        numero=121,
        titulo="Derechos de los Pueblos Indígenas",
        capitulo="De los Derechos de los Pueblos Indígenas",
        contenido="Los pueblos indígenas tienen derecho a mantener y desarrollar su identidad étnica y cultural, cosmovisión, valores, espiritualidad y sus lugares sagrados y de culto. El Estado fomentará la valoración y difusión de las manifestaciones culturales de los pueblos indígenas.",
        area=ConstitutionalArea.DERECHOS_PUEBLOS_INDIGENAS,
        keywords=["identidad étnica", "cosmovisión", "lugares sagrados"]
    ),
    123: ConstitutionalArticle(
        numero=123,
        titulo="Derechos de los Pueblos Indígenas",
        capitulo="De los Derechos de los Pueblos Indígenas",
        contenido="Los pueblos indígenas tienen derecho a mantener y promover sus propias prácticas económicas basadas en la reciprocidad, la solidaridad y el intercambio; sus actividades productivas tradicionales, su participación en la economía nacional y a definir sus prioridades.",
        area=ConstitutionalArea.DERECHOS_PUEBLOS_INDIGENAS,
        keywords=["economía indígena", "prácticas tradicionales", "participación económica"]
    ),
    125: ConstitutionalArticle(
        numero=125,
        titulo="Derechos de los Pueblos Indígenas",
        capitulo="De los Derechos de los Pueblos Indígenas",
        contenido="Los pueblos indígenas tienen derecho a la participación política. El Estado garantizará la representación indígena en la Asamblea Nacional y en los cuerpos deliberantes de las entidades federales y locales con población indígena, conforme a la ley.",
        area=ConstitutionalArea.DERECHOS_PUEBLOS_INDIGENAS,
        keywords=["participación política indígena", "representación", "Asamblea Nacional"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ENVIRONMENTAL RIGHTS (Arts. 127-129)
    # ═══════════════════════════════════════════════════════════════════════════
    127: ConstitutionalArticle(
        numero=127,
        titulo="Derechos Ambientales",
        capitulo="De los Derechos Ambientales",
        contenido="Es un derecho y un deber de cada generación proteger y mantener el ambiente en beneficio de sí misma y del mundo futuro. Toda persona tiene derecho individual y colectivamente a disfrutar de una vida y de un ambiente seguro, sano y ecológicamente equilibrado.",
        area=ConstitutionalArea.DERECHOS_AMBIENTALES,
        keywords=["ambiente", "generaciones futuras", "equilibrio ecológico"],
        requires_organic_law=True
    ),
    128: ConstitutionalArticle(
        numero=128,
        titulo="Derechos Ambientales",
        capitulo="De los Derechos Ambientales",
        contenido="El Estado desarrollará una política de ordenación del territorio atendiendo a las realidades ecológicas, geográficas, poblacionales, sociales, culturales, económicas, políticas, de acuerdo con las premisas del desarrollo sustentable.",
        area=ConstitutionalArea.DERECHOS_AMBIENTALES,
        keywords=["ordenación territorial", "desarrollo sustentable"]
    ),
    129: ConstitutionalArticle(
        numero=129,
        titulo="Derechos Ambientales",
        capitulo="De los Derechos Ambientales",
        contenido="Todas las actividades susceptibles de generar daños a los ecosistemas deben ser previamente acompañadas de estudios de impacto ambiental y socio cultural. El Estado impedirá la entrada al país de desechos tóxicos y peligrosos, así como la fabricación y uso de armas nucleares, químicas y biológicas.",
        area=ConstitutionalArea.DERECHOS_AMBIENTALES,
        keywords=["impacto ambiental", "desechos tóxicos", "armas prohibidas"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL POWER STRUCTURE (Arts. 138-185)
    # ═══════════════════════════════════════════════════════════════════════════
    138: ConstitutionalArticle(
        numero=138,
        titulo="Poder Público",
        capitulo="Disposiciones Fundamentales",
        contenido="Toda autoridad usurpada es ineficaz y sus actos son nulos.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["usurpación", "nulidad", "autoridad legítima"]
    ),
    139: ConstitutionalArticle(
        numero=139,
        titulo="Poder Público",
        capitulo="Disposiciones Fundamentales",
        contenido="El ejercicio del Poder Público acarrea responsabilidad individual por abuso o desviación de poder o por violación de esta Constitución o de la ley.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["responsabilidad", "abuso de poder", "desviación de poder"]
    ),
    140: ConstitutionalArticle(
        numero=140,
        titulo="Poder Público",
        capitulo="Disposiciones Fundamentales",
        contenido="El Estado responderá patrimonialmente por los daños que sufran los o las particulares en cualquiera de sus bienes y derechos, siempre que la lesión sea imputable al funcionamiento de la administración pública.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["responsabilidad patrimonial", "daños", "administración pública"]
    ),
    141: ConstitutionalArticle(
        numero=141,
        titulo="Poder Público",
        capitulo="De la Función Pública",
        contenido="La Administración Pública está al servicio de los ciudadanos y ciudadanas y se fundamenta en los principios de honestidad, participación, celeridad, eficacia, eficiencia, transparencia, rendición de cuentas y responsabilidad en el ejercicio de la función pública.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["administración pública", "transparencia", "eficiencia"]
    ),
    143: ConstitutionalArticle(
        numero=143,
        titulo="Poder Público",
        capitulo="De la Función Pública",
        contenido="Los ciudadanos y ciudadanas tienen derecho a ser informados e informadas oportuna y verazmente por la Administración Pública, sobre el estado de las actuaciones en que estén directamente interesados e interesadas, y a conocer las resoluciones definitivas que se adopten sobre el particular.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["derecho a la información", "transparencia administrativa"]
    ),
    144: ConstitutionalArticle(
        numero=144,
        titulo="Poder Público",
        capitulo="De la Función Pública",
        contenido="La ley establecerá el Estatuto de la función pública mediante normas sobre el ingreso, ascenso, traslado, suspensión y retiro de los funcionarios o funcionarias de la Administración Pública.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["función pública", "estatuto", "funcionarios"]
    ),
    145: ConstitutionalArticle(
        numero=145,
        titulo="Poder Público",
        capitulo="De la Función Pública",
        contenido="Los funcionarios públicos y funcionarias públicas están al servicio del Estado y no de parcialidad alguna. Su nombramiento o remoción no podrán estar determinados por la afiliación u orientación política.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["neutralidad", "servicio público", "imparcialidad"]
    ),
    157: ConstitutionalArticle(
        numero=157,
        titulo="Poder Público Nacional",
        capitulo="De la Competencia del Poder Público Nacional",
        contenido="La Asamblea Nacional, por mayoría de sus integrantes, podrá atribuir a los Municipios o a los Estados determinadas materias de la competencia nacional, a fin de promover la descentralización.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["descentralización", "transferencia de competencias"]
    ),
    158: ConstitutionalArticle(
        numero=158,
        titulo="Poder Público Nacional",
        capitulo="De la Competencia del Poder Público Nacional",
        contenido="La descentralización, como política nacional, debe profundizar la democracia, acercando el poder a la población y creando las mejores condiciones, tanto para el ejercicio de la democracia como para la prestación eficaz y eficiente de los cometidos estatales.",
        area=ConstitutionalArea.PODER_PUBLICO,
        keywords=["descentralización", "democracia", "eficiencia estatal"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL LEGISLATIVE POWER (Arts. 186-224)
    # ═══════════════════════════════════════════════════════════════════════════
    186: ConstitutionalArticle(
        numero=186,
        titulo="Poder Legislativo",
        capitulo="De la Asamblea Nacional",
        contenido="La Asamblea Nacional estará integrada por diputados y diputadas elegidos o elegidas en cada entidad federal por votación universal, directa, personalizada y secreta con representación proporcional, según una base poblacional del uno coma uno por ciento de la población total del país.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["Asamblea Nacional", "diputados", "representación proporcional"]
    ),
    188: ConstitutionalArticle(
        numero=188,
        titulo="Poder Legislativo",
        capitulo="De la Asamblea Nacional",
        contenido="Las condiciones para ser elegido o elegida diputado o diputada a la Asamblea Nacional son: 1. Ser venezolano o venezolana por nacimiento o por naturalización con, por lo menos, quince años de residencia en territorio venezolano. 2. Ser mayor de veintiún años de edad. 3. Haber residido cuatro años consecutivos en la entidad correspondiente antes de la fecha de la elección.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["requisitos diputados", "nacionalidad", "residencia"]
    ),
    192: ConstitutionalArticle(
        numero=192,
        titulo="Poder Legislativo",
        capitulo="De los Diputados y Diputadas",
        contenido="Los diputados o diputadas a la Asamblea Nacional no son responsables por votos y opiniones emitidos en el ejercicio de sus funciones. Sólo responderán ante los electores o electoras y el cuerpo legislativo de acuerdo con esta Constitución y los reglamentos.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["inmunidad parlamentaria", "irresponsabilidad", "votos y opiniones"]
    ),
    193: ConstitutionalArticle(
        numero=193,
        titulo="Poder Legislativo",
        capitulo="De los Diputados y Diputadas",
        contenido="Los diputados o diputadas a la Asamblea Nacional gozarán de inmunidad en el ejercicio de sus funciones desde su proclamación hasta la conclusión de su mandato o de la renuncia del mismo. De los presuntos delitos que cometan los integrantes de la Asamblea Nacional conocerá en forma privativa el Tribunal Supremo de Justicia.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["inmunidad parlamentaria", "fuero especial", "TSJ"]
    ),
    204: ConstitutionalArticle(
        numero=204,
        titulo="Poder Legislativo",
        capitulo="De la Formación de las Leyes",
        contenido="La iniciativa de las leyes corresponde: 1. Al Poder Ejecutivo Nacional. 2. A la Comisión Delegada y a las Comisiones Permanentes. 3. A los integrantes de la Asamblea Nacional, en número no menor de tres. 4. Al Tribunal Supremo de Justicia, cuando se trate de leyes relativas a la organización y procedimientos judiciales. 5. Al Poder Ciudadano. 6. Al Poder Electoral. 7. A los electores en un número no menor del cero coma uno por ciento de los inscritos en el Registro Civil y Electoral. 8. Al Consejo Legislativo, cuando se trate de leyes relativas a los Estados.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["iniciativa legislativa", "proyectos de ley", "iniciativa popular"]
    ),
    207: ConstitutionalArticle(
        numero=207,
        titulo="Poder Legislativo",
        capitulo="De la Formación de las Leyes",
        contenido="Para convertirse en ley todo proyecto recibirá dos discusiones, en días diferentes, siguiendo las reglas establecidas en esta Constitución y en el reglamento respectivo. Aprobado el proyecto, el Presidente o Presidenta de la Asamblea Nacional declarará sancionada la ley.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["proceso legislativo", "dos discusiones", "sanción de ley"]
    ),
    214: ConstitutionalArticle(
        numero=214,
        titulo="Poder Legislativo",
        capitulo="De la Formación de las Leyes",
        contenido="El Presidente o Presidenta de la República promulgará la ley dentro de los diez días siguientes a aquél en que la haya recibido. Dentro de ese lapso podrá, en acuerdo con el Consejo de Ministros, solicitar a la Asamblea Nacional, mediante exposición razonada, que modifique alguna de las disposiciones de la ley o levante la sanción a toda la ley o a parte de ella.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["promulgación", "veto presidencial", "objeciones"]
    ),
    218: ConstitutionalArticle(
        numero=218,
        titulo="Poder Legislativo",
        capitulo="De la Formación de las Leyes",
        contenido="Las leyes se derogan por otras leyes y se abrogan por referendo, salvo las excepciones establecidas en esta Constitución. Podrán ser reformadas total o parcialmente. La ley que sea objeto de reforma parcial se publicará en un solo texto que incorpore las modificaciones aprobadas.",
        area=ConstitutionalArea.PODER_LEGISLATIVO,
        keywords=["derogación", "abrogación", "reforma de leyes"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTIVE POWER (Arts. 225-252)
    # ═══════════════════════════════════════════════════════════════════════════
    225: ConstitutionalArticle(
        numero=225,
        titulo="Poder Ejecutivo",
        capitulo="Del Presidente de la República",
        contenido="El Poder Ejecutivo se ejerce por el Presidente o Presidenta de la República, el Vicepresidente Ejecutivo o Vicepresidenta Ejecutiva, los Ministros o Ministras y demás funcionarios o funcionarias que determinen esta Constitución y la ley.",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["Poder Ejecutivo", "Presidente", "Vicepresidente"]
    ),
    226: ConstitutionalArticle(
        numero=226,
        titulo="Poder Ejecutivo",
        capitulo="Del Presidente de la República",
        contenido="El Presidente o Presidenta de la República es el Jefe o Jefa del Estado y del Ejecutivo Nacional, en cuya condición dirige la acción del Gobierno.",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["Jefe de Estado", "Jefe de Gobierno", "dirección gubernamental"]
    ),
    227: ConstitutionalArticle(
        numero=227,
        titulo="Poder Ejecutivo",
        capitulo="Del Presidente de la República",
        contenido="Para ser elegido Presidente o Presidenta de la República se requiere ser venezolano o venezolana por nacimiento, no poseer otra nacionalidad, ser mayor de treinta años, de estado seglar y no estar sometido o sometida a condena mediante sentencia definitivamente firme y cumplir con los demás requisitos establecidos en esta Constitución.",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["requisitos presidenciales", "nacionalidad", "elegibilidad"]
    ),
    228: ConstitutionalArticle(
        numero=228,
        titulo="Poder Ejecutivo",
        capitulo="Del Presidente de la República",
        contenido="La elección del Presidente o Presidenta de la República se hará por votación universal, directa y secreta, en conformidad con la ley. Se proclamará electo o electa el candidato o la candidata que hubiere obtenido la mayoría de votos válidos.",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["elección presidencial", "mayoría de votos", "sufragio"]
    ),
    230: ConstitutionalArticle(
        numero=230,
        titulo="Poder Ejecutivo",
        capitulo="Del Presidente de la República",
        contenido="El período presidencial es de seis años. El Presidente o Presidenta de la República puede ser reelegido o reelegida.",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["período presidencial", "reelección"]
    ),
    233: ConstitutionalArticle(
        numero=233,
        titulo="Poder Ejecutivo",
        capitulo="Del Presidente de la República",
        contenido="Serán faltas absolutas del Presidente o Presidenta de la República: su muerte, su renuncia, o su destitución decretada por sentencia del Tribunal Supremo de Justicia; su incapacidad física o mental permanente certificada por una junta médica designada por el Tribunal Supremo de Justicia y con aprobación de la Asamblea Nacional; el abandono del cargo, declarado como tal por la Asamblea Nacional, así como la revocación popular de su mandato.",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["falta absoluta", "sucesión presidencial", "vacante"]
    ),
    236: ConstitutionalArticle(
        numero=236,
        titulo="Poder Ejecutivo",
        capitulo="De las Atribuciones del Presidente",
        contenido="Son atribuciones y obligaciones del Presidente o Presidenta de la República: 1. Cumplir y hacer cumplir esta Constitución y la ley. 2. Dirigir la acción del Gobierno. 3. Nombrar y remover al Vicepresidente Ejecutivo o Vicepresidenta Ejecutiva, nombrar y remover los Ministros o Ministras. 4. Dirigir las relaciones exteriores de la República y celebrar y ratificar los tratados, convenios o acuerdos internacionales...",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["atribuciones presidenciales", "gobierno", "relaciones exteriores"]
    ),
    239: ConstitutionalArticle(
        numero=239,
        titulo="Poder Ejecutivo",
        capitulo="Del Vicepresidente Ejecutivo",
        contenido="Son atribuciones del Vicepresidente Ejecutivo o Vicepresidenta Ejecutiva: 1. Colaborar con el Presidente o Presidenta de la República en la dirección de la acción del Gobierno. 2. Coordinar la Administración Pública Nacional de conformidad con las instrucciones del Presidente o Presidenta de la República...",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["Vicepresidente", "coordinación", "administración pública"]
    ),
    242: ConstitutionalArticle(
        numero=242,
        titulo="Poder Ejecutivo",
        capitulo="De los Ministros",
        contenido="Los Ministros o Ministras son órganos directos del Presidente o Presidenta de la República, y reunidos o reunidas conjuntamente con éste o ésta y con el Vicepresidente Ejecutivo o Vicepresidenta Ejecutiva, integran el Consejo de Ministros.",
        area=ConstitutionalArea.PODER_EJECUTIVO,
        keywords=["ministros", "Consejo de Ministros", "gabinete"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # JUDICIAL POWER (Arts. 253-272)
    # ═══════════════════════════════════════════════════════════════════════════
    253: ConstitutionalArticle(
        numero=253,
        titulo="Poder Judicial",
        capitulo="Disposiciones Generales",
        contenido="La potestad de administrar justicia emana de los ciudadanos y ciudadanas y se imparte en nombre de la República por autoridad de la ley. Corresponde a los órganos del Poder Judicial conocer de las causas y asuntos de su competencia mediante los procedimientos que determinen las leyes, y ejecutar o hacer ejecutar sus sentencias.",
        area=ConstitutionalArea.PODER_JUDICIAL,
        keywords=["administración de justicia", "Poder Judicial", "sentencias"],
        requires_organic_law=True
    ),
    254: ConstitutionalArticle(
        numero=254,
        titulo="Poder Judicial",
        capitulo="Disposiciones Generales",
        contenido="El Poder Judicial es independiente y el Tribunal Supremo de Justicia gozará de autonomía funcional, financiera y administrativa. A tal efecto, dentro del presupuesto general del Estado se le asignará al sistema de justicia una partida anual variable, no menor del dos por ciento del presupuesto ordinario nacional.",
        area=ConstitutionalArea.PODER_JUDICIAL,
        keywords=["independencia judicial", "autonomía", "presupuesto judicial"]
    ),
    255: ConstitutionalArticle(
        numero=255,
        titulo="Poder Judicial",
        capitulo="Disposiciones Generales",
        contenido="El ingreso a la carrera judicial y el ascenso de los jueces o juezas se hará por concursos de oposición públicos que aseguren la idoneidad y excelencia de los o las participantes y serán seleccionados o seleccionadas por los jurados de los circuitos judiciales.",
        area=ConstitutionalArea.PODER_JUDICIAL,
        keywords=["carrera judicial", "concursos", "selección de jueces"]
    ),
    256: ConstitutionalArticle(
        numero=256,
        titulo="Poder Judicial",
        capitulo="Disposiciones Generales",
        contenido="Con la finalidad de garantizar la imparcialidad y la independencia en el ejercicio de sus funciones, los magistrados o las magistradas, los jueces o las juezas, los fiscales o las fiscales del Ministerio Público y los defensores públicos o las defensoras públicas, desde la fecha de su nombramiento y hasta su egreso del cargo respectivo, no podrán, salvo el ejercicio del voto, llevar a cabo activismo político partidista.",
        area=ConstitutionalArea.PODER_JUDICIAL,
        keywords=["imparcialidad judicial", "prohibición activismo político"]
    ),
    257: ConstitutionalArticle(
        numero=257,
        titulo="Poder Judicial",
        capitulo="Disposiciones Generales",
        contenido="El proceso constituye un instrumento fundamental para la realización de la justicia. Las leyes procesales establecerán la simplificación, uniformidad y eficacia de los trámites y adoptarán un procedimiento breve, oral y público. No se sacrificará la justicia por la omisión de formalidades no esenciales.",
        area=ConstitutionalArea.PODER_JUDICIAL,
        keywords=["proceso judicial", "simplificación", "oralidad", "formalidades"]
    ),
    262: ConstitutionalArticle(
        numero=262,
        titulo="Poder Judicial",
        capitulo="Del Tribunal Supremo de Justicia",
        contenido="El Tribunal Supremo de Justicia funcionará en Sala Plena y en las Salas Constitucional, Político-Administrativa, Electoral, de Casación Civil, de Casación Penal y de Casación Social, cuyas integraciones y competencias serán determinadas por su ley orgánica.",
        area=ConstitutionalArea.PODER_JUDICIAL,
        keywords=["TSJ", "Salas", "Sala Constitucional", "Casación"]
    ),
    266: ConstitutionalArticle(
        numero=266,
        titulo="Poder Judicial",
        capitulo="Del Tribunal Supremo de Justicia",
        contenido="Son atribuciones del Tribunal Supremo de Justicia: 1. Ejercer la jurisdicción constitucional conforme al Título VIII de esta Constitución. 2. Declarar si hay o no mérito para el enjuiciamiento del Presidente o Presidenta de la República o quien haga sus veces, y en caso afirmativo, continuar conociendo de la causa previa autorización de la Asamblea Nacional, hasta sentencia definitiva...",
        area=ConstitutionalArea.PODER_JUDICIAL,
        keywords=["atribuciones TSJ", "jurisdicción constitucional", "enjuiciamiento"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # CITIZEN POWER (Arts. 273-291)
    # ═══════════════════════════════════════════════════════════════════════════
    273: ConstitutionalArticle(
        numero=273,
        titulo="Poder Ciudadano",
        capitulo="Disposiciones Generales",
        contenido="El Poder Ciudadano se ejerce por el Consejo Moral Republicano integrado por el Defensor o Defensora del Pueblo, el Fiscal o la Fiscal General y el Contralor o Contralora General de la República.",
        area=ConstitutionalArea.PODER_CIUDADANO,
        keywords=["Poder Ciudadano", "Consejo Moral Republicano", "Defensor del Pueblo"]
    ),
    274: ConstitutionalArticle(
        numero=274,
        titulo="Poder Ciudadano",
        capitulo="Disposiciones Generales",
        contenido="Los órganos que ejercen el Poder Ciudadano tienen a su cargo, de conformidad con esta Constitución y con la ley, prevenir, investigar y sancionar los hechos que atenten contra la ética pública y la moral administrativa; velar por la buena gestión y la legalidad en el uso del patrimonio público.",
        area=ConstitutionalArea.PODER_CIUDADANO,
        keywords=["ética pública", "moral administrativa", "control"]
    ),
    280: ConstitutionalArticle(
        numero=280,
        titulo="Poder Ciudadano",
        capitulo="De la Defensoría del Pueblo",
        contenido="La Defensoría del Pueblo tiene a su cargo la promoción, defensa y vigilancia de los derechos y garantías establecidos en esta Constitución y en los tratados internacionales sobre derechos humanos, además de los intereses legítimos, colectivos o difusos de los ciudadanos y ciudadanas.",
        area=ConstitutionalArea.PODER_CIUDADANO,
        keywords=["Defensoría del Pueblo", "derechos humanos", "ombudsman"]
    ),
    285: ConstitutionalArticle(
        numero=285,
        titulo="Poder Ciudadano",
        capitulo="Del Ministerio Público",
        contenido="Son atribuciones del Ministerio Público: 1. Garantizar en los procesos judiciales el respeto a los derechos y garantías constitucionales, así como a los tratados, convenios y acuerdos internacionales suscritos por la República. 2. Garantizar la celeridad y buena marcha de la administración de justicia, el juicio previo y el debido proceso. 3. Ordenar y dirigir la investigación penal de la perpetración de los hechos punibles...",
        area=ConstitutionalArea.PODER_CIUDADANO,
        keywords=["Ministerio Público", "Fiscal General", "investigación penal"]
    ),
    287: ConstitutionalArticle(
        numero=287,
        titulo="Poder Ciudadano",
        capitulo="De la Contraloría General",
        contenido="La Contraloría General de la República es el órgano de control, vigilancia y fiscalización de los ingresos, gastos, bienes públicos y bienes nacionales, así como de las operaciones relativas a los mismos. Goza de autonomía funcional, administrativa y organizativa.",
        area=ConstitutionalArea.PODER_CIUDADANO,
        keywords=["Contraloría General", "control fiscal", "bienes públicos"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ELECTORAL POWER (Arts. 292-298)
    # ═══════════════════════════════════════════════════════════════════════════
    292: ConstitutionalArticle(
        numero=292,
        titulo="Poder Electoral",
        capitulo="Del Poder Electoral",
        contenido="El Poder Electoral se ejerce por el Consejo Nacional Electoral como ente rector y, son organismos subordinados a éste, la Junta Electoral Nacional, la Comisión de Registro Civil y Electoral y la Comisión de Participación Política y Financiamiento.",
        area=ConstitutionalArea.PODER_ELECTORAL,
        keywords=["Poder Electoral", "CNE", "Consejo Nacional Electoral"]
    ),
    293: ConstitutionalArticle(
        numero=293,
        titulo="Poder Electoral",
        capitulo="Del Poder Electoral",
        contenido="El Poder Electoral tiene por funciones: 1. Reglamentar las leyes electorales y resolver las dudas y vacíos que éstas susciten o contengan. 2. Formular su presupuesto, el cual tramitará directamente ante la Asamblea Nacional y administrará autónomamente. 3. Dictar directivas vinculantes en materia de financiamiento y publicidad político-electorales...",
        area=ConstitutionalArea.PODER_ELECTORAL,
        keywords=["funciones electorales", "reglamentación", "financiamiento político"]
    ),
    294: ConstitutionalArticle(
        numero=294,
        titulo="Poder Electoral",
        capitulo="Del Poder Electoral",
        contenido="Los órganos del Poder Electoral garantizarán la igualdad, confiabilidad, imparcialidad, transparencia y eficiencia de los procesos electorales, así como la aplicación de la personalización del sufragio y la representación proporcional.",
        area=ConstitutionalArea.PODER_ELECTORAL,
        keywords=["garantías electorales", "imparcialidad", "transparencia electoral"]
    ),
    297: ConstitutionalArticle(
        numero=297,
        titulo="Poder Electoral",
        capitulo="Del Poder Electoral",
        contenido="La jurisdicción contencioso electoral será ejercida por la Sala Electoral del Tribunal Supremo de Justicia y los demás tribunales que determine la ley.",
        area=ConstitutionalArea.PODER_ELECTORAL,
        keywords=["contencioso electoral", "Sala Electoral", "recursos electorales"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL SOCIOECONOMIC SYSTEM (Arts. 300-321)
    # ═══════════════════════════════════════════════════════════════════════════
    300: ConstitutionalArticle(
        numero=300,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico",
        contenido="La ley nacional establecerá las condiciones para la creación de entidades funcionalmente descentralizadas para la realización de actividades sociales o empresariales, con el objeto de asegurar la razonable productividad económica y social de los recursos públicos que en ellas se inviertan.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["entidades descentralizadas", "empresas públicas", "productividad"]
    ),
    301: ConstitutionalArticle(
        numero=301,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico",
        contenido="El Estado se reserva el uso de la política comercial para defender las actividades económicas de las empresas nacionales públicas y privadas. No se podrá otorgar a personas, empresas u organismos extranjeros regímenes más beneficiosos que los establecidos para los nacionales.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["política comercial", "protección nacional", "trato nacional"]
    ),
    305: ConstitutionalArticle(
        numero=305,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico",
        contenido="El Estado promoverá la agricultura sustentable como base estratégica del desarrollo rural integral a fin de garantizar la seguridad alimentaria de la población; entendida como la disponibilidad suficiente y estable de alimentos en el ámbito nacional y el acceso oportuno y permanente a éstos por parte del público consumidor.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["seguridad alimentaria", "agricultura", "desarrollo rural"]
    ),
    306: ConstitutionalArticle(
        numero=306,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico",
        contenido="El Estado promoverá las condiciones para el desarrollo rural integral, con el propósito de generar empleo y garantizar a la población campesina un nivel adecuado de bienestar, así como su incorporación al desarrollo nacional.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["desarrollo rural", "población campesina", "bienestar rural"]
    ),
    307: ConstitutionalArticle(
        numero=307,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Socioeconómico",
        contenido="El régimen latifundista es contrario al interés social. La ley dispondrá lo conducente en materia tributaria para gravar las tierras ociosas y establecerá las medidas necesarias para su transformación en unidades económicas productivas, rescatando igualmente las tierras de vocación agrícola.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["latifundio", "tierras ociosas", "reforma agraria"]
    ),
    311: ConstitutionalArticle(
        numero=311,
        titulo="Sistema Socioeconómico",
        capitulo="Del Régimen Fiscal y Monetario",
        contenido="La gestión fiscal estará regida y será ejecutada con base en principios de eficiencia, solvencia, transparencia, responsabilidad y equilibrio fiscal. Esta se equilibrará en el marco plurianual del presupuesto, de manera que los ingresos ordinarios deben ser suficientes para cubrir los gastos ordinarios.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["gestión fiscal", "equilibrio fiscal", "presupuesto"]
    ),
    316: ConstitutionalArticle(
        numero=316,
        titulo="Sistema Socioeconómico",
        capitulo="Del Sistema Tributario",
        contenido="El sistema tributario procurará la justa distribución de las cargas públicas según la capacidad económica del o la contribuyente, atendiendo al principio de progresividad, así como la protección de la economía nacional y la elevación del nivel de vida de la población; para ello se sustentará en un sistema eficiente para la recaudación de los tributos.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["sistema tributario", "capacidad contributiva", "progresividad"]
    ),
    317: ConstitutionalArticle(
        numero=317,
        titulo="Sistema Socioeconómico",
        capitulo="Del Sistema Tributario",
        contenido="No podrán cobrarse impuestos, tasas, ni contribuciones que no estén establecidos en la ley, ni concederse exenciones o rebajas, ni otras formas de incentivos fiscales, sino en los casos previstos por las leyes. Ningún tributo puede tener efecto confiscatorio.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["principio de legalidad tributaria", "no confiscatoriedad"]
    ),
    318: ConstitutionalArticle(
        numero=318,
        titulo="Sistema Socioeconómico",
        capitulo="Del Sistema Monetario",
        contenido="Las competencias monetarias del Poder Nacional serán ejercidas de manera exclusiva y obligatoria por el Banco Central de Venezuela. El objetivo fundamental del Banco Central de Venezuela es lograr la estabilidad de precios y preservar el valor interno y externo de la unidad monetaria.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["Banco Central", "política monetaria", "estabilidad de precios"]
    ),
    320: ConstitutionalArticle(
        numero=320,
        titulo="Sistema Socioeconómico",
        capitulo="De la Coordinación Macroeconómica",
        contenido="El Estado debe promover y defender la estabilidad económica, evitar la vulnerabilidad de la economía y velar por la estabilidad monetaria y de precios, para asegurar el bienestar social. El ministerio responsable de las finanzas y el Banco Central de Venezuela contribuirán a la armonización de la política fiscal con la política monetaria.",
        area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
        keywords=["estabilidad económica", "coordinación macroeconómica"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # NATIONAL SECURITY (Arts. 322-332)
    # ═══════════════════════════════════════════════════════════════════════════
    322: ConstitutionalArticle(
        numero=322,
        titulo="Seguridad de la Nación",
        capitulo="Disposiciones Generales",
        contenido="La seguridad de la Nación es competencia esencial y responsabilidad del Estado, fundamentada en el desarrollo integral de ésta y su defensa es responsabilidad de los venezolanos y venezolanas; también de las personas naturales y jurídicas, tanto de derecho público como de derecho privado, que se encuentren en el espacio geográfico nacional.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["seguridad nacional", "defensa", "responsabilidad compartida"]
    ),
    324: ConstitutionalArticle(
        numero=324,
        titulo="Seguridad de la Nación",
        capitulo="Disposiciones Generales",
        contenido="Sólo el Estado puede poseer y usar armas de guerra. Todas las que existan, se fabriquen o se introduzcan en el país, pasarán a ser propiedad de la República sin indemnización ni proceso. La Fuerza Armada Nacional será la institución competente para reglamentar y controlar, de acuerdo con la ley respectiva la fabricación, importación, exportación, almacenamiento, tránsito, registro, control, inspección, comercio, posesión y uso de otras armas, municiones y explosivos.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["armas de guerra", "monopolio estatal", "control de armas"]
    ),
    326: ConstitutionalArticle(
        numero=326,
        titulo="Seguridad de la Nación",
        capitulo="De los Principios de Seguridad",
        contenido="La seguridad de la Nación se fundamenta en la corresponsabilidad entre el Estado y la sociedad civil, para dar cumplimiento a los principios de independencia, democracia, igualdad, paz, libertad, justicia, solidaridad, promoción y conservación ambiental y afirmación de los derechos humanos, así como en la satisfacción progresiva de las necesidades individuales y colectivas de los venezolanos y venezolanas.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["corresponsabilidad", "seguridad integral", "derechos humanos"]
    ),
    328: ConstitutionalArticle(
        numero=328,
        titulo="Seguridad de la Nación",
        capitulo="De la Fuerza Armada Nacional",
        contenido="La Fuerza Armada Nacional constituye una institución esencialmente profesional, sin militancia política, organizada por el Estado para garantizar la independencia y soberanía de la Nación y asegurar la integridad del espacio geográfico, mediante la defensa militar, la cooperación en el mantenimiento del orden interno y la participación activa en el desarrollo nacional.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["Fuerza Armada", "profesionalismo militar", "defensa nacional"]
    ),
    329: ConstitutionalArticle(
        numero=329,
        titulo="Seguridad de la Nación",
        capitulo="De la Fuerza Armada Nacional",
        contenido="El Ejército, la Armada y la Aviación tienen como responsabilidad esencial la planificación, ejecución y control de las operaciones militares requeridas para asegurar la defensa de la Nación. La Guardia Nacional cooperará en el desarrollo de dichas operaciones y tendrá como responsabilidad básica la conducción de las operaciones exigidas para el mantenimiento del orden interno del país.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["Ejército", "Armada", "Aviación", "Guardia Nacional"]
    ),
    332: ConstitutionalArticle(
        numero=332,
        titulo="Seguridad de la Nación",
        capitulo="De los Órganos de Seguridad Ciudadana",
        contenido="El Ejecutivo Nacional, para mantener y restablecer el orden público, proteger al ciudadano o ciudadana, hogares y familias, apoyar las decisiones de las autoridades competentes y asegurar el pacífico disfrute de las garantías y derechos constitucionales, de conformidad con la ley, organizará: 1. Un cuerpo uniformado de policía nacional. 2. Un cuerpo de investigaciones científicas, penales y criminalísticas. 3. Un cuerpo de bomberos y administración de emergencias de carácter civil. 4. Una organización de protección civil y administración de desastres.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["policía nacional", "CICPC", "bomberos", "protección civil"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # STATES OF EXCEPTION (Arts. 337-339)
    # ═══════════════════════════════════════════════════════════════════════════
    337: ConstitutionalArticle(
        numero=337,
        titulo="Estados de Excepción",
        capitulo="De los Estados de Excepción",
        contenido="El Presidente o Presidenta de la República, en Consejo de Ministros, podrá decretar los estados de excepción. Se califican expresamente como tales las circunstancias de orden social, económico, político, natural o ecológico, que afecten gravemente la seguridad de la Nación, de las instituciones y de los ciudadanos y ciudadanas.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["estados de excepción", "emergencia", "decreto presidencial"]
    ),
    338: ConstitutionalArticle(
        numero=338,
        titulo="Estados de Excepción",
        capitulo="De los Estados de Excepción",
        contenido="Podrá decretarse el estado de alarma cuando se produzcan catástrofes, calamidades públicas u otros acontecimientos similares que pongan seriamente en peligro la seguridad de la Nación o de sus ciudadanos o ciudadanas. Dicho estado de excepción durará hasta treinta días, siendo prorrogable hasta por treinta días más.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["estado de alarma", "catástrofe", "calamidad pública"]
    ),
    339: ConstitutionalArticle(
        numero=339,
        titulo="Estados de Excepción",
        capitulo="De los Estados de Excepción",
        contenido="El Decreto que declare el estado de excepción, en el cual se regulará el ejercicio del derecho cuya garantía se restringe, será presentado, dentro de los ocho días siguientes de haberse dictado, a la Asamblea Nacional, o a la Comisión Delegada, para su consideración y aprobación, y a la Sala Constitucional del Tribunal Supremo de Justicia, para que se pronuncie sobre su constitucionalidad.",
        area=ConstitutionalArea.SEGURIDAD_NACION,
        keywords=["control parlamentario", "control constitucional", "restricción de garantías"]
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL CONSTITUTIONAL REFORM (Arts. 341-349)
    # ═══════════════════════════════════════════════════════════════════════════
    341: ConstitutionalArticle(
        numero=341,
        titulo="Reforma Constitucional",
        capitulo="De las Enmiendas",
        contenido="Las enmiendas a la Constitución se tramitarán en la forma siguiente: 1. La iniciativa podrá partir del quince por ciento de los ciudadanos inscritos en el Registro Civil y Electoral; o de un treinta por ciento de los integrantes de la Asamblea Nacional o del Presidente o Presidenta de la República en Consejo de Ministros. 2. Cuando la iniciativa parta de la Asamblea Nacional, la enmienda requerirá la aprobación de ésta por la mayoría de sus integrantes y se discutirá, según el procedimiento establecido en esta Constitución para la formación de leyes. 3. El Poder Electoral someterá a referendo las enmiendas a los treinta días siguientes a su recepción formal. 4. Se considerarán aprobadas las enmiendas de acuerdo con lo establecido en esta Constitución y en la ley relativa al referendo aprobatorio.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["enmienda", "iniciativa popular", "referendo"]
    ),
    343: ConstitutionalArticle(
        numero=343,
        titulo="Reforma Constitucional",
        capitulo="De la Reforma Constitucional",
        contenido="La iniciativa de la Reforma de la Constitución la ejerce la Asamblea Nacional mediante acuerdo aprobado por el voto de la mayoría de sus integrantes; el Presidente o Presidenta de la República en Consejo de Ministros; o un número no menor del quince por ciento de los electores inscritos y electoras inscritas en el Registro Civil y Electoral que lo soliciten.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["reforma constitucional", "iniciativa", "mayoría parlamentaria"]
    ),
    344: ConstitutionalArticle(
        numero=344,
        titulo="Reforma Constitucional",
        capitulo="De la Reforma Constitucional",
        contenido="El proyecto de Reforma Constitucional tendrá una primera discusión en el período de sesiones correspondiente a la presentación del mismo. Una segunda discusión por Título o Capítulo, según fuera el caso. Una tercera y última discusión artículo por artículo. La Asamblea Nacional aprobará el proyecto de reforma constitucional en un plazo no mayor de dos años, contados a partir de la fecha en la cual conoció y aprobó la solicitud de reforma.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["proceso de reforma", "discusiones", "plazo"]
    ),
    345: ConstitutionalArticle(
        numero=345,
        titulo="Reforma Constitucional",
        capitulo="De la Reforma Constitucional",
        contenido="El proyecto de Reforma Constitucional aprobado por la Asamblea Nacional se someterá a referendo dentro de los treinta días siguientes a su sanción. El referendo se pronunciará en conjunto sobre la Reforma, pero podrá votarse separadamente hasta una tercera parte de ella, si así lo aprobara un número no menor de una tercera parte de la Asamblea Nacional o si en la iniciativa de reforma así lo hubiere solicitado el Presidente o Presidenta de la República o un número no menor del cinco por ciento de los electores inscritos y electoras inscritas en el Registro Civil y Electoral.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["referendo", "votación separada", "aprobación popular"]
    ),
    348: ConstitutionalArticle(
        numero=348,
        titulo="Reforma Constitucional",
        capitulo="De la Asamblea Nacional Constituyente",
        contenido="La iniciativa de convocatoria a la Asamblea Nacional Constituyente podrán tomarla el Presidente o Presidenta de la República en Consejo de Ministros; la Asamblea Nacional, mediante acuerdo de las dos terceras partes de sus integrantes; los Concejos Municipales en cabildo, mediante el voto de las dos terceras partes de los mismos; o el quince por ciento de los electores inscritos y electoras inscritas en el Registro Civil y Electoral.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["Asamblea Constituyente", "convocatoria", "iniciativa popular"]
    ),
    349: ConstitutionalArticle(
        numero=349,
        titulo="Reforma Constitucional",
        capitulo="De la Asamblea Nacional Constituyente",
        contenido="El Presidente o Presidenta de la República no podrá objetar la nueva Constitución. Los poderes constituidos no podrán en forma alguna impedir las decisiones de la Asamblea Nacional Constituyente. A efectos de la promulgación de la nueva Constitución, ésta se publicará en la Gaceta Oficial de la República Bolivariana de Venezuela o en la Gaceta de la Asamblea Nacional Constituyente.",
        area=ConstitutionalArea.REFORMA_CONSTITUCIONAL,
        keywords=["promulgación", "poderes constituidos", "soberanía constituyente"]
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
#                         ANALYSIS ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def extract_keywords(text: str) -> List[str]:
    """Extract legal keywords from text."""
    # Legal term patterns
    keywords = []

    legal_terms = [
        "derecho", "derechos", "libertad", "libertades", "garantía", "garantías",
        "obligación", "obligaciones", "prohibición", "prohibido", "permitido",
        "autorización", "sanción", "pena", "multa", "prisión", "arresto",
        "propiedad", "expropiación", "confiscación", "decomiso",
        "contrato", "concesión", "licencia", "permiso",
        "impuesto", "tributo", "tasa", "contribución",
        "competencia", "jurisdicción", "atribución",
        "ley", "decreto", "reglamento", "resolución",
        "constitución", "constitucional", "inconstitucional",
        "orgánica", "ordinaria", "habilitante",
        "soberanía", "independencia", "autonomía",
        "hidrocarburos", "petróleo", "gas", "minería",
        "ambiente", "ambiental", "ecológico",
        "trabajo", "laboral", "trabajador", "patrono",
        "salud", "educación", "vivienda", "seguridad social",
        "familia", "matrimonio", "niños", "adolescentes",
        "electoral", "sufragio", "voto", "referendo",
        "judicial", "tribunal", "juez", "sentencia",
        "penal", "civil", "administrativo", "mercantil",
        "público", "privado", "estatal", "nacional"
    ]

    text_lower = text.lower()
    for term in legal_terms:
        if term in text_lower:
            keywords.append(term)

    return list(set(keywords))


def find_related_articles(text: str) -> List[int]:
    """Find constitutional articles that may be related to the text."""
    keywords = extract_keywords(text)
    related = set()

    for num, article in CONSTITUTIONAL_ARTICLES.items():
        # Check keyword overlap
        article_keywords = set(article.keywords)
        text_keywords = set(keywords)

        if article_keywords & text_keywords:
            related.add(num)

        # Check direct mentions in content
        for word in keywords:
            if word in article.contenido.lower():
                related.add(num)

    return sorted(list(related))


def analyze_conflict(
    proposed_text: str,
    article: ConstitutionalArticle,
    context: str = ""
) -> Optional[ConflictAnalysis]:
    """
    Analyze potential conflict between proposed text and constitutional article.

    Returns ConflictAnalysis if conflict found, None otherwise.
    """
    proposed_lower = proposed_text.lower()
    article_lower = article.contenido.lower()

    # Check for eternity clause violations (most severe)
    if article.is_eternity_clause:
        # Look for contradictions to fundamental principles
        contradiction_patterns = [
            (r"(?:elimina|suprime|deroga|anula).*(?:derecho|garantía|libertad)", ConflictType.ETERNITY_CLAUSE),
            (r"(?:pena de muerte|cadena perpetua)", ConflictType.RIGHTS_VIOLATION),
            (r"(?:tortura|tratos? (?:cruel|inhumano|degradante))", ConflictType.RIGHTS_VIOLATION),
        ]

        for pattern, conflict_type in contradiction_patterns:
            if re.search(pattern, proposed_lower):
                return ConflictAnalysis(
                    articulo=article.numero,
                    conflict_type=conflict_type,
                    severity=ConflictSeverity.CRITICAL,
                    area=article.area,
                    descripcion=f"Posible violación de cláusula pétrea del Artículo {article.numero}",
                    texto_constitucional=article.contenido[:300],
                    texto_propuesto=proposed_text[:300],
                    recomendacion="Esta disposición viola principios fundamentales inmutables de la Constitución. No puede ser aprobada sin una Asamblea Nacional Constituyente.",
                    requires_amendment=True,
                    amendment_type="Constituyente"
                )

    # Check for organic law requirements
    if article.requires_organic_law:
        if "ley ordinaria" in proposed_lower or "decreto" in proposed_lower:
            # Check if the subject matter requires organic law
            organic_subjects = ["trabajo", "laboral", "hidrocarburos", "petróleo", "poderes públicos"]
            for subject in organic_subjects:
                if subject in proposed_lower and subject in article_lower:
                    return ConflictAnalysis(
                        articulo=article.numero,
                        conflict_type=ConflictType.ORGANIC_LAW_REQUIRED,
                        severity=ConflictSeverity.HIGH,
                        area=article.area,
                        descripcion=f"La materia tratada requiere Ley Orgánica según el Artículo {article.numero}",
                        texto_constitucional=article.contenido[:300],
                        texto_propuesto=proposed_text[:300],
                        recomendacion="Reformular como proyecto de Ley Orgánica con la mayoría calificada requerida.",
                        requires_amendment=False
                    )

    # Check for competency conflicts
    competency_keywords = ["competencia", "atribución", "facultad", "potestad"]
    if any(kw in proposed_lower for kw in competency_keywords):
        if article.area in [ConstitutionalArea.PODER_PUBLICO, ConstitutionalArea.PODER_LEGISLATIVO]:
            # Check for potential overreach
            overreach_patterns = [
                r"(?:asume|transfiere|delega).*competencia",
                r"(?:municipal|estadal|nacional).*(?:asumirá|ejercerá)"
            ]
            for pattern in overreach_patterns:
                if re.search(pattern, proposed_lower):
                    return ConflictAnalysis(
                        articulo=article.numero,
                        conflict_type=ConflictType.COMPETENCY_CONFLICT,
                        severity=ConflictSeverity.HIGH,
                        area=article.area,
                        descripcion=f"Posible conflicto de competencias con el Artículo {article.numero}",
                        texto_constitucional=article.contenido[:300],
                        texto_propuesto=proposed_text[:300],
                        recomendacion="Verificar que la transferencia o asunción de competencias sea conforme al esquema constitucional de distribución del poder público.",
                        requires_amendment=False
                    )

    # Check for retroactivity issues
    if article.numero == 24:
        retroactivity_patterns = [
            r"(?:aplicará|surtirá efecto).*(?:retroactiv|anterior)",
            r"(?:desde|a partir de).*(?:fecha anterior|vigencia anterior)",
            r"(?:casos|procesos|situaciones).*(?:anteriores|pendientes)"
        ]
        for pattern in retroactivity_patterns:
            if re.search(pattern, proposed_lower):
                # Exception for favorable criminal law
                if not ("penal" in proposed_lower and "menor pena" in proposed_lower):
                    return ConflictAnalysis(
                        articulo=24,
                        conflict_type=ConflictType.RETROACTIVITY,
                        severity=ConflictSeverity.HIGH,
                        area=ConstitutionalArea.DERECHOS_CIVILES,
                        descripcion="Posible violación del principio de irretroactividad",
                        texto_constitucional=article.contenido[:300],
                        texto_propuesto=proposed_text[:300],
                        recomendacion="Eliminar efectos retroactivos o limitarlos a casos donde beneficien al reo en materia penal.",
                        requires_amendment=False
                    )

    # Check for hydrocarbon/PDVSA issues
    if article.numero in [302, 303]:
        pdvsa_patterns = [
            r"(?:privatiz|vend|enajen|transfier).*(?:pdvsa|petróleos|petrolera|acciones)",
            r"(?:particular|privad).*(?:control|mayoría|propiedad).*(?:petrolera|hidrocarburos)"
        ]
        for pattern in pdvsa_patterns:
            if re.search(pattern, proposed_lower):
                return ConflictAnalysis(
                    articulo=article.numero,
                    conflict_type=ConflictType.RESERVED_TO_CONSTITUTION,
                    severity=ConflictSeverity.CRITICAL,
                    area=ConstitutionalArea.SISTEMA_SOCIOECONOMICO,
                    descripcion=f"Violación de la reserva estatal de la industria petrolera (Art. {article.numero})",
                    texto_constitucional=article.contenido[:300],
                    texto_propuesto=proposed_text[:300],
                    recomendacion="La propiedad estatal de PDVSA es materia constitucional que no puede modificarse por ley ordinaria.",
                    requires_amendment=True,
                    amendment_type="Constituyente"
                )

    # Check for due process violations
    if article.numero == 49:
        due_process_violations = [
            (r"sin.*(?:audiencia|proceso|juicio)", "derecho a ser oído"),
            (r"(?:presunción de culpabilidad|culpable hasta)", "presunción de inocencia"),
            (r"sin.*(?:defensa|abogado|asistencia)", "derecho a la defensa"),
        ]
        for pattern, right_name in due_process_violations:
            if re.search(pattern, proposed_lower):
                return ConflictAnalysis(
                    articulo=49,
                    conflict_type=ConflictType.RIGHTS_VIOLATION,
                    severity=ConflictSeverity.CRITICAL,
                    area=ConstitutionalArea.DERECHOS_CIVILES,
                    descripcion=f"Violación del debido proceso: {right_name}",
                    texto_constitucional=article.contenido[:300],
                    texto_propuesto=proposed_text[:300],
                    recomendacion=f"Garantizar el {right_name} en todas las actuaciones.",
                    requires_amendment=False
                )

    return None


def generate_diff_report(
    titulo_proyecto: str,
    texto_propuesto: str,
    articulos_especificos: Optional[List[int]] = None
) -> DiffReport:
    """
    Generate a comprehensive constitutional diff report.

    Args:
        titulo_proyecto: Title of the proposed legislation
        texto_propuesto: Full text of the proposed legislation
        articulos_especificos: Specific articles to check (None = all)

    Returns:
        Complete DiffReport
    """
    conflicts = []
    related_articles = find_related_articles(texto_propuesto)

    # Determine which articles to analyze
    if articulos_especificos:
        articles_to_check = {
            num: CONSTITUTIONAL_ARTICLES[num]
            for num in articulos_especificos
            if num in CONSTITUTIONAL_ARTICLES
        }
    else:
        # Check all articles, prioritizing related ones
        articles_to_check = CONSTITUTIONAL_ARTICLES

    # Analyze each article
    for num, article in articles_to_check.items():
        conflict = analyze_conflict(texto_propuesto, article, titulo_proyecto)
        if conflict:
            conflicts.append(conflict)

    # Calculate statistics
    conflicts_by_severity = {}
    conflicts_by_type = {}

    for conflict in conflicts:
        sev = conflict.severity.value
        typ = conflict.conflict_type.value
        conflicts_by_severity[sev] = conflicts_by_severity.get(sev, 0) + 1
        conflicts_by_type[typ] = conflicts_by_type.get(typ, 0) + 1

    # Determine if constitutional change is required
    requires_change = any(c.requires_amendment for c in conflicts)

    # Determine amendment type
    amendment_recommendation = None
    if requires_change:
        if any(c.amendment_type == "Constituyente" for c in conflicts):
            amendment_recommendation = "Asamblea Nacional Constituyente"
        elif any(c.amendment_type == "Reforma" for c in conflicts):
            amendment_recommendation = "Reforma Constitucional (Art. 342)"
        else:
            amendment_recommendation = "Enmienda Constitucional (Art. 340)"

    # Calculate risk score
    severity_weights = {
        ConflictSeverity.CRITICAL: 1.0,
        ConflictSeverity.HIGH: 0.7,
        ConflictSeverity.MEDIUM: 0.4,
        ConflictSeverity.LOW: 0.2,
        ConflictSeverity.INFO: 0.0
    }

    if conflicts:
        risk_score = sum(severity_weights[c.severity] for c in conflicts) / len(conflicts)
    else:
        risk_score = 0.0

    compliance_percentage = max(0, (1 - risk_score) * 100)

    # Generate executive summary
    if not conflicts:
        resumen = f"El proyecto '{titulo_proyecto}' no presenta conflictos constitucionales identificados."
    else:
        critical_count = conflicts_by_severity.get("Crítico", 0)
        high_count = conflicts_by_severity.get("Alto", 0)

        if critical_count > 0:
            resumen = f"ALERTA: El proyecto presenta {critical_count} conflicto(s) CRÍTICO(S) con la Constitución."
        elif high_count > 0:
            resumen = f"El proyecto presenta {high_count} conflicto(s) de alta severidad que requieren atención."
        else:
            resumen = f"El proyecto presenta {len(conflicts)} observación(es) de menor severidad."

    return DiffReport(
        titulo_proyecto=titulo_proyecto,
        fecha_analisis=datetime.now().strftime("%d-%m-%Y %H:%M"),
        resumen_ejecutivo=resumen,
        total_conflicts=len(conflicts),
        conflicts_by_severity=conflicts_by_severity,
        conflicts_by_type=conflicts_by_type,
        conflicts=conflicts,
        related_articles=related_articles,
        requires_constitutional_change=requires_change,
        amendment_recommendation=amendment_recommendation,
        risk_score=round(risk_score, 2),
        compliance_percentage=round(compliance_percentage, 1)
    )


def get_article(numero: int) -> Optional[ConstitutionalArticle]:
    """Get a constitutional article by number."""
    return CONSTITUTIONAL_ARTICLES.get(numero)


def search_articles(query: str) -> List[ConstitutionalArticle]:
    """Search constitutional articles by keyword."""
    query_lower = query.lower()
    results = []

    for article in CONSTITUTIONAL_ARTICLES.values():
        if query_lower in article.contenido.lower():
            results.append(article)
        elif any(query_lower in kw.lower() for kw in article.keywords):
            results.append(article)
        elif query_lower in article.titulo.lower():
            results.append(article)

    return results


def get_eternity_clauses() -> List[ConstitutionalArticle]:
    """Get all articles marked as eternity clauses (cláusulas pétreas)."""
    return [a for a in CONSTITUTIONAL_ARTICLES.values() if a.is_eternity_clause]


def get_articles_by_area(area: ConstitutionalArea) -> List[ConstitutionalArticle]:
    """Get all articles in a specific constitutional area."""
    return [a for a in CONSTITUTIONAL_ARTICLES.values() if a.area == area]


def get_statistics() -> Dict[str, Any]:
    """Get database statistics."""
    areas = {}
    eternity_count = 0
    organic_count = 0

    for article in CONSTITUTIONAL_ARTICLES.values():
        area_name = article.area.value
        areas[area_name] = areas.get(area_name, 0) + 1
        if article.is_eternity_clause:
            eternity_count += 1
        if article.requires_organic_law:
            organic_count += 1

    return {
        "total_articles": len(CONSTITUTIONAL_ARTICLES),
        "articles_by_area": areas,
        "eternity_clauses": eternity_count,
        "requiring_organic_law": organic_count,
        "areas_covered": len(areas)
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def print_report(report: DiffReport) -> None:
    """Print formatted diff report."""
    print(f"\n{'═' * 80}")
    print(f"CONSTITUTIONAL DIFF REPORT")
    print(f"{'═' * 80}")
    print(f"Proyecto: {report.titulo_proyecto}")
    print(f"Fecha: {report.fecha_analisis}")
    print(f"{'─' * 80}")

    # Risk assessment
    risk_color = "🔴" if report.risk_score > 0.7 else "🟡" if report.risk_score > 0.3 else "🟢"
    print(f"\n{risk_color} RISK SCORE: {report.risk_score:.0%}")
    print(f"   Compliance: {report.compliance_percentage:.1f}%")

    print(f"\n📋 RESUMEN EJECUTIVO:")
    print(f"   {report.resumen_ejecutivo}")

    if report.requires_constitutional_change:
        print(f"\n⚠️  REQUIERE CAMBIO CONSTITUCIONAL: {report.amendment_recommendation}")

    # Conflict summary
    if report.conflicts:
        print(f"\n📊 CONFLICTOS IDENTIFICADOS: {report.total_conflicts}")
        print(f"   Por severidad:")
        for sev, count in sorted(report.conflicts_by_severity.items()):
            icon = "🔴" if sev == "Crítico" else "🟠" if sev == "Alto" else "🟡" if sev == "Medio" else "🟢"
            print(f"     {icon} {sev}: {count}")

        print(f"\n   Por tipo:")
        for typ, count in sorted(report.conflicts_by_type.items()):
            print(f"     • {typ}: {count}")

        # Detailed conflicts
        print(f"\n{'─' * 80}")
        print("DETALLE DE CONFLICTOS:")
        print(f"{'─' * 80}")

        for i, conflict in enumerate(report.conflicts, 1):
            icon = "🔴" if conflict.severity == ConflictSeverity.CRITICAL else "🟠" if conflict.severity == ConflictSeverity.HIGH else "🟡"
            print(f"\n{icon} Conflicto #{i}: Art. {conflict.articulo}")
            print(f"   Tipo: {conflict.conflict_type.value}")
            print(f"   Severidad: {conflict.severity.value}")
            print(f"   Área: {conflict.area.value}")
            print(f"\n   Descripción:")
            print(f"   {conflict.descripcion}")
            print(f"\n   Texto Constitucional:")
            print(f"   \"{conflict.texto_constitucional[:200]}...\"")
            print(f"\n   Recomendación:")
            print(f"   {conflict.recomendacion}")
            if conflict.requires_amendment:
                print(f"   ⚠️  Requiere: {conflict.amendment_type}")

    # Related articles
    if report.related_articles:
        print(f"\n{'─' * 80}")
        print(f"ARTÍCULOS RELACIONADOS: {', '.join(map(str, report.related_articles[:10]))}")
        if len(report.related_articles) > 10:
            print(f"   ... y {len(report.related_articles) - 10} más")

    print(f"\n{'═' * 80}\n")


def print_article(article: ConstitutionalArticle) -> None:
    """Print formatted constitutional article."""
    print(f"\n{'═' * 70}")
    print(f"ARTÍCULO {article.numero}")
    print(f"{'═' * 70}")
    print(f"Título: {article.titulo}")
    print(f"Capítulo: {article.capitulo}")
    print(f"Área: {article.area.value}")

    if article.is_eternity_clause:
        print("⚠️  CLÁUSULA PÉTREA")
    if article.requires_organic_law:
        print("📜 Requiere Ley Orgánica")

    print(f"\nContenido:")
    print(f"{article.contenido}")

    if article.keywords:
        print(f"\nPalabras clave: {', '.join(article.keywords)}")
    if article.related_articles:
        print(f"Artículos relacionados: {article.related_articles}")


def main():
    """CLI interface for Constitution Diff Engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Venezuela Super Lawyer - Constitution Diff Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 constitution_diff.py analyze "Ley de X" --text "El Estado privatizará..."
  python3 constitution_diff.py analyze "Proyecto" --file proyecto.txt
  python3 constitution_diff.py article 49
  python3 constitution_diff.py search "debido proceso"
  python3 constitution_diff.py eternity
  python3 constitution_diff.py area DERECHOS_CIVILES
  python3 constitution_diff.py stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze proposed legislation")
    analyze_parser.add_argument("titulo", help="Title of the proposed legislation")
    analyze_parser.add_argument("--text", help="Text to analyze")
    analyze_parser.add_argument("--file", help="File containing text to analyze")
    analyze_parser.add_argument("--articles", type=int, nargs="+",
                               help="Specific articles to check")
    analyze_parser.add_argument("--json", action="store_true",
                               help="Output as JSON")

    # Article lookup
    article_parser = subparsers.add_parser("article", help="Get constitutional article")
    article_parser.add_argument("numero", type=int, help="Article number")

    # Search
    search_parser = subparsers.add_parser("search", help="Search articles")
    search_parser.add_argument("query", help="Search query")

    # Eternity clauses
    subparsers.add_parser("eternity", help="List eternity clauses")

    # Articles by area
    area_parser = subparsers.add_parser("area", help="Get articles by area")
    area_parser.add_argument("area", choices=[a.name for a in ConstitutionalArea],
                            help="Constitutional area")

    # Statistics
    subparsers.add_parser("stats", help="Show database statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "analyze":
        # Get text to analyze
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                texto = f.read()
        elif args.text:
            texto = args.text
        else:
            print("Error: Provide --text or --file")
            return

        report = generate_diff_report(
            args.titulo,
            texto,
            args.articles
        )

        if args.json:
            # Convert to JSON-serializable format
            output = {
                "titulo_proyecto": report.titulo_proyecto,
                "fecha_analisis": report.fecha_analisis,
                "resumen_ejecutivo": report.resumen_ejecutivo,
                "total_conflicts": report.total_conflicts,
                "conflicts_by_severity": report.conflicts_by_severity,
                "conflicts_by_type": report.conflicts_by_type,
                "requires_constitutional_change": report.requires_constitutional_change,
                "amendment_recommendation": report.amendment_recommendation,
                "risk_score": report.risk_score,
                "compliance_percentage": report.compliance_percentage,
                "conflicts": [
                    {
                        "articulo": c.articulo,
                        "conflict_type": c.conflict_type.value,
                        "severity": c.severity.value,
                        "area": c.area.value,
                        "descripcion": c.descripcion,
                        "recomendacion": c.recomendacion,
                        "requires_amendment": c.requires_amendment,
                        "amendment_type": c.amendment_type
                    }
                    for c in report.conflicts
                ],
                "related_articles": report.related_articles
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print_report(report)

    elif args.command == "article":
        article = get_article(args.numero)
        if article:
            print_article(article)
        else:
            print(f"Artículo {args.numero} no encontrado en la base de datos.")
            print(f"Artículos disponibles: {sorted(CONSTITUTIONAL_ARTICLES.keys())}")

    elif args.command == "search":
        results = search_articles(args.query)
        print(f"\nResultados para '{args.query}': {len(results)} artículo(s)\n")
        for article in results[:10]:
            print(f"  Art. {article.numero}: {article.titulo} ({article.area.value})")
            print(f"    {article.contenido[:150]}...")
            print()

    elif args.command == "eternity":
        clauses = get_eternity_clauses()
        print(f"\n{'═' * 70}")
        print("CLÁUSULAS PÉTREAS DE LA CONSTITUCIÓN")
        print(f"{'═' * 70}")
        print(f"\nTotal: {len(clauses)} artículos\n")
        for article in clauses:
            print(f"  ⚠️  Art. {article.numero}: {article.titulo}")
            print(f"     {article.contenido[:100]}...")
            print()

    elif args.command == "area":
        area = ConstitutionalArea[args.area]
        articles = get_articles_by_area(area)
        print(f"\n{'═' * 70}")
        print(f"ARTÍCULOS: {area.value}")
        print(f"{'═' * 70}")
        print(f"\nTotal: {len(articles)} artículos\n")
        for article in articles:
            icon = "⚠️" if article.is_eternity_clause else "📜" if article.requires_organic_law else "•"
            print(f"  {icon} Art. {article.numero}: {article.keywords[:3] if article.keywords else 'N/A'}")

    elif args.command == "stats":
        stats = get_statistics()
        print(f"\n{'═' * 70}")
        print("CONSTITUTIONAL DATABASE STATISTICS")
        print(f"{'═' * 70}")
        print(f"\nTotal Articles: {stats['total_articles']}")
        print(f"Areas Covered: {stats['areas_covered']}")
        print(f"Eternity Clauses: {stats['eternity_clauses']}")
        print(f"Requiring Organic Law: {stats['requiring_organic_law']}")
        print(f"\nArticles by Area:")
        for area, count in sorted(stats['articles_by_area'].items()):
            print(f"  • {area}: {count}")


if __name__ == "__main__":
    main()
