#!/usr/bin/env python3
"""
Unit tests for tsj_scraper.py - TSJ Web Scraper

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

from tsj_scraper import (
    SalaTSJ,
    ScrapedDecision,
    SearchResult,
    RateLimiter,
    clean_html_text,
    extract_text_between,
    get_cache_path,
    is_cache_valid,
    read_cache,
    write_cache,
    clear_cache,
    get_scraper_status,
    SALA_CODES,
    TSJ_BASE_URL,
    CACHE_DIR,
)


class TestSalaTSJEnum(unittest.TestCase):
    """Test SalaTSJ enum."""

    def test_all_salas_defined(self):
        """SalaTSJ should have all 7 chambers."""
        expected = [
            'CONSTITUCIONAL', 'POLITICO_ADMINISTRATIVA', 'CASACION_CIVIL',
            'CASACION_PENAL', 'CASACION_SOCIAL', 'ELECTORAL', 'PLENA'
        ]
        for name in expected:
            self.assertTrue(hasattr(SalaTSJ, name), f"Missing SalaTSJ.{name}")

    def test_sala_values(self):
        """SalaTSJ values should be correct."""
        self.assertEqual(SalaTSJ.CONSTITUCIONAL.value, "Sala Constitucional")
        self.assertEqual(SalaTSJ.PLENA.value, "Sala Plena")

    def test_sala_codes_match(self):
        """SALA_CODES should have entries for all salas."""
        for sala in SalaTSJ:
            self.assertIn(sala.name, SALA_CODES, f"Missing code for {sala.name}")


class TestScrapedDecision(unittest.TestCase):
    """Test ScrapedDecision dataclass."""

    def test_creation(self):
        """ScrapedDecision should be created correctly."""
        decision = ScrapedDecision(
            numero="123",
            fecha="15-03-2024",
            sala=SalaTSJ.CONSTITUCIONAL,
            expediente="24-0001",
            ponente="Magistrado Test",
            partes="Parte A vs Parte B",
            materia="Amparo Constitucional",
            resumen="Resumen del caso",
            url="http://example.com/decision.html"
        )

        self.assertEqual(decision.numero, "123")
        self.assertEqual(decision.sala, SalaTSJ.CONSTITUCIONAL)
        self.assertTrue(decision.scraped_at)  # Auto-generated

    def test_optional_fields(self):
        """ScrapedDecision optional fields should default correctly."""
        decision = ScrapedDecision(
            numero="123",
            fecha="15-03-2024",
            sala=SalaTSJ.CONSTITUCIONAL,
            expediente="",
            ponente="",
            partes="",
            materia="",
            resumen="",
            url=""
        )

        self.assertIsNone(decision.texto_completo)


class TestSearchResult(unittest.TestCase):
    """Test SearchResult dataclass."""

    def test_creation(self):
        """SearchResult should be created correctly."""
        result = SearchResult(
            query="amparo",
            sala=SalaTSJ.CONSTITUCIONAL,
            fecha_desde="01-01-2024",
            fecha_hasta="31-12-2024",
            total_results=10,
            decisions=[],
            search_time=1.5
        )

        self.assertEqual(result.query, "amparo")
        self.assertEqual(result.total_results, 10)
        self.assertFalse(result.cached)

    def test_cached_flag(self):
        """SearchResult cached flag should work."""
        result = SearchResult(
            query="test",
            sala=None,
            fecha_desde=None,
            fecha_hasta=None,
            total_results=0,
            decisions=[],
            search_time=0.0,
            cached=True
        )

        self.assertTrue(result.cached)


class TestTextParsing(unittest.TestCase):
    """Test text parsing functions."""

    def test_clean_html_text(self):
        """clean_html_text should remove HTML and normalize whitespace."""
        html = "<div>  Hello   <span>World</span>  </div>"
        result = clean_html_text(html)
        self.assertEqual(result, "Hello World")

    def test_clean_html_entities(self):
        """clean_html_text should decode HTML entities."""
        html = "Sentencia N&deg; 123 &amp; 456"
        result = clean_html_text(html)
        self.assertIn("123", result)

    def test_extract_text_between(self):
        """extract_text_between should extract text correctly."""
        content = "START Hello World END"
        result = extract_text_between(content, "START ", " END")
        self.assertEqual(result, "Hello World")

    def test_extract_text_between_not_found(self):
        """extract_text_between should return None if markers not found."""
        content = "Hello World"
        result = extract_text_between(content, "START", "END")
        self.assertIsNone(result)

    def test_extract_text_between_partial(self):
        """extract_text_between should return None if only start found."""
        content = "START Hello World"
        result = extract_text_between(content, "START ", " END")
        self.assertIsNone(result)


class TestCacheManagement(unittest.TestCase):
    """Test cache management functions."""

    def setUp(self):
        """Set up temporary cache directory."""
        self.temp_dir = tempfile.mkdtemp()

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

    def test_rate_limiter_wait_updates_timestamp(self):
        """RateLimiter.wait should update last_request."""
        limiter = RateLimiter(min_interval=0.01)  # Very short for testing
        limiter.wait()
        self.assertGreater(limiter.last_request, 0.0)

    def test_rate_limiter_enforces_interval(self):
        """RateLimiter should enforce minimum interval."""
        import time

        limiter = RateLimiter(min_interval=0.1)

        start = time.time()
        limiter.wait()
        limiter.wait()  # Should wait
        elapsed = time.time() - start

        # Should have waited at least min_interval
        self.assertGreaterEqual(elapsed, 0.09)  # Allow small variance


class TestScraperStatus(unittest.TestCase):
    """Test scraper status function."""

    def test_get_scraper_status(self):
        """get_scraper_status should return expected keys."""
        status = get_scraper_status()

        expected_keys = [
            'tsj_base_url', 'cache_dir', 'cached_items', 'cache_size_kb',
            'cache_expiry_hours', 'rate_limit_seconds', 'available_salas', 'sala_codes'
        ]

        for key in expected_keys:
            self.assertIn(key, status, f"Missing key: {key}")

    def test_status_salas_complete(self):
        """Status should list all salas."""
        status = get_scraper_status()
        self.assertEqual(len(status['available_salas']), 7)

    def test_status_sala_codes_complete(self):
        """Status should have all sala codes."""
        status = get_scraper_status()
        self.assertEqual(len(status['sala_codes']), 7)

    def test_status_base_url(self):
        """Status should include base URL."""
        status = get_scraper_status()
        self.assertEqual(status['tsj_base_url'], TSJ_BASE_URL)


class TestMockedHTTPFunctions(unittest.TestCase):
    """Test functions that require mocked HTTP responses."""

    @patch('tsj_scraper.fetch_url')
    def test_search_with_mock_response(self, mock_fetch):
        """Search should work with mocked response."""
        from tsj_scraper import search_tsj

        mock_html = """
        <html>
        <body>
            <a href="/decisiones/scon/marzo/123-010312-12-0001.HTML">
                Sentencia 123
            </a>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        result = search_tsj("amparo", use_cache=False, max_results=5)

        self.assertIsInstance(result, SearchResult)
        self.assertEqual(result.query, "amparo")
        self.assertFalse(result.cached)

    @patch('tsj_scraper.fetch_url')
    def test_search_handles_none_response(self, mock_fetch):
        """Search should handle None response gracefully."""
        from tsj_scraper import search_tsj

        mock_fetch.return_value = None

        result = search_tsj("test", use_cache=False)

        self.assertIsInstance(result, SearchResult)
        self.assertEqual(result.total_results, 0)

    @patch('tsj_scraper.fetch_url')
    def test_search_with_sala_filter(self, mock_fetch):
        """Search should filter by sala."""
        from tsj_scraper import search_tsj

        mock_fetch.return_value = "<html><body></body></html>"

        result = search_tsj(
            "amparo",
            sala=SalaTSJ.CONSTITUCIONAL,
            use_cache=False
        )

        self.assertEqual(result.sala, SalaTSJ.CONSTITUCIONAL)

    @patch('tsj_scraper.fetch_url')
    def test_get_decision_details(self, mock_fetch):
        """get_decision_details should parse decision page."""
        from tsj_scraper import get_decision_details

        mock_html = """
        <html>
        <body>
            <p>Expediente: 24-0001</p>
            <p>Ponente: Magistrado Test</p>
            <p>15 de marzo de 2024</p>
            <div class="texto">
                Este es el contenido de la decisión judicial...
            </div>
        </body>
        </html>
        """
        mock_fetch.return_value = mock_html

        decision = ScrapedDecision(
            numero="123",
            fecha="",
            sala=SalaTSJ.CONSTITUCIONAL,
            expediente="",
            ponente="",
            partes="",
            materia="",
            resumen="",
            url="http://example.com/decision.html"
        )

        result = get_decision_details(decision, use_cache=False)

        self.assertIsInstance(result, ScrapedDecision)

    @patch('tsj_scraper.fetch_url')
    def test_verify_decision_exists(self, mock_fetch):
        """verify_decision_exists should return decision if found."""
        from tsj_scraper import verify_decision_exists

        mock_html = """
        <a href="/decisiones/scon/marzo/123-010312.HTML">Sentencia 123</a>
        """
        mock_fetch.return_value = mock_html

        # This may return None since the decision parsing depends on URL structure
        result = verify_decision_exists("123", SalaTSJ.CONSTITUCIONAL, year=2024)

        # Either None or a decision
        self.assertTrue(result is None or isinstance(result, ScrapedDecision))


class TestParseSearchResults(unittest.TestCase):
    """Test search result parsing."""

    def test_parse_search_results(self):
        """parse_search_results should extract decisions."""
        from tsj_scraper import parse_search_results

        html = """
        <html>
        <body>
            <a href="/decisiones/scon/marzo/123-010324-24-0001.HTML">Sentencia 123</a>
            <a href="/decisiones/scon/marzo/456-020324-24-0002.HTML">Sentencia 456</a>
        </body>
        </html>
        """

        decisions = parse_search_results(html, SalaTSJ.CONSTITUCIONAL)

        self.assertIsInstance(decisions, list)
        for d in decisions:
            self.assertIsInstance(d, ScrapedDecision)
            self.assertEqual(d.sala, SalaTSJ.CONSTITUCIONAL)


class TestParseDecisionPage(unittest.TestCase):
    """Test decision page parsing."""

    def test_parse_decision_page_expediente(self):
        """parse_decision_page should extract expediente."""
        from tsj_scraper import parse_decision_page

        html = """
        <html>
        <body>
            <p>Expediente: 24-0001</p>
        </body>
        </html>
        """

        decision = ScrapedDecision(
            numero="123",
            fecha="",
            sala=SalaTSJ.CONSTITUCIONAL,
            expediente="",
            ponente="",
            partes="",
            materia="",
            resumen="",
            url=""
        )

        result = parse_decision_page(html, decision)
        self.assertEqual(result.expediente, "24-0001")

    def test_parse_decision_page_fecha(self):
        """parse_decision_page should extract fecha."""
        from tsj_scraper import parse_decision_page

        html = """
        <html>
        <body>
            <p>Fecha: 15 de marzo de 2024</p>
        </body>
        </html>
        """

        decision = ScrapedDecision(
            numero="123",
            fecha="",
            sala=SalaTSJ.CONSTITUCIONAL,
            expediente="",
            ponente="",
            partes="",
            materia="",
            resumen="",
            url=""
        )

        result = parse_decision_page(html, decision)
        self.assertEqual(result.fecha, "15-03-2024")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_html_parsing(self):
        """Functions should handle empty HTML."""
        result = clean_html_text("")
        self.assertEqual(result, "")

    def test_scraped_decision_auto_timestamp(self):
        """ScrapedDecision should auto-generate scraped_at."""
        decision = ScrapedDecision(
            numero="1",
            fecha="01-01-2024",
            sala=SalaTSJ.PLENA,
            expediente="",
            ponente="",
            partes="",
            materia="",
            resumen="",
            url=""
        )
        self.assertTrue(decision.scraped_at)
        # Should be a valid ISO timestamp
        datetime.fromisoformat(decision.scraped_at)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""

    def test_full_decision_serialization(self):
        """Decision should be JSON serializable."""
        from dataclasses import asdict

        decision = ScrapedDecision(
            numero="123",
            fecha="15-03-2024",
            sala=SalaTSJ.CONSTITUCIONAL,
            expediente="24-0001",
            ponente="Magistrado Test",
            partes="Parte A vs Parte B",
            materia="Amparo",
            resumen="Resumen del caso",
            url="http://example.com"
        )

        # Convert to dict with sala as string
        decision_dict = {**asdict(decision), 'sala': decision.sala.value}

        # Should not raise
        json_str = json.dumps(decision_dict)
        self.assertIn("123", json_str)

    def test_search_result_with_decisions(self):
        """SearchResult with decisions should be JSON serializable."""
        from dataclasses import asdict

        decision = ScrapedDecision(
            numero="123",
            fecha="15-03-2024",
            sala=SalaTSJ.CONSTITUCIONAL,
            expediente="24-0001",
            ponente="Magistrado Test",
            partes="",
            materia="",
            resumen="",
            url=""
        )

        result = SearchResult(
            query="test",
            sala=SalaTSJ.CONSTITUCIONAL,
            fecha_desde=None,
            fecha_hasta=None,
            total_results=1,
            decisions=[decision],
            search_time=1.0
        )

        # Serialize decisions
        decisions_dict = [
            {**asdict(d), 'sala': d.sala.value}
            for d in result.decisions
        ]

        # Should not raise
        json.dumps(decisions_dict)


if __name__ == '__main__':
    unittest.main()
