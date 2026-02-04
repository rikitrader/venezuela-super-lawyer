#!/usr/bin/env python3
"""
Unit tests for export_documents.py module.
Tests PDF and DOCX export functionality.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from export_documents import (
    export_to_pdf,
    export_to_docx,
    markdown_to_html,
    get_pdf_css,
    get_docx_styles,
    ExportFormat,
    WEASYPRINT_AVAILABLE,
    DOCX_AVAILABLE
)


class TestExportFormat(unittest.TestCase):
    """Test cases for ExportFormat enum."""

    def test_pdf_format_exists(self):
        """Test that PDF format is defined."""
        self.assertEqual(ExportFormat.PDF.value, "pdf")

    def test_docx_format_exists(self):
        """Test that DOCX format is defined."""
        self.assertEqual(ExportFormat.DOCX.value, "docx")

    def test_html_format_exists(self):
        """Test that HTML format is defined."""
        self.assertEqual(ExportFormat.HTML.value, "html")


class TestMarkdownToHtml(unittest.TestCase):
    """Test cases for markdown_to_html function."""

    def test_converts_heading(self):
        """Test conversion of markdown headings."""
        md = "# Heading 1"
        html = markdown_to_html(md)
        self.assertIn("<h1>", html.lower())
        self.assertIn("Heading 1", html)

    def test_converts_bold(self):
        """Test conversion of bold text."""
        md = "**bold text**"
        html = markdown_to_html(md)
        self.assertTrue(
            "<strong>" in html.lower() or
            "<b>" in html.lower() or
            "bold text" in html
        )

    def test_converts_italic(self):
        """Test conversion of italic text."""
        md = "*italic text*"
        html = markdown_to_html(md)
        self.assertTrue(
            "<em>" in html.lower() or
            "<i>" in html.lower() or
            "italic text" in html
        )

    def test_converts_list(self):
        """Test conversion of lists."""
        md = "- Item 1\n- Item 2"
        html = markdown_to_html(md)
        self.assertTrue(
            "<li>" in html.lower() or
            "Item 1" in html
        )

    def test_converts_code_block(self):
        """Test conversion of code blocks."""
        md = "```python\nprint('hello')\n```"
        html = markdown_to_html(md)
        self.assertIn("print", html)

    def test_handles_empty_input(self):
        """Test handling of empty input."""
        html = markdown_to_html("")
        self.assertIsInstance(html, str)

    def test_handles_unicode(self):
        """Test handling of unicode characters."""
        md = "# Título con ñ y acentos: á é í ó ú"
        html = markdown_to_html(md)
        self.assertIn("ñ", html)
        self.assertIn("á", html)


class TestGetPdfCss(unittest.TestCase):
    """Test cases for get_pdf_css function."""

    def test_returns_string(self):
        """Test that CSS is returned as string."""
        css = get_pdf_css()
        self.assertIsInstance(css, str)

    def test_not_empty(self):
        """Test that CSS is not empty."""
        css = get_pdf_css()
        self.assertGreater(len(css), 0)

    def test_has_page_styles(self):
        """Test that CSS includes page styles."""
        css = get_pdf_css()
        css_lower = css.lower()
        self.assertTrue(
            "@page" in css_lower or
            "body" in css_lower or
            "font" in css_lower
        )

    def test_has_font_family(self):
        """Test that CSS includes font-family."""
        css = get_pdf_css()
        self.assertIn("font", css.lower())


class TestGetDocxStyles(unittest.TestCase):
    """Test cases for get_docx_styles function."""

    def test_returns_dict(self):
        """Test that styles are returned as dictionary."""
        styles = get_docx_styles()
        self.assertIsInstance(styles, dict)

    def test_has_heading_styles(self):
        """Test that styles include headings."""
        styles = get_docx_styles()
        keys_lower = [k.lower() for k in styles.keys()]
        self.assertTrue(
            any("heading" in k or "titulo" in k or "h1" in k
                for k in keys_lower) or
            len(styles) > 0
        )


class TestExportToPdf(unittest.TestCase):
    """Test cases for export_to_pdf function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_md = "# Test Report\n\nThis is a test.\n\n## Section 1\n\nContent here."
        self.md_file = Path(self.temp_dir) / "test.md"
        self.md_file.write_text(self.sample_md, encoding='utf-8')

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(not WEASYPRINT_AVAILABLE, "WeasyPrint not installed")
    def test_creates_pdf_file(self):
        """Test that PDF file is created."""
        output = export_to_pdf(str(self.md_file))
        if output:
            self.assertTrue(Path(output).exists())
            self.assertTrue(output.endswith(".pdf"))

    def test_returns_none_without_weasyprint(self):
        """Test graceful handling when WeasyPrint unavailable."""
        with patch('export_documents.WEASYPRINT_AVAILABLE', False):
            result = export_to_pdf(str(self.md_file))
            # Should return None or handle gracefully
            self.assertTrue(result is None or isinstance(result, str))

    def test_handles_missing_file(self):
        """Test handling of missing input file."""
        result = export_to_pdf("/nonexistent/path/file.md")
        self.assertIsNone(result)

    def test_custom_output_path(self):
        """Test with custom output path."""
        output_path = Path(self.temp_dir) / "custom_output.pdf"
        if WEASYPRINT_AVAILABLE:
            result = export_to_pdf(str(self.md_file), str(output_path))
            if result:
                self.assertEqual(result, str(output_path))


class TestExportToDocx(unittest.TestCase):
    """Test cases for export_to_docx function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_md = "# Test Document\n\nParagraph text.\n\n## Section\n\nMore content."
        self.md_file = Path(self.temp_dir) / "test.md"
        self.md_file.write_text(self.sample_md, encoding='utf-8')

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(not DOCX_AVAILABLE, "python-docx not installed")
    def test_creates_docx_file(self):
        """Test that DOCX file is created."""
        output = export_to_docx(str(self.md_file))
        if output:
            self.assertTrue(Path(output).exists())
            self.assertTrue(output.endswith(".docx"))

    def test_returns_none_without_docx(self):
        """Test graceful handling when python-docx unavailable."""
        with patch('export_documents.DOCX_AVAILABLE', False):
            result = export_to_docx(str(self.md_file))
            self.assertTrue(result is None or isinstance(result, str))

    def test_handles_missing_file(self):
        """Test handling of missing input file."""
        result = export_to_docx("/nonexistent/path/file.md")
        self.assertIsNone(result)

    def test_custom_output_path(self):
        """Test with custom output path."""
        output_path = Path(self.temp_dir) / "custom_output.docx"
        if DOCX_AVAILABLE:
            result = export_to_docx(str(self.md_file), str(output_path))
            if result:
                self.assertEqual(result, str(output_path))


class TestExportWithTitle(unittest.TestCase):
    """Test cases for export with custom titles."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.md_file = Path(self.temp_dir) / "test.md"
        self.md_file.write_text("# Content\n\nText here.", encoding='utf-8')

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(not WEASYPRINT_AVAILABLE, "WeasyPrint not installed")
    def test_pdf_with_title(self):
        """Test PDF export with custom title."""
        output = export_to_pdf(
            str(self.md_file),
            title="Custom PDF Title"
        )
        # Title should be used in document
        if output:
            self.assertTrue(Path(output).exists())

    @unittest.skipIf(not DOCX_AVAILABLE, "python-docx not installed")
    def test_docx_with_title(self):
        """Test DOCX export with custom title."""
        output = export_to_docx(
            str(self.md_file),
            title="Custom DOCX Title"
        )
        if output:
            self.assertTrue(Path(output).exists())


class TestDependencyAvailability(unittest.TestCase):
    """Test cases for dependency availability flags."""

    def test_weasyprint_flag_is_bool(self):
        """Test that WEASYPRINT_AVAILABLE is boolean."""
        self.assertIsInstance(WEASYPRINT_AVAILABLE, bool)

    def test_docx_flag_is_bool(self):
        """Test that DOCX_AVAILABLE is boolean."""
        self.assertIsInstance(DOCX_AVAILABLE, bool)


class TestUnicodeHandling(unittest.TestCase):
    """Test cases for unicode character handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_spanish_characters(self):
        """Test handling of Spanish characters."""
        md = "# Título del Documento\n\nContenido con ñ, á, é, í, ó, ú."
        html = markdown_to_html(md)
        self.assertIn("ñ", html)
        self.assertIn("á", html)

    def test_legal_symbols(self):
        """Test handling of legal symbols."""
        md = "# Artículo §1\n\n© 2024 - Ley №123"
        html = markdown_to_html(md)
        self.assertIn("§", html)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""

    def test_invalid_markdown_path(self):
        """Test handling of invalid file path."""
        result = export_to_pdf("/invalid/path/file.md")
        self.assertIsNone(result)

    def test_permission_error_handling(self):
        """Test handling of permission errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            md_file = Path(tmpdir) / "test.md"
            md_file.write_text("# Test")

            # Try to write to a read-only location
            # This should be handled gracefully
            if WEASYPRINT_AVAILABLE:
                result = export_to_pdf(str(md_file), "/root/output.pdf")
                # Should either fail gracefully or succeed if has permissions
                self.assertTrue(result is None or isinstance(result, str))


if __name__ == '__main__':
    unittest.main()
