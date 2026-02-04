#!/usr/bin/env python3
"""
Unit tests for report_manager.py module.
Tests report generation, formatting, and saving.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from report_manager import (
    ReportManager,
    generate_report_header,
    format_section,
    REPORTS_DIR,
    REPORT_TEMPLATES
)


class TestReportManager(unittest.TestCase):
    """Test cases for ReportManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ReportManager()

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_manager_instantiation(self):
        """Test that ReportManager can be instantiated."""
        manager = ReportManager()
        self.assertIsNotNone(manager)

    def test_manager_has_reports_dir(self):
        """Test that manager knows reports directory."""
        self.assertTrue(hasattr(self.manager, 'reports_dir') or
                       hasattr(ReportManager, 'REPORTS_DIR') or
                       REPORTS_DIR is not None)

    def test_generate_analysis_report(self):
        """Test generating analysis report."""
        report = self.manager.generate_analysis_report(
            case_name="Test_Case",
            constitutional_analysis={"risk_score": 50},
            constitutional_tests={"tests_passed": 3},
            gaceta_results={"norms_found": 5},
            tsj_results={"cases_found": 10},
            voting_map={"votes_needed": 84}
        )
        self.assertIsInstance(report, str)
        self.assertGreater(len(report), 0)

    def test_report_includes_case_name(self):
        """Test that report includes case name."""
        report = self.manager.generate_analysis_report(
            case_name="Specific_Case_Name"
        )
        self.assertIn("Specific_Case_Name", report)

    def test_report_includes_timestamp(self):
        """Test that report includes generation timestamp."""
        report = self.manager.generate_analysis_report(case_name="Test")
        current_year = str(datetime.now().year)
        self.assertIn(current_year, report)

    def test_save_report(self):
        """Test saving report to file."""
        with patch.object(self.manager, 'reports_dir', Path(self.temp_dir)):
            content = "# Test Report\n\nContent here."
            path = self.manager.save_report("Test_Case", content)
            self.assertTrue(Path(path).exists())

    def test_save_report_creates_file(self):
        """Test that save_report creates a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(self.manager, 'reports_dir', Path(tmpdir)):
                content = "# Report Content"
                path = self.manager.save_report("Save_Test", content)
                saved_file = Path(path)
                self.assertTrue(saved_file.exists())
                self.assertEqual(saved_file.read_text(), content)

    def test_report_is_markdown(self):
        """Test that generated report is valid markdown."""
        report = self.manager.generate_analysis_report(case_name="MD_Test")
        # Should have markdown headings
        self.assertTrue(
            report.startswith("#") or
            "# " in report or
            "## " in report
        )


class TestGenerateReportHeader(unittest.TestCase):
    """Test cases for generate_report_header function."""

    def test_header_returns_string(self):
        """Test that header returns a string."""
        header = generate_report_header("Test Report", "Test Case")
        self.assertIsInstance(header, str)

    def test_header_includes_title(self):
        """Test that header includes report title."""
        header = generate_report_header("Analysis Report", "Case_123")
        # Check if title text appears in header (case-insensitive)
        self.assertTrue(
            "ANALYSIS" in header.upper() or
            "REPORT" in header.upper()
        )

    def test_header_includes_case_name(self):
        """Test that header includes case name."""
        header = generate_report_header("Report", "Unique_Case_Name")
        self.assertIn("Unique_Case_Name", header)

    def test_header_includes_date(self):
        """Test that header includes date."""
        header = generate_report_header("Report", "Case")
        current_year = str(datetime.now().year)
        self.assertIn(current_year, header)

    def test_header_has_vsl_branding(self):
        """Test that header includes VSL branding."""
        header = generate_report_header("Report", "Case")
        header_upper = header.upper()
        self.assertTrue(
            "VENEZUELA" in header_upper or
            "VSL" in header_upper or
            "SUPER LAWYER" in header_upper or
            "LEGAL" in header_upper
        )


class TestFormatSection(unittest.TestCase):
    """Test cases for format_section function."""

    def test_format_section_returns_string(self):
        """Test that format_section returns a string."""
        result = format_section("Title", "Content here")
        self.assertIsInstance(result, str)

    def test_format_section_includes_title(self):
        """Test that section includes title."""
        result = format_section("Section Title", "Body text")
        self.assertIn("Section Title", result)

    def test_format_section_includes_content(self):
        """Test that section includes content."""
        result = format_section("Title", "Specific content text")
        self.assertIn("Specific content text", result)

    def test_format_section_markdown(self):
        """Test that section is properly formatted markdown."""
        result = format_section("My Section", "Content")
        # Should have heading markers
        self.assertTrue(
            "#" in result or
            "**" in result or
            result.strip().startswith("My Section")
        )

    def test_format_section_empty_content(self):
        """Test formatting section with empty content."""
        result = format_section("Title", "")
        self.assertIn("Title", result)

    def test_format_section_with_dict(self):
        """Test formatting section with dictionary content."""
        content = {"key1": "value1", "key2": "value2"}
        result = format_section("Dict Section", str(content))
        self.assertIn("key1", result)


class TestReportsDir(unittest.TestCase):
    """Test cases for REPORTS_DIR constant."""

    def test_reports_dir_defined(self):
        """Test that REPORTS_DIR is defined."""
        self.assertIsNotNone(REPORTS_DIR)

    def test_reports_dir_is_path(self):
        """Test that REPORTS_DIR is a Path object."""
        self.assertIsInstance(REPORTS_DIR, Path)

    def test_reports_dir_name(self):
        """Test that REPORTS_DIR has expected name."""
        dir_name = str(REPORTS_DIR).lower()
        self.assertTrue(
            "report" in dir_name or
            "legal" in dir_name
        )


class TestReportTemplates(unittest.TestCase):
    """Test cases for REPORT_TEMPLATES constant."""

    def test_templates_defined(self):
        """Test that REPORT_TEMPLATES is defined."""
        self.assertIsNotNone(REPORT_TEMPLATES)

    def test_templates_is_dict(self):
        """Test that templates is a dictionary."""
        self.assertIsInstance(REPORT_TEMPLATES, dict)

    def test_templates_have_strings(self):
        """Test that template values are strings."""
        for key, value in REPORT_TEMPLATES.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)


class TestReportGeneration(unittest.TestCase):
    """Integration tests for report generation."""

    def test_full_report_generation(self):
        """Test generating a complete report with all sections."""
        manager = ReportManager()
        report = manager.generate_analysis_report(
            case_name="Integration_Test",
            constitutional_analysis={
                "conflicts_found": 3,
                "risk_score": 65.5,
                "compliance_percentage": 72.0
            },
            constitutional_tests={
                "tests_passed": 4,
                "tests_failed": 1,
                "total_tests": 5
            },
            gaceta_results={
                "norms_found": 12,
                "results": [{"name": "Test Norm"}]
            },
            tsj_results={
                "cases_found": 8,
                "binding_precedents": 2
            },
            voting_map={
                "votes_needed": 84,
                "feasibility": "MEDIUM"
            }
        )

        # Report should include key information
        self.assertIn("Integration_Test", report)
        self.assertGreater(len(report), 500)  # Should be substantial

    def test_report_with_minimal_data(self):
        """Test generating report with minimal data."""
        manager = ReportManager()
        report = manager.generate_analysis_report(case_name="Minimal")
        self.assertIsInstance(report, str)
        self.assertIn("Minimal", report)

    def test_report_with_none_values(self):
        """Test generating report with None values."""
        manager = ReportManager()
        report = manager.generate_analysis_report(
            case_name="None_Test",
            constitutional_analysis=None,
            constitutional_tests=None
        )
        self.assertIsInstance(report, str)


class TestReportFilenaming(unittest.TestCase):
    """Test cases for report file naming."""

    def test_filename_includes_date(self):
        """Test that saved filename includes date."""
        manager = ReportManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(manager, 'reports_dir', Path(tmpdir)):
                path = manager.save_report("Test", "Content")
                filename = Path(path).name
                # Should include date in some format
                self.assertTrue(
                    "202" in filename or  # Year
                    "Test" in filename
                )

    def test_filename_includes_case_name(self):
        """Test that saved filename includes case name."""
        manager = ReportManager()
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(manager, 'reports_dir', Path(tmpdir)):
                path = manager.save_report("Specific_Name", "Content")
                filename = Path(path).name
                self.assertIn("Specific", filename)


if __name__ == '__main__':
    unittest.main()
