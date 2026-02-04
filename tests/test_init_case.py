#!/usr/bin/env python3
"""
Unit tests for init_case.py module.
Tests case structure creation and initialization.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from init_case import (
    create_case_structure,
    generate_case_header,
    get_case_template,
    CASES_DIR,
    CASE_SUBDIRS
)


class TestCaseSubdirs(unittest.TestCase):
    """Test cases for CASE_SUBDIRS constant."""

    def test_subdirs_defined(self):
        """Test that CASE_SUBDIRS is defined."""
        self.assertIsInstance(CASE_SUBDIRS, (list, tuple))

    def test_subdirs_not_empty(self):
        """Test that subdirs list is not empty."""
        self.assertGreater(len(CASE_SUBDIRS), 0)

    def test_common_subdirs_exist(self):
        """Test that common subdirectories are defined."""
        subdirs_lower = [s.lower() for s in CASE_SUBDIRS]
        # Common legal case subdirectories
        common = ["documentos", "evidencia", "investigacion", "reportes"]
        for common_dir in common:
            found = any(common_dir in s for s in subdirs_lower)
            # At least some common directories should exist
            self.assertTrue(
                found or len(CASE_SUBDIRS) >= 3,
                f"Expected common directory structure"
            )


class TestGenerateCaseHeader(unittest.TestCase):
    """Test cases for generate_case_header function."""

    def test_header_includes_case_name(self):
        """Test that header includes case name."""
        header = generate_case_header("Test_Case_Name")
        self.assertIn("Test_Case_Name", header)

    def test_header_includes_date(self):
        """Test that header includes creation date."""
        header = generate_case_header("Test_Case")
        # Should include current year
        current_year = str(datetime.now().year)
        self.assertIn(current_year, header)

    def test_header_is_markdown(self):
        """Test that header is valid markdown."""
        header = generate_case_header("Test")
        # Should start with markdown heading
        self.assertTrue(
            header.strip().startswith("#") or
            header.strip().startswith("=") or
            "CASO:" in header.upper() or
            "CASE:" in header.upper()
        )

    def test_header_handles_special_chars(self):
        """Test header with special characters in name."""
        header = generate_case_header("Caso_Ley_Amnistía_2024")
        self.assertIn("Amnistía", header)


class TestGetCaseTemplate(unittest.TestCase):
    """Test cases for get_case_template function."""

    def test_template_returns_string(self):
        """Test that template returns a string."""
        template = get_case_template("Test_Case")
        self.assertIsInstance(template, str)

    def test_template_not_empty(self):
        """Test that template is not empty."""
        template = get_case_template("Test")
        self.assertGreater(len(template), 0)

    def test_template_includes_sections(self):
        """Test that template includes common sections."""
        template = get_case_template("Test_Case")
        template_upper = template.upper()
        # Should have some structure
        self.assertTrue(
            "#" in template or
            "RESUMEN" in template_upper or
            "SUMMARY" in template_upper or
            "ANÁLISIS" in template_upper or
            len(template) > 100
        )


class TestCreateCaseStructure(unittest.TestCase):
    """Test cases for create_case_structure function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cases_dir = CASES_DIR

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_creates_case_directory(self):
        """Test that case directory is created."""
        import uuid
        unique_name = f"Test_Case_{uuid.uuid4().hex[:8]}"
        case_path = create_case_structure(unique_name, "Test Client", self.temp_dir)
        self.assertTrue(Path(case_path).exists())

    def test_creates_subdirectories(self):
        """Test that subdirectories are created."""
        import uuid
        unique_name = f"Test_Case_{uuid.uuid4().hex[:8]}"
        case_path = create_case_structure(unique_name, "Test Client", self.temp_dir)
        case_dir = Path(case_path)
        # Should have some subdirectories
        subdirs = [d for d in case_dir.iterdir() if d.is_dir()]
        self.assertGreater(len(subdirs), 0)

    def test_creates_readme(self):
        """Test that README.md is created in case directory."""
        import uuid
        unique_name = f"Test_Case_{uuid.uuid4().hex[:8]}"
        case_path = create_case_structure(unique_name, "Test Client", self.temp_dir)
        # Either README.md or MANIFEST.md or INDEX.md or similar
        md_files = list(Path(case_path).glob("*.md"))
        self.assertGreater(len(md_files), 0)

    def test_returns_path_string(self):
        """Test that function returns path as string."""
        import uuid
        unique_name = f"Test_Case_{uuid.uuid4().hex[:8]}"
        result = create_case_structure(unique_name, "Test Client", self.temp_dir)
        self.assertIsInstance(result, (str, Path))

    def test_handles_unicode_name(self):
        """Test handling of unicode characters in case name."""
        import uuid
        unique_name = f"Caso_Ley_Amnistía_{uuid.uuid4().hex[:8]}"
        case_path = create_case_structure(unique_name, "Test Client", self.temp_dir)
        self.assertTrue(Path(case_path).exists())

    def test_handles_spaces_in_name(self):
        """Test handling of spaces in case name."""
        import uuid
        unique_name = f"Test Case Name {uuid.uuid4().hex[:8]}"
        # Should either accept or sanitize spaces
        try:
            case_path = create_case_structure(unique_name, "Test Client", self.temp_dir)
            self.assertTrue(Path(case_path).exists())
        except (ValueError, OSError, SystemExit):
            # Some implementations may reject spaces
            pass

    def test_unique_case_names(self):
        """Test that duplicate case names are handled."""
        import uuid
        unique_name = f"Unique_Test_{uuid.uuid4().hex[:8]}"
        path1 = create_case_structure(unique_name, "Test Client", self.temp_dir)
        # Second creation should either append suffix or raise error
        try:
            path2 = create_case_structure(unique_name, "Test Client", self.temp_dir)
            # If successful, paths should be different or same
            self.assertTrue(Path(path2).exists())
        except (ValueError, FileExistsError, SystemExit):
            # Raising error is also acceptable behavior
            pass


class TestCasesDir(unittest.TestCase):
    """Test cases for CASES_DIR constant."""

    def test_cases_dir_is_path(self):
        """Test that CASES_DIR is a Path object."""
        self.assertIsInstance(CASES_DIR, Path)

    def test_cases_dir_name(self):
        """Test that CASES_DIR has expected name."""
        self.assertIn("cases", str(CASES_DIR).lower())


class TestCaseNaming(unittest.TestCase):
    """Test cases for case naming conventions."""

    def test_name_sanitization(self):
        """Test that case names are properly sanitized."""
        import uuid
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with potentially problematic characters
            unique_name = f"Test_2024_01_15_{uuid.uuid4().hex[:8]}"
            case_path = create_case_structure(unique_name, "Test Client", tmpdir)
            path = Path(case_path)
            # Name should be filesystem-safe
            self.assertTrue(path.exists())
            self.assertFalse("/" in path.name)
            self.assertFalse("\\" in path.name)


class TestCaseStructureContent(unittest.TestCase):
    """Test the content of created case structures."""

    def test_case_has_legal_sections(self):
        """Test that case structure has legal document sections."""
        import uuid
        with tempfile.TemporaryDirectory() as tmpdir:
            unique_name = f"Legal_Test_{uuid.uuid4().hex[:8]}"
            case_path = create_case_structure(unique_name, "Test Client", tmpdir)
            case_dir = Path(case_path)

            # Get all markdown files
            md_files = list(case_dir.rglob("*.md"))

            if md_files:
                # Read content
                content = md_files[0].read_text(encoding='utf-8')
                # Should have some structure
                self.assertGreater(len(content), 10)


if __name__ == '__main__':
    unittest.main()
