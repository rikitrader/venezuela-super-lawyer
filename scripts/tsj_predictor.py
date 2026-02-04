#!/usr/bin/env python3
"""
Venezuela Super Lawyer - ML-based TSJ Prediction Module

Machine learning module for predicting TSJ (Tribunal Supremo de Justicia) outcomes
based on historical ruling patterns, case features, and legal area analysis.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
import re
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import Counter

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Try to import ML libraries (optional)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
#                         ENUMS AND CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class TSJSala(Enum):
    """TSJ chambers."""
    CONSTITUCIONAL = "Sala Constitucional"
    POLITICO_ADMINISTRATIVA = "Sala Político Administrativa"
    ELECTORAL = "Sala Electoral"
    CASACION_CIVIL = "Sala de Casación Civil"
    CASACION_PENAL = "Sala de Casación Penal"
    CASACION_SOCIAL = "Sala de Casación Social"
    PLENA = "Sala Plena"


class CaseOutcome(Enum):
    """Possible case outcomes."""
    FAVORABLE = "favorable"
    UNFAVORABLE = "unfavorable"
    PARTIAL = "partial"
    INADMISSIBLE = "inadmisible"
    DISMISSED = "desestimado"


class LegalArea(Enum):
    """Legal areas for classification."""
    CONSTITUTIONAL = "constitucional"
    ADMINISTRATIVE = "administrativo"
    LABOR = "laboral"
    CIVIL = "civil"
    CRIMINAL = "penal"
    COMMERCIAL = "mercantil"
    TAX = "tributario"
    FAMILY = "familia"
    ELECTORAL = "electoral"
    HYDROCARBONS = "hidrocarburos"


# ═══════════════════════════════════════════════════════════════════════════════
#                         HISTORICAL DATA (Training Data)
# ═══════════════════════════════════════════════════════════════════════════════

# Simulated historical TSJ rulings for training
# In production, this would come from a database
HISTORICAL_RULINGS = [
    # Constitutional cases
    {"id": "SC-001", "sala": TSJSala.CONSTITUCIONAL, "area": LegalArea.CONSTITUTIONAL,
     "keywords": ["amparo", "derechos fundamentales", "debido proceso"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2020,
     "facts_summary": "Violación del debido proceso en procedimiento administrativo"},
    {"id": "SC-002", "sala": TSJSala.CONSTITUCIONAL, "area": LegalArea.CONSTITUTIONAL,
     "keywords": ["control difuso", "inconstitucionalidad", "ley orgánica"],
     "outcome": CaseOutcome.UNFAVORABLE, "year": 2021,
     "facts_summary": "Solicitud de nulidad de ley por vicios de forma"},
    {"id": "SC-003", "sala": TSJSala.CONSTITUCIONAL, "area": LegalArea.CONSTITUTIONAL,
     "keywords": ["habeas corpus", "libertad personal", "detención"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2019,
     "facts_summary": "Detención sin orden judicial"},
    {"id": "SC-004", "sala": TSJSala.CONSTITUCIONAL, "area": LegalArea.CONSTITUTIONAL,
     "keywords": ["habeas data", "información", "privacidad"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2022,
     "facts_summary": "Acceso a información personal en registros públicos"},

    # Administrative cases
    {"id": "SPA-001", "sala": TSJSala.POLITICO_ADMINISTRATIVA, "area": LegalArea.ADMINISTRATIVE,
     "keywords": ["nulidad", "acto administrativo", "incompetencia"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2020,
     "facts_summary": "Acto administrativo dictado por autoridad incompetente"},
    {"id": "SPA-002", "sala": TSJSala.POLITICO_ADMINISTRATIVA, "area": LegalArea.ADMINISTRATIVE,
     "keywords": ["silencio administrativo", "recurso", "contencioso"],
     "outcome": CaseOutcome.UNFAVORABLE, "year": 2021,
     "facts_summary": "Recurso contra silencio administrativo"},
    {"id": "SPA-003", "sala": TSJSala.POLITICO_ADMINISTRATIVA, "area": LegalArea.ADMINISTRATIVE,
     "keywords": ["expropiación", "utilidad pública", "indemnización"],
     "outcome": CaseOutcome.PARTIAL, "year": 2022,
     "facts_summary": "Impugnación de justiprecio en expropiación"},

    # Labor cases
    {"id": "SCS-001", "sala": TSJSala.CASACION_SOCIAL, "area": LegalArea.LABOR,
     "keywords": ["despido injustificado", "reenganche", "salarios caídos"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2020,
     "facts_summary": "Despido sin justa causa de trabajador con estabilidad"},
    {"id": "SCS-002", "sala": TSJSala.CASACION_SOCIAL, "area": LegalArea.LABOR,
     "keywords": ["prestaciones sociales", "antigüedad", "liquidación"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2021,
     "facts_summary": "Diferencia de prestaciones sociales"},
    {"id": "SCS-003", "sala": TSJSala.CASACION_SOCIAL, "area": LegalArea.LABOR,
     "keywords": ["accidente laboral", "enfermedad ocupacional", "indemnización"],
     "outcome": CaseOutcome.PARTIAL, "year": 2019,
     "facts_summary": "Indemnización por enfermedad ocupacional"},

    # Civil cases
    {"id": "SCC-001", "sala": TSJSala.CASACION_CIVIL, "area": LegalArea.CIVIL,
     "keywords": ["cumplimiento contrato", "daños y perjuicios", "incumplimiento"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2021,
     "facts_summary": "Incumplimiento de contrato de compraventa"},
    {"id": "SCC-002", "sala": TSJSala.CASACION_CIVIL, "area": LegalArea.CIVIL,
     "keywords": ["propiedad", "reivindicación", "posesión"],
     "outcome": CaseOutcome.UNFAVORABLE, "year": 2020,
     "facts_summary": "Acción reivindicatoria sobre inmueble"},
    {"id": "SCC-003", "sala": TSJSala.CASACION_CIVIL, "area": LegalArea.CIVIL,
     "keywords": ["herencia", "testamento", "nulidad"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2022,
     "facts_summary": "Nulidad de testamento por incapacidad"},

    # Tax cases
    {"id": "SPA-TAX-001", "sala": TSJSala.POLITICO_ADMINISTRATIVA, "area": LegalArea.TAX,
     "keywords": ["ISLR", "reparo fiscal", "contribuyente"],
     "outcome": CaseOutcome.PARTIAL, "year": 2020,
     "facts_summary": "Impugnación de reparo fiscal ISLR"},
    {"id": "SPA-TAX-002", "sala": TSJSala.POLITICO_ADMINISTRATIVA, "area": LegalArea.TAX,
     "keywords": ["IVA", "crédito fiscal", "rechazo"],
     "outcome": CaseOutcome.FAVORABLE, "year": 2021,
     "facts_summary": "Rechazo de créditos fiscales IVA"},

    # Hydrocarbons cases
    {"id": "SPA-HC-001", "sala": TSJSala.POLITICO_ADMINISTRATIVA, "area": LegalArea.HYDROCARBONS,
     "keywords": ["PDVSA", "empresa mixta", "participación estatal"],
     "outcome": CaseOutcome.UNFAVORABLE, "year": 2019,
     "facts_summary": "Impugnación de condiciones de empresa mixta"},
    {"id": "SPA-HC-002", "sala": TSJSala.POLITICO_ADMINISTRATIVA, "area": LegalArea.HYDROCARBONS,
     "keywords": ["regalía", "hidrocarburos", "ministerio"],
     "outcome": CaseOutcome.UNFAVORABLE, "year": 2020,
     "facts_summary": "Recurso contra determinación de regalía"},
]

# Outcome weights by legal area (based on historical patterns)
OUTCOME_PROBABILITIES = {
    LegalArea.CONSTITUTIONAL: {
        CaseOutcome.FAVORABLE: 0.55,
        CaseOutcome.UNFAVORABLE: 0.30,
        CaseOutcome.PARTIAL: 0.10,
        CaseOutcome.INADMISSIBLE: 0.05
    },
    LegalArea.ADMINISTRATIVE: {
        CaseOutcome.FAVORABLE: 0.40,
        CaseOutcome.UNFAVORABLE: 0.35,
        CaseOutcome.PARTIAL: 0.20,
        CaseOutcome.INADMISSIBLE: 0.05
    },
    LegalArea.LABOR: {
        CaseOutcome.FAVORABLE: 0.60,
        CaseOutcome.UNFAVORABLE: 0.25,
        CaseOutcome.PARTIAL: 0.10,
        CaseOutcome.INADMISSIBLE: 0.05
    },
    LegalArea.CIVIL: {
        CaseOutcome.FAVORABLE: 0.45,
        CaseOutcome.UNFAVORABLE: 0.40,
        CaseOutcome.PARTIAL: 0.10,
        CaseOutcome.INADMISSIBLE: 0.05
    },
    LegalArea.TAX: {
        CaseOutcome.FAVORABLE: 0.35,
        CaseOutcome.UNFAVORABLE: 0.40,
        CaseOutcome.PARTIAL: 0.20,
        CaseOutcome.INADMISSIBLE: 0.05
    },
    LegalArea.HYDROCARBONS: {
        CaseOutcome.FAVORABLE: 0.25,
        CaseOutcome.UNFAVORABLE: 0.55,
        CaseOutcome.PARTIAL: 0.15,
        CaseOutcome.INADMISSIBLE: 0.05
    },
}

# Keywords that affect outcome probability
FAVORABLE_INDICATORS = [
    "derechos fundamentales", "debido proceso", "amparo",
    "violación", "inconstitucional", "nulidad absoluta",
    "despido injustificado", "trabajador", "prestaciones",
    "incumplimiento", "daños"
]

UNFAVORABLE_INDICATORS = [
    "prescripción", "caducidad", "extemporáneo",
    "inadmisible", "falta de legitimación", "cosa juzgada",
    "soberanía", "reserva estatal", "interés público"
]


# ═══════════════════════════════════════════════════════════════════════════════
#                         DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class FeatureVector:
    """Feature vector for ML model."""
    legal_area: LegalArea
    sala: TSJSala
    keywords: List[str]
    text_features: Dict[str, float] = field(default_factory=dict)
    favorable_score: float = 0.0
    unfavorable_score: float = 0.0
    complexity_score: float = 0.0


@dataclass
class PredictionResult:
    """TSJ prediction result."""
    predicted_outcome: str
    confidence: float
    favorable_probability: float
    sala_recomendada: TSJSala
    similar_cases: List[Dict[str, Any]]
    key_factors: List[str]
    risk_factors: List[str]
    legal_area: LegalArea
    analysis_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['sala_recomendada'] = self.sala_recomendada.value
        result['legal_area'] = self.legal_area.value
        return result


# ═══════════════════════════════════════════════════════════════════════════════
#                         FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

def extract_keywords(text: str) -> List[str]:
    """Extract legal keywords from text."""
    text_lower = text.lower()
    found_keywords = []

    # Legal term patterns
    legal_terms = [
        "amparo", "habeas corpus", "habeas data", "nulidad",
        "inconstitucional", "recurso", "apelación", "casación",
        "debido proceso", "derechos fundamentales", "libertad",
        "propiedad", "contrato", "daños", "perjuicios",
        "despido", "trabajador", "prestaciones", "salario",
        "impuesto", "tributo", "fiscal", "contribuyente",
        "hidrocarburos", "petróleo", "PDVSA", "regalía",
        "expropiación", "indemnización", "administrativa"
    ]

    for term in legal_terms:
        if term.lower() in text_lower:
            found_keywords.append(term)

    return found_keywords


def detect_legal_area(text: str, keywords: List[str]) -> LegalArea:
    """Detect the legal area from text and keywords."""
    text_lower = text.lower()

    # Area indicators
    area_indicators = {
        LegalArea.CONSTITUTIONAL: ["amparo", "constitucional", "derechos fundamentales", "habeas"],
        LegalArea.ADMINISTRATIVE: ["administrativo", "acto administrativo", "nulidad", "recurso contencioso"],
        LegalArea.LABOR: ["laboral", "trabajador", "despido", "prestaciones", "salario"],
        LegalArea.CIVIL: ["civil", "contrato", "propiedad", "herencia", "obligación"],
        LegalArea.CRIMINAL: ["penal", "delito", "acusación", "pena"],
        LegalArea.TAX: ["tributario", "fiscal", "impuesto", "ISLR", "IVA", "reparo"],
        LegalArea.COMMERCIAL: ["mercantil", "sociedad", "comercio", "quiebra"],
        LegalArea.HYDROCARBONS: ["hidrocarburos", "petróleo", "PDVSA", "regalía", "empresa mixta"],
        LegalArea.ELECTORAL: ["electoral", "voto", "elección", "candidato"],
        LegalArea.FAMILY: ["familia", "divorcio", "custodia", "alimentos", "matrimonio"]
    }

    scores = {area: 0 for area in LegalArea}

    for area, indicators in area_indicators.items():
        for indicator in indicators:
            if indicator.lower() in text_lower:
                scores[area] += 2
            if indicator.lower() in [k.lower() for k in keywords]:
                scores[area] += 1

    best_area = max(scores, key=scores.get)
    if scores[best_area] == 0:
        return LegalArea.CIVIL  # Default

    return best_area


def recommend_sala(legal_area: LegalArea) -> TSJSala:
    """Recommend the appropriate TSJ chamber for a legal area."""
    sala_mapping = {
        LegalArea.CONSTITUTIONAL: TSJSala.CONSTITUCIONAL,
        LegalArea.ADMINISTRATIVE: TSJSala.POLITICO_ADMINISTRATIVA,
        LegalArea.LABOR: TSJSala.CASACION_SOCIAL,
        LegalArea.CIVIL: TSJSala.CASACION_CIVIL,
        LegalArea.CRIMINAL: TSJSala.CASACION_PENAL,
        LegalArea.TAX: TSJSala.POLITICO_ADMINISTRATIVA,
        LegalArea.COMMERCIAL: TSJSala.CASACION_CIVIL,
        LegalArea.HYDROCARBONS: TSJSala.POLITICO_ADMINISTRATIVA,
        LegalArea.ELECTORAL: TSJSala.ELECTORAL,
        LegalArea.FAMILY: TSJSala.CASACION_CIVIL
    }
    return sala_mapping.get(legal_area, TSJSala.CONSTITUCIONAL)


def calculate_favorable_score(text: str, keywords: List[str]) -> float:
    """Calculate score for favorable outcome indicators."""
    text_lower = text.lower()
    score = 0.0

    for indicator in FAVORABLE_INDICATORS:
        if indicator.lower() in text_lower:
            score += 0.1
        if indicator.lower() in [k.lower() for k in keywords]:
            score += 0.05

    return min(score, 1.0)


def calculate_unfavorable_score(text: str, keywords: List[str]) -> float:
    """Calculate score for unfavorable outcome indicators."""
    text_lower = text.lower()
    score = 0.0

    for indicator in UNFAVORABLE_INDICATORS:
        if indicator.lower() in text_lower:
            score += 0.15
        if indicator.lower() in [k.lower() for k in keywords]:
            score += 0.05

    return min(score, 1.0)


def extract_features(case_facts: str, legal_area: str = None) -> FeatureVector:
    """Extract features from case facts."""
    keywords = extract_keywords(case_facts)

    # Detect legal area if not provided
    if legal_area:
        try:
            area = LegalArea(legal_area.lower())
        except ValueError:
            area = detect_legal_area(case_facts, keywords)
    else:
        area = detect_legal_area(case_facts, keywords)

    sala = recommend_sala(area)

    favorable_score = calculate_favorable_score(case_facts, keywords)
    unfavorable_score = calculate_unfavorable_score(case_facts, keywords)

    # Complexity based on text length and keyword density
    complexity = min(len(case_facts) / 5000, 1.0) + (len(keywords) / 20)

    return FeatureVector(
        legal_area=area,
        sala=sala,
        keywords=keywords,
        favorable_score=favorable_score,
        unfavorable_score=unfavorable_score,
        complexity_score=complexity
    )


# ═══════════════════════════════════════════════════════════════════════════════
#                         SIMILARITY SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

def find_similar_cases(keywords: List[str], legal_area: LegalArea, limit: int = 5) -> List[Dict]:
    """Find similar historical cases based on keywords and legal area."""
    similar = []

    for ruling in HISTORICAL_RULINGS:
        if ruling['area'] != legal_area:
            continue

        # Calculate keyword overlap
        ruling_keywords = set(k.lower() for k in ruling['keywords'])
        case_keywords = set(k.lower() for k in keywords)
        overlap = len(ruling_keywords.intersection(case_keywords))

        if overlap > 0:
            similar.append({
                'id': ruling['id'],
                'sala': ruling['sala'].value,
                'outcome': ruling['outcome'].value,
                'year': ruling['year'],
                'facts_summary': ruling['facts_summary'],
                'keyword_overlap': overlap,
                'similarity_score': overlap / max(len(ruling_keywords), len(case_keywords), 1)
            })

    # Sort by similarity score
    similar.sort(key=lambda x: x['similarity_score'], reverse=True)
    return similar[:limit]


# ═══════════════════════════════════════════════════════════════════════════════
#                         ML PREDICTION (Heuristic + Optional sklearn)
# ═══════════════════════════════════════════════════════════════════════════════

class TSJPredictor:
    """TSJ outcome predictor using heuristics and optional ML."""

    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.trained = False

        if SKLEARN_AVAILABLE:
            self._train_model()

    def _train_model(self):
        """Train the ML model on historical data."""
        if not SKLEARN_AVAILABLE:
            return

        # Prepare training data
        texts = []
        labels = []

        for ruling in HISTORICAL_RULINGS:
            text = ruling['facts_summary'] + ' ' + ' '.join(ruling['keywords'])
            texts.append(text)
            labels.append(1 if ruling['outcome'] == CaseOutcome.FAVORABLE else 0)

        if len(texts) < 5:
            return  # Not enough data

        # Create TF-IDF features
        self.vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2))
        X = self.vectorizer.fit_transform(texts)

        # Train classifier
        self.model = MultinomialNB()
        self.model.fit(X, labels)
        self.trained = True

    def predict_with_ml(self, text: str) -> Tuple[float, float]:
        """Predict using ML model, returns (favorable_prob, confidence)."""
        if not self.trained or not self.vectorizer:
            return 0.5, 0.0

        X = self.vectorizer.transform([text])
        proba = self.model.predict_proba(X)[0]

        # proba[1] is favorable probability
        favorable_prob = proba[1] if len(proba) > 1 else 0.5
        confidence = max(proba) - 0.5  # How confident vs random

        return favorable_prob, confidence

    def predict(self, case_facts: str, legal_area: str = None) -> PredictionResult:
        """Generate full prediction for a case."""
        # Extract features
        features = extract_features(case_facts, legal_area)

        # Get base probabilities for legal area
        base_probs = OUTCOME_PROBABILITIES.get(
            features.legal_area,
            {CaseOutcome.FAVORABLE: 0.5, CaseOutcome.UNFAVORABLE: 0.5}
        )

        # Adjust based on text analysis
        favorable_base = base_probs.get(CaseOutcome.FAVORABLE, 0.5)

        # Apply heuristic adjustments
        favorable_prob = favorable_base
        favorable_prob += features.favorable_score * 0.2
        favorable_prob -= features.unfavorable_score * 0.25

        # ML adjustment if available
        ml_confidence = 0.0
        if self.trained:
            ml_prob, ml_conf = self.predict_with_ml(case_facts)
            # Blend heuristic and ML predictions
            favorable_prob = (favorable_prob * 0.6) + (ml_prob * 0.4)
            ml_confidence = ml_conf

        # Clamp probability
        favorable_prob = max(0.1, min(0.9, favorable_prob))

        # Determine predicted outcome
        if favorable_prob > 0.6:
            predicted_outcome = "Favorable"
        elif favorable_prob > 0.4:
            predicted_outcome = "Resultado Incierto"
        else:
            predicted_outcome = "Desfavorable"

        # Calculate confidence
        distance_from_uncertain = abs(favorable_prob - 0.5)
        base_confidence = 0.5 + distance_from_uncertain
        confidence = min(0.95, base_confidence + ml_confidence * 0.1)

        # Find similar cases
        similar_cases = find_similar_cases(features.keywords, features.legal_area)

        # Identify key factors
        key_factors = []
        if features.favorable_score > 0.3:
            key_factors.append("Presencia de indicadores favorables en los hechos")
        if features.keywords:
            key_factors.append(f"Área legal identificada: {features.legal_area.value}")
        if similar_cases:
            favorable_count = sum(1 for c in similar_cases if c['outcome'] == 'favorable')
            key_factors.append(f"Casos similares: {favorable_count}/{len(similar_cases)} favorables")

        # Identify risk factors
        risk_factors = []
        if features.unfavorable_score > 0.2:
            risk_factors.append("Presencia de indicadores desfavorables")
        if features.legal_area == LegalArea.HYDROCARBONS:
            risk_factors.append("Materia de hidrocarburos - Alta reserva estatal")
        if features.legal_area == LegalArea.TAX:
            risk_factors.append("Materia tributaria - Presunción de legalidad del acto")
        if features.complexity_score > 1.5:
            risk_factors.append("Caso de alta complejidad")

        return PredictionResult(
            predicted_outcome=predicted_outcome,
            confidence=round(confidence, 3),
            favorable_probability=round(favorable_prob, 3),
            sala_recomendada=features.sala,
            similar_cases=similar_cases,
            key_factors=key_factors,
            risk_factors=risk_factors,
            legal_area=features.legal_area
        )


# ═══════════════════════════════════════════════════════════════════════════════
#                         PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

# Global predictor instance
_predictor: Optional[TSJPredictor] = None


def get_predictor() -> TSJPredictor:
    """Get or create the global predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = TSJPredictor()
    return _predictor


def predict_outcome(case_facts: str, legal_area: str = None) -> PredictionResult:
    """
    Predict TSJ case outcome.

    Args:
        case_facts: Description of case facts
        legal_area: Optional legal area hint (constitucional, laboral, civil, etc.)

    Returns:
        PredictionResult with prediction details
    """
    predictor = get_predictor()
    return predictor.predict(case_facts, legal_area)


def get_outcome_probabilities(legal_area: str) -> Dict[str, float]:
    """Get base outcome probabilities for a legal area."""
    try:
        area = LegalArea(legal_area.lower())
    except ValueError:
        return {"error": f"Unknown legal area: {legal_area}"}

    probs = OUTCOME_PROBABILITIES.get(area, {})
    return {k.value: v for k, v in probs.items()}


def get_statistics() -> Dict[str, Any]:
    """Get TSJ predictor statistics."""
    predictor = get_predictor()

    return {
        "module": "TSJ Predictor (ML)",
        "version": __version__,
        "sklearn_available": SKLEARN_AVAILABLE,
        "numpy_available": NUMPY_AVAILABLE,
        "model_trained": predictor.trained,
        "training_samples": len(HISTORICAL_RULINGS),
        "legal_areas_supported": [a.value for a in LegalArea],
        "salas_supported": [s.value for s in TSJSala],
        "features": [
            "Keyword extraction",
            "Legal area detection",
            "Sala recommendation",
            "Heuristic probability estimation",
            "Similar case retrieval",
            "ML enhancement (when sklearn available)"
        ],
        "outcome_types": [o.value for o in CaseOutcome]
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for TSJ predictor."""
    import argparse

    parser = argparse.ArgumentParser(description="TSJ Outcome Predictor")
    parser.add_argument("--predict", type=str, help="Case facts to predict")
    parser.add_argument("--area", type=str, help="Legal area hint")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    if args.stats:
        print(json.dumps(get_statistics(), indent=2, ensure_ascii=False))
        return

    if args.predict:
        result = predict_outcome(args.predict, args.area)
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        # Demo prediction
        demo_case = """
        El trabajador fue despedido sin justa causa después de 5 años de servicio.
        No se le pagaron las prestaciones sociales ni los salarios caídos.
        Solicita reenganche y pago de salarios caídos.
        """
        print("Demo prediction:")
        result = predict_outcome(demo_case, "laboral")
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
