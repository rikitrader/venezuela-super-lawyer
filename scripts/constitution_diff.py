#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Constitution Diff Engine
Compares proposed legislation against the Venezuelan Constitution (CRBV)
to identify potential conflicts, required amendments, and compliance issues.

CRBV: Constitución de la República Bolivariana de Venezuela (1999)
Published in Gaceta Oficial Extraordinaria N° 5.908 del 19 de febrero de 2009
(Enmienda N° 1)
"""

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
