#!/usr/bin/env python3
"""
Unit tests for gaceta_scraper.py - Gaceta Oficial Web Scraper

Tests use mocked HTTP responses to avoid network dependencies.
"""

import unittest
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from gaceta_scraper import (
    GacetaType,
    NormType,
    NormStatus,
    GacetaEntry,
    ScrapedNorm,
    GacetaSearchResult,
    RateLimiter,
    clean_html_text,
    detect_norm_type,
    detect_gaceta_type,
    parse_date,
    parse_gaceta_number,
    get_cache_path,
    is_cache_valid,
    read_cache,
    write_cache,
    clear_cache,
    get_scraper_status,
    CACHE_DIR,
)


class TestEnums(unittest.TestCase):
    """Test enum definitions."""

    def test_gaceta_type_values(self):
        """GacetaType should have expected values."""
        self.assertEqual(GacetaType.ORDINARIA.value, "Gaceta Oficial Ordinaria")
        self.assertEqual(GacetaType.EXTRAORDINARIA.value, "Gaceta Oficial Extraordinaria")
        self.assertEqual(GacetaType.OFICIAL.value, "Gaceta Oficial")

    def test_norm_type_values(self):
        """NormType should have all required types."""
        expected = [
            'CONSTITUCION', 'LEY_ORGANICA', 'LEY_ORDINARIA', 'CODIGO',
            'DECRETO_LEY', 'DECRETO', 'REGLAMENTO', 'RESOLUCION',
            'PROVIDENCIA', 'AVISO', 'OTRO'
        ]
        for name in expected:
            self.assertTrue(hasattr(NormType, name), f"Missing NormType.{name}")

    def test_norm_status_values(self):
        """NormStatus should have expected values."""
        self.assertEqual(NormStatus.VIGENTE.value, "Vigente")
        self.assertEqual(NormStatus.DEROGADA.value, "Derogada")
        self.assertEqual(NormStatus.REFORMADA.value, "Reformada")


class TestDataClasses(unittest.TestCase):
    """Test dataclass structures."""

    def test_gaceta_entry_creation(self):
        """GacetaEntry should be created correctly."""
        entry = GacetaEntry(
            numero="6.152",
            fecha="15-03-2024",
            tipo=GacetaType.EXTRAORDINARIA
        )
        self.assertEqual(entry.numero, "6.152")
        self.assertEqual(entry.fecha, "15-03-2024")
        self.assertEqual(entry.tipo, GacetaType.EXTRAORDINARIA)
        self.assertIsInstance(entry.contenido, list)
        self.assertTrue(entry.scraped_at)  # Auto-generated

    def test_scraped_norm_creation(self):
        """ScrapedNorm should be created correctly."""
        norm = ScrapedNorm(
            nombre="Ley Orgánica del Trabajo",
            tipo=NormType.LEY_ORGANICA,
            gaceta_numero="6.076",
            gaceta_fecha="07-05-2012",
            gaceta_tipo=GacetaType.EXTRAORDINARIA,
            fecha_publicacion="07-05-2012",
            status=NormStatus.VIGENTE
        )
        self.assertEqual(norm.nombre, "Ley Orgánica del Trabajo")
        self.assertEqual(norm.tipo, NormType.LEY_ORGANICA)
        self.assertEqual(norm.status, NormStatus.VIGENTE)

    def test_search_result_creation(self):
        """GacetaSearchResult should be created correctly."""
        result = GacetaSearchResult(
            query="hidrocarburos",
            tipo_norm=NormType.LEY_ORGANICA,
            fecha_desde="01-01-2020",
            fecha_hasta="31-12-2024",
            total_results=5,
            norms=[],
            gacetas=[],
            search_time=1.5
        )
        self.assertEqual(result.query, "hidrocarburos")
        self.assertEqual(result.total_results, 5)
        self.assertFalse(result.cached)


class TestTextParsing(unittest.TestCase):
    """Test text parsing functions."""

    def test_clean_html_text(self):
        """clean_html_text should remove HTML and normalize whitespace."""
        html = "<p>  Hello   <b>World</b>  </p>"
        result = clean_html_text(html)
        self.assertEqual(result, "Hello World")

    def test_clean_html_entities(self):
        """clean_html_text should decode HTML entities."""
        html = "Constitución &amp; Leyes &lt;2024&gt;"
        result = clean_html_text(html)
        self.assertEqual(result, "Constitución & Leyes <2024>")

    def test_detect_norm_type_constitucion(self):
        """detect_norm_type should identify constitution."""
        result = detect_norm_type("Constitución de la República")
        self.assertEqual(result, NormType.CONSTITUCION)

    def test_detect_norm_type_ley_organica(self):
        """detect_norm_type should identify organic laws."""
        result = detect_norm_type("Ley Orgánica del Trabajo")
        self.assertEqual(result, NormType.LEY_ORGANICA)

    def test_detect_norm_type_codigo(self):
        """detect_norm_type should identify codes."""
        result = detect_norm_type("Código Civil de Venezuela")
        self.assertEqual(result, NormType.CODIGO)

    def test_detect_norm_type_decreto(self):
        """detect_norm_type should identify decrees."""
        result = detect_norm_type("Decreto Presidencial N° 123")
        self.assertEqual(result, NormType.DECRETO)

    def test_detect_norm_type_decreto_ley(self):
        """detect_norm_type should identify decree-laws."""
        result = detect_norm_type("Decreto con Rango, Valor y Fuerza de Ley")
        self.assertEqual(result, NormType.DECRETO_LEY)

    def test_detect_gaceta_type_extraordinaria(self):
        """detect_gaceta_type should identify extraordinary."""
        result = detect_gaceta_type("Gaceta Extraordinaria N° 6.152")
        self.assertEqual(result, GacetaType.EXTRAORDINARIA)

    def test_detect_gaceta_type_ordinaria(self):
        """detect_gaceta_type should identify ordinary."""
        result = detect_gaceta_type("Gaceta Ordinaria N° 42.000")
        self.assertEqual(result, GacetaType.ORDINARIA)


class TestDateParsing(unittest.TestCase):
    """Test date parsing functions."""

    def test_parse_date_spanish_format(self):
        """parse_date should handle Spanish format."""
        result = parse_date("15 de marzo de 2024")
        self.assertEqual(result, "15-03-2024")

    def test_parse_date_slash_format(self):
        """parse_date should handle DD/MM/YYYY format."""
        result = parse_date("15/03/2024")
        self.assertEqual(result, "15-03-2024")

    def test_parse_date_iso_format(self):
        """parse_date should handle YYYY-MM-DD format."""
        result = parse_date("2024-03-15")
        self.assertEqual(result, "15-03-2024")

    def test_parse_date_invalid(self):
        """parse_date should return None for invalid dates."""
        result = parse_date("invalid date")
        self.assertIsNone(result)


class TestGacetaNumberParsing(unittest.TestCase):
    """Test Gaceta number parsing."""

    def test_parse_gaceta_number_standard(self):
        """parse_gaceta_number should extract standard number."""
        numero, tipo = parse_gaceta_number("N° 6.152 Extraordinaria")
        self.assertEqual(numero, "6.152")
        self.assertEqual(tipo, GacetaType.EXTRAORDINARIA)

    def test_parse_gaceta_number_with_comma(self):
        """parse_gaceta_number should handle comma separator."""
        numero, tipo = parse_gaceta_number("Nº 6,152 Ordinaria")
        self.assertIn("6", numero)
        self.assertEqual(tipo, GacetaType.ORDINARIA)


class TestCacheManagement(unittest.TestCase):
    """Test cache management functions."""

    def setUp(self):
        """Set up temporary cache directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cache_dir = CACHE_DIR

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_cache_path(self):
        """get_cache_path should return Path object."""
        result = get_cache_path("test_key")
        self.assertIsInstance(result, Path)
        self.assertTrue(result.name.endswith(".json"))

    def test_cache_path_deterministic(self):
        """Same key should give same path."""
        path1 = get_cache_path("test_key")
        path2 = get_cache_path("test_key")
        self.assertEqual(path1, path2)

    def test_different_keys_different_paths(self):
        """Different keys should give different paths."""
        path1 = get_cache_path("key1")
        path2 = get_cache_path("key2")
        self.assertNotEqual(path1, path2)


class TestRateLimiter(unittest.TestCase):
    """Test rate limiter functionality."""

    def test_rate_limiter_creation(self):
        """RateLimiter should be created with correct interval."""
        limiter = RateLimiter(min_interval=1.0)
        self.assertEqual(limiter.min_interval, 1.0)
        self.assertEqual(limiter.last_request, 0.0)

    def test_rate_limiter_wait(self):
        """RateLimiter.wait should update last_request."""
        limiter = RateLimiter(min_interval=0.01)  # Very short for testing
        limiter.wait()
        self.assertGreater(limiter.last_request, 0.0)


class TestScraperStatus(unittest.TestCase):
    """Test scraper status function."""

    def test_get_scraper_status(self):
        """get_scraper_status should return expected keys."""
        status = get_scraper_status()

        expected_keys = [
            'gaceta_url', 'cache_dir', 'cached_items', 'cache_size_kb',
            'cache_expiry_hours', 'rate_limit_seconds', 'norm_types', 'gaceta_types'
        ]

        for key in expected_keys:
            self.assertIn(key, status, f"Missing key: {key}")

    def test_status_norm_types_complete(self):
        """Status should list all norm types."""
        status = get_scraper_status()
        self.assertGreaterEqual(len(status['norm_types']), 10)

    def test_status_gaceta_types_complete(self):
        """Status should list all gaceta types."""
        status = get_scraper_status()
        self.assertEqual(len(status['gaceta_types']), 3)


class TestMockedHTTPFunctions(unittest.TestCase):
    """Test functions that require mocked HTTP responses."""

    @patch('gaceta_scraper.fetch_url')
    def test_search_with_mock_response(self, mock_fetch):
        """Search should work with mocked response."""
        # Import here to use the patched version
        from gaceta_scraper import search_gaceta

        mock_html = """
        <html>
        <body>
            <div class="resultado">
                <h3>Ley Orgánica del Trabajo</h3>
                <p>Gaceta N° 6.076 del 07-05-2012</p>
            </div>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = search_gaceta("trabajo", use_cache=False, max_results=5)

        self.assertIsInstance(result, GacetaSearchResult)
        self.assertEqual(result.query, "trabajo")
        self.assertFalse(result.cached)

    @patch('gaceta_scraper.fetch_url')
    def test_search_handles_none_response(self, mock_fetch):
        """Search should handle None response gracefully."""
        from gaceta_scraper import search_gaceta

        mock_fetch.return_value = None

        result = search_gaceta("test", use_cache=False)

        self.assertIsInstance(result, GacetaSearchResult)
        self.assertEqual(result.total_results, 0)

    @patch('gaceta_scraper.fetch_url')
    def test_verify_norm_publication(self, mock_fetch):
        """verify_norm_publication should return verification result."""
        from gaceta_scraper import verify_norm_publication

        mock_html = """
        <div class="resultado">
            <h3>CRBV</h3>
            <p>Gaceta N° 5.908 del 19-02-2009</p>
        </div>
        """
        mock_fetch.return_value = mock_html

        result = verify_norm_publication("CRBV", gaceta_numero="5.908")

        self.assertIsInstance(result, dict)
        self.assertIn('verified', result)
        self.assertIn('nombre', result)
        self.assertIn('confidence', result)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_html_parsing(self):
        """Functions should handle empty HTML."""
        result = clean_html_text("")
        self.assertEqual(result, "")

    def test_detect_norm_type_unknown(self):
        """detect_norm_type should return OTRO for unknown types."""
        result = detect_norm_type("Some random document")
        self.assertEqual(result, NormType.OTRO)

    def test_parse_date_empty_string(self):
        """parse_date should handle empty string."""
        result = parse_date("")
        self.assertIsNone(result)

    def test_gaceta_entry_auto_timestamp(self):
        """GacetaEntry should auto-generate scraped_at."""
        entry = GacetaEntry(
            numero="6.000",
            fecha="01-01-2024",
            tipo=GacetaType.OFICIAL
        )
        self.assertTrue(entry.scraped_at)
        # Should be a valid ISO timestamp
        datetime.fromisoformat(entry.scraped_at)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def test_full_search_result_serialization(self):
        """Search result should be JSON serializable."""
        norm = ScrapedNorm(
            nombre="Test Norm",
            tipo=NormType.LEY_ORDINARIA,
            gaceta_numero="1.000",
            gaceta_fecha="01-01-2024",
            gaceta_tipo=GacetaType.OFICIAL,
            fecha_publicacion="01-01-2024"
        )

        gaceta = GacetaEntry(
            numero="1.000",
            fecha="01-01-2024",
            tipo=GacetaType.OFICIAL
        )

        # Convert to dict for serialization
        from dataclasses import asdict
        norm_dict = {**asdict(norm), 'tipo': norm.tipo.value,
                     'gaceta_tipo': norm.gaceta_tipo.value,
                     'status': norm.status.value}
        gaceta_dict = {**asdict(gaceta), 'tipo': gaceta.tipo.value}

        # Should not raise
        json.dumps(norm_dict)
        json.dumps(gaceta_dict)


if __name__ == '__main__':
    unittest.main()
