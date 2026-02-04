#!/usr/bin/env python3
"""
Unit tests for gaceta_verify.py - Gaceta Oficial Verification
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from gaceta_verify import (
    NormType,
    NormStatus,
    GacetaType,
    GacetaEntry,
    search_norms,
    get_norms_by_type,
    lookup_known_norm,
    get_statistics,
    KNOWN_NORMS
)


class TestGacetaVerify(unittest.TestCase):
    """Test cases for Gaceta verification functionality."""

    def test_database_not_empty(self):
        """Database should have norms."""
        self.assertGreater(len(KNOWN_NORMS), 0, "Database should not be empty")

    def test_database_has_minimum_norms(self):
        """Database should have at least 30 norms."""
        self.assertGreaterEqual(len(KNOWN_NORMS), 30, "Should have at least 30 norms")

    def test_constitution_exists(self):
        """CRBV should be in the database."""
        crbv = lookup_known_norm("CRBV")
        self.assertIsNotNone(crbv, "CRBV should exist")

    def test_search_norms_returns_list(self):
        """Search should return a list."""
        result = search_norms("hidrocarburos")
        self.assertIsInstance(result, list)

    def test_search_norms_finds_results(self):
        """Search should find matching norms."""
        result = search_norms("trabajo")
        self.assertGreater(len(result), 0, "Should find labor-related norms")

    def test_get_norms_by_type(self):
        """Filter by type should work."""
        result = get_norms_by_type(NormType.LEY_ORGANICA.value)
        self.assertGreater(len(result), 0, "Should have organic laws")

    def test_get_statistics(self):
        """Statistics should return valid data."""
        stats = get_statistics()
        self.assertIn('total_norms', stats)
        self.assertIn('by_type', stats)
        self.assertGreater(stats['total_norms'], 0)

    def test_all_norm_types_have_value(self):
        """All NormType enum members should have values."""
        for norm_type in NormType:
            self.assertTrue(norm_type.value)


class TestGacetaEntryStructure(unittest.TestCase):
    """Test norm structure and data integrity."""

    def test_known_norms_not_empty(self):
        """KNOWN_NORMS should have entries."""
        self.assertGreater(len(KNOWN_NORMS), 0)

    def test_entries_have_required_fields(self):
        """Each entry should have required fields."""
        for key, entry in KNOWN_NORMS.items():
            if isinstance(entry, dict):
                self.assertIn('name', entry)
            else:
                self.assertTrue(hasattr(entry, 'nombre') or hasattr(entry, 'name'))

    def test_codes_exist_in_search(self):
        """Major codes should be findable via search."""
        code_terms = ["civil", "comercio", "penal"]
        for term in code_terms:
            result = search_norms(term)
            self.assertGreater(len(result), 0, f"Should find {term}")


class TestNormTypeEnum(unittest.TestCase):
    """Test NormType enum."""

    def test_constitucion_type_exists(self):
        """Constitution type should exist."""
        self.assertEqual(NormType.CONSTITUCION.value, "Constitución")

    def test_ley_organica_type_exists(self):
        """Organic law type should exist."""
        self.assertEqual(NormType.LEY_ORGANICA.value, "Ley Orgánica")

    def test_codigo_type_exists(self):
        """Code type should exist."""
        self.assertEqual(NormType.CODIGO.value, "Código")


class TestNormStatusEnum(unittest.TestCase):
    """Test NormStatus enum."""

    def test_vigente_exists(self):
        """Vigente status should exist."""
        self.assertTrue(NormStatus.VIGENTE)

    def test_derogada_exists(self):
        """Derogada status should exist."""
        self.assertTrue(NormStatus.DEROGADA)


if __name__ == '__main__':
    unittest.main()
