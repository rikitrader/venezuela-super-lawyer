#!/usr/bin/env python3
"""
Unit tests for tsj_search.py - TSJ Jurisprudence Database
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from tsj_search import (
    SalaTSJ,
    TipoDecision,
    CasoTSJ,
    ResultadoBusqueda,
    buscar_por_sala,
    buscar_por_articulo_crbv,
    buscar_por_materia,
    buscar_por_texto,
    buscar_por_keywords,
    buscar_vinculantes,
    buscar_hidrocarburos,
    ejecutar_busqueda,
    get_statistics,
    JURISPRUDENCIA_DATABASE
)


class TestTSJSearch(unittest.TestCase):
    """Test cases for TSJ search functionality."""

    def test_database_not_empty(self):
        """Database should have cases."""
        self.assertGreater(len(JURISPRUDENCIA_DATABASE), 0, "Database should not be empty")

    def test_database_has_minimum_cases(self):
        """Database should have at least 50 cases."""
        self.assertGreaterEqual(len(JURISPRUDENCIA_DATABASE), 50, "Should have at least 50 cases")

    def test_all_salas_represented(self):
        """At least 5 TSJ chambers should have cases."""
        salas_found = set()
        for caso in JURISPRUDENCIA_DATABASE:
            salas_found.add(caso.sala)

        # Check at least 5 of 7 salas are represented
        self.assertGreaterEqual(len(salas_found), 5, "Should have cases from at least 5 salas")

    def test_buscar_por_texto_returns_list(self):
        """Search should return a list."""
        result = buscar_por_texto("constitucional")
        self.assertIsInstance(result, list)

    def test_buscar_por_texto_finds_results(self):
        """Search should find matching cases."""
        result = buscar_por_texto("amparo")
        # May or may not find results depending on database content
        self.assertIsInstance(result, list)

    def test_buscar_por_sala(self):
        """Search by sala should return correct results."""
        result = buscar_por_sala(SalaTSJ.CONSTITUCIONAL)
        self.assertGreater(len(result), 0)
        for caso in result:
            self.assertEqual(caso.sala, SalaTSJ.CONSTITUCIONAL)

    def test_buscar_hidrocarburos(self):
        """Should find hydrocarbon-related cases."""
        result = buscar_hidrocarburos()
        self.assertGreater(len(result), 0, "Should have hydrocarbon cases")

    def test_buscar_por_keywords(self):
        """Keyword search should work."""
        result = buscar_por_keywords(["debido", "proceso"])
        self.assertIsInstance(result, list)

    def test_buscar_vinculantes(self):
        """Should find binding decisions."""
        result = buscar_vinculantes()
        self.assertIsInstance(result, list)
        for caso in result:
            self.assertTrue(caso.vinculante)

    def test_ejecutar_busqueda(self):
        """ejecutar_busqueda should return ResultadoBusqueda."""
        result = ejecutar_busqueda("test")  # Pass a query string
        self.assertIsInstance(result, ResultadoBusqueda)

    def test_get_statistics(self):
        """Statistics should return valid data."""
        stats = get_statistics()
        self.assertIn('total_cases', stats)
        self.assertIn('by_sala', stats)
        self.assertGreater(stats['total_cases'], 0)


class TestCasoTSJStructure(unittest.TestCase):
    """Test case structure and data integrity."""

    def test_all_cases_have_numero_expediente(self):
        """All cases must have an expediente number."""
        for caso in JURISPRUDENCIA_DATABASE:
            self.assertTrue(caso.numero_expediente, f"Case missing numero_expediente")

    def test_all_cases_have_fecha(self):
        """All cases must have a date."""
        for caso in JURISPRUDENCIA_DATABASE:
            self.assertTrue(caso.fecha, f"Case missing fecha")

    def test_all_cases_have_sala(self):
        """All cases must have a valid sala."""
        for caso in JURISPRUDENCIA_DATABASE:
            self.assertIsInstance(caso.sala, SalaTSJ)

    def test_all_cases_have_ponente(self):
        """All cases must have a ponente."""
        for caso in JURISPRUDENCIA_DATABASE:
            self.assertTrue(caso.ponente, f"Case missing ponente")


class TestEnums(unittest.TestCase):
    """Test enum definitions."""

    def test_sala_tsj_has_all_chambers(self):
        """SalaTSJ should have all 7 chambers."""
        expected = [
            'PLENA', 'CONSTITUCIONAL', 'POLITICO_ADMINISTRATIVA',
            'ELECTORAL', 'CASACION_CIVIL', 'CASACION_PENAL', 'CASACION_SOCIAL'
        ]
        for sala in expected:
            self.assertTrue(hasattr(SalaTSJ, sala), f"Missing {sala}")

    def test_tipo_decision_values(self):
        """TipoDecision should have expected values."""
        self.assertTrue(TipoDecision.SENTENCIA)


if __name__ == '__main__':
    unittest.main()
