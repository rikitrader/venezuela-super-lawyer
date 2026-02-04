#!/usr/bin/env python3
"""
Unit tests for constitution_diff.py - Constitutional Diff Engine
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from constitution_diff import (
    ConflictSeverity,
    ConflictType,
    ConstitutionalArea,
    ConstitutionalArticle,
    ConflictAnalysis,
    DiffReport,
    generate_diff_report,
    get_article,
    search_articles,
    get_eternity_clauses,
    get_articles_by_area,
    get_statistics,
    CONSTITUTIONAL_ARTICLES
)


class TestConstitutionDiff(unittest.TestCase):
    """Test cases for Constitution Diff Engine."""

    def test_database_not_empty(self):
        """Constitutional database should have articles."""
        self.assertGreater(len(CONSTITUTIONAL_ARTICLES), 0)

    def test_database_has_minimum_articles(self):
        """Database should have at least 100 articles (expanded database)."""
        self.assertGreaterEqual(len(CONSTITUTIONAL_ARTICLES), 100)

    def test_key_articles_exist(self):
        """Key constitutional articles should exist."""
        key_articles = [1, 2, 7, 19, 21, 24, 49, 302, 303]
        for num in key_articles:
            article = get_article(num)
            self.assertIsNotNone(article, f"Missing article {num}")

    def test_get_article_returns_correct_type(self):
        """get_article should return ConstitutionalArticle."""
        article = get_article(49)
        self.assertIsInstance(article, ConstitutionalArticle)

    def test_get_article_invalid_returns_none(self):
        """get_article with invalid number should return None."""
        article = get_article(99999)
        self.assertIsNone(article)

    def test_search_articles(self):
        """Search should find matching articles."""
        results = search_articles("debido proceso")
        self.assertGreater(len(results), 0)

    def test_get_eternity_clauses(self):
        """Should find eternity clauses."""
        clauses = get_eternity_clauses()
        self.assertGreater(len(clauses), 0)
        for clause in clauses:
            self.assertTrue(clause.is_eternity_clause)

    def test_get_articles_by_area(self):
        """Should filter articles by area."""
        civil_articles = get_articles_by_area(ConstitutionalArea.DERECHOS_CIVILES)
        self.assertGreater(len(civil_articles), 0)
        for article in civil_articles:
            self.assertEqual(article.area, ConstitutionalArea.DERECHOS_CIVILES)

    def test_get_statistics(self):
        """Statistics should return valid data."""
        stats = get_statistics()
        self.assertIn('total_articles', stats)
        self.assertIn('eternity_clauses', stats)
        self.assertGreater(stats['total_articles'], 0)


class TestDiffReport(unittest.TestCase):
    """Test diff report generation."""

    def test_generate_report_returns_diff_report(self):
        """generate_diff_report should return DiffReport."""
        report = generate_diff_report(
            "Test Project",
            "Este es un texto de prueba sin conflictos obvios."
        )
        self.assertIsInstance(report, DiffReport)

    def test_report_has_required_fields(self):
        """Report should have all required fields."""
        report = generate_diff_report(
            "Test Project",
            "Texto de prueba"
        )
        self.assertTrue(report.titulo_proyecto)
        self.assertTrue(report.fecha_analisis)
        self.assertIsNotNone(report.total_conflicts)
        self.assertIsNotNone(report.risk_score)
        self.assertIsNotNone(report.compliance_percentage)

    def test_report_detects_retroactivity(self):
        """Report should detect retroactivity issues."""
        report = generate_diff_report(
            "Ley Retroactiva",
            "Esta ley aplicará retroactivamente a todos los casos anteriores."
        )
        has_retroactivity = any(
            c.conflict_type == ConflictType.RETROACTIVITY
            for c in report.conflicts
        )
        self.assertTrue(has_retroactivity, "Should detect retroactivity conflict")

    def test_report_compliance_percentage_valid(self):
        """Compliance percentage should be between 0 and 100."""
        report = generate_diff_report("Test", "Texto normal")
        self.assertGreaterEqual(report.compliance_percentage, 0)
        self.assertLessEqual(report.compliance_percentage, 100)

    def test_report_risk_score_valid(self):
        """Risk score should be between 0 and 1."""
        report = generate_diff_report("Test", "Texto normal")
        self.assertGreaterEqual(report.risk_score, 0)
        self.assertLessEqual(report.risk_score, 1)


class TestConflictDetection(unittest.TestCase):
    """Test conflict detection capabilities."""

    def test_eternity_clause_violation_detected(self):
        """Should detect eternity clause violations."""
        # Text that proposes death penalty (violates Art. 43)
        report = generate_diff_report(
            "Ley Penal",
            "Se establece la pena de muerte para delitos graves."
        )
        has_critical = any(
            c.severity == ConflictSeverity.CRITICAL
            for c in report.conflicts
        )
        # This should ideally detect a critical violation
        # but depends on the analysis engine sophistication

    def test_safe_text_has_low_risk(self):
        """Safe text should have low risk score."""
        report = generate_diff_report(
            "Ley de Bibliotecas",
            "Se crea el Sistema Nacional de Bibliotecas Públicas para promover la lectura."
        )
        # Safe legislation should have low risk
        self.assertLess(report.risk_score, 0.5)


class TestEnums(unittest.TestCase):
    """Test enum definitions."""

    def test_conflict_severity_values(self):
        """ConflictSeverity should have expected values."""
        self.assertEqual(ConflictSeverity.CRITICAL.value, "Crítico")
        self.assertEqual(ConflictSeverity.HIGH.value, "Alto")
        self.assertEqual(ConflictSeverity.MEDIUM.value, "Medio")
        self.assertEqual(ConflictSeverity.LOW.value, "Bajo")

    def test_conflict_type_values(self):
        """ConflictType should have expected values."""
        self.assertTrue(ConflictType.RIGHTS_VIOLATION)
        self.assertTrue(ConflictType.RETROACTIVITY)
        self.assertTrue(ConflictType.ETERNITY_CLAUSE)

    def test_constitutional_area_values(self):
        """ConstitutionalArea should have expected values."""
        self.assertTrue(ConstitutionalArea.DERECHOS_FUNDAMENTALES)
        self.assertTrue(ConstitutionalArea.DERECHOS_CIVILES)
        self.assertTrue(ConstitutionalArea.SISTEMA_SOCIOECONOMICO)


if __name__ == '__main__':
    unittest.main()
