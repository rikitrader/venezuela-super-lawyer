#!/usr/bin/env python3
"""
Unit tests for security.py module.
Tests authentication, access control, and audit logging.
"""

import os
import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from security import (
    get_access_key,
    hash_key,
    log_access,
    get_valid_password_hash,
    is_file_protected,
    authenticate,
    ACCESS_KEY_VAR,
    PASSWORD_HASH_VAR,
    PROTECTED_FILES
)


class TestHashKey(unittest.TestCase):
    """Test cases for hash_key function."""

    def test_hash_returns_string(self):
        """Test that hash_key returns a string."""
        result = hash_key("test_password")
        self.assertIsInstance(result, str)

    def test_hash_length(self):
        """Test that SHA-256 hash has correct length (64 hex chars)."""
        result = hash_key("any_password")
        self.assertEqual(len(result), 64)

    def test_hash_consistency(self):
        """Test that same input produces same hash."""
        hash1 = hash_key("consistent_password")
        hash2 = hash_key("consistent_password")
        self.assertEqual(hash1, hash2)

    def test_hash_different_inputs(self):
        """Test that different inputs produce different hashes."""
        hash1 = hash_key("password1")
        hash2 = hash_key("password2")
        self.assertNotEqual(hash1, hash2)

    def test_hash_empty_string(self):
        """Test hashing empty string."""
        result = hash_key("")
        self.assertEqual(len(result), 64)

    def test_hash_unicode(self):
        """Test hashing unicode characters."""
        result = hash_key("contraseña_ñ_á_é")
        self.assertEqual(len(result), 64)


class TestGetAccessKey(unittest.TestCase):
    """Test cases for get_access_key function."""

    def test_returns_empty_when_not_set(self):
        """Test returns empty string when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the key if it exists
            os.environ.pop(ACCESS_KEY_VAR, None)
            result = get_access_key()
            self.assertEqual(result, "")

    def test_returns_value_when_set(self):
        """Test returns correct value when env var is set."""
        with patch.dict(os.environ, {ACCESS_KEY_VAR: "my_test_key"}):
            result = get_access_key()
            self.assertEqual(result, "my_test_key")


class TestGetValidPasswordHash(unittest.TestCase):
    """Test cases for get_valid_password_hash function."""

    def test_returns_default_when_not_set(self):
        """Test returns default dev hash when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop(PASSWORD_HASH_VAR, None)
            result = get_valid_password_hash()
            # Should return the default dev hash
            self.assertEqual(len(result), 64)

    def test_returns_env_value_when_set(self):
        """Test returns env value when set."""
        custom_hash = "a" * 64
        with patch.dict(os.environ, {PASSWORD_HASH_VAR: custom_hash}):
            result = get_valid_password_hash()
            self.assertEqual(result, custom_hash)


class TestLogAccess(unittest.TestCase):
    """Test cases for log_access function."""

    def test_log_creates_directory(self):
        """Test that log_access creates log directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "logs" / "test_audit.log"
            with patch('security.AUDIT_LOG', log_file):
                log_access("test_action", True, "test details")
                self.assertTrue(log_file.parent.exists())

    def test_log_writes_success(self):
        """Test logging successful access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"
            with patch('security.AUDIT_LOG', log_file):
                log_access("test_action", True, "success details")
                content = log_file.read_text()
                self.assertIn("[SUCCESS]", content)
                self.assertIn("test_action", content)

    def test_log_writes_failure(self):
        """Test logging failed access."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"
            with patch('security.AUDIT_LOG', log_file):
                log_access("failed_action", False, "failure reason")
                content = log_file.read_text()
                self.assertIn("[FAILED]", content)
                self.assertIn("failed_action", content)

    def test_log_includes_timestamp(self):
        """Test that log entries include timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "audit.log"
            with patch('security.AUDIT_LOG', log_file):
                log_access("timestamp_test", True)
                content = log_file.read_text()
                # ISO timestamp format check
                self.assertIn("202", content)  # Year prefix


class TestIsFileProtected(unittest.TestCase):
    """Test cases for is_file_protected function."""

    def test_skill_md_protected(self):
        """Test that SKILL.md is protected."""
        self.assertTrue(is_file_protected("SKILL.md"))

    def test_scripts_protected(self):
        """Test that script files are protected."""
        self.assertTrue(is_file_protected("scripts/report_manager.py"))
        self.assertTrue(is_file_protected("scripts/gaceta_verify.py"))

    def test_reports_protected(self):
        """Test that report files are protected."""
        self.assertTrue(is_file_protected("reportes_legales/test.md"))

    def test_cases_protected(self):
        """Test that case files are protected."""
        self.assertTrue(is_file_protected("cases/test_case/file.md"))

    def test_references_protected(self):
        """Test that reference files are protected."""
        self.assertTrue(is_file_protected("references/crbv_articles.md"))

    def test_templates_protected(self):
        """Test that template files are protected."""
        self.assertTrue(is_file_protected("assets/templates/demanda_civil.md"))

    def test_unprotected_file(self):
        """Test that random files are not protected."""
        self.assertFalse(is_file_protected("random_file.txt"))
        self.assertFalse(is_file_protected("some/other/path.py"))

    def test_readme_not_protected(self):
        """Test that README is not in protected list."""
        # README is typically public
        self.assertFalse(is_file_protected("README.md"))


class TestAuthenticate(unittest.TestCase):
    """Test cases for authenticate function."""

    def test_authenticate_with_valid_password(self):
        """Test authentication with correct password."""
        # The default dev hash is for some password
        # We need to test with the hash that matches
        test_password = "VenezuelaSuperLawyer2024"
        test_hash = hash_key(test_password)

        with patch('security.get_valid_password_hash', return_value=test_hash):
            with patch('security.log_access'):
                result = authenticate(test_password)
                self.assertTrue(result)

    def test_authenticate_with_invalid_password(self):
        """Test authentication with wrong password."""
        with patch('security.log_access'):
            result = authenticate("wrong_password_123")
            self.assertFalse(result)

    def test_authenticate_empty_password(self):
        """Test authentication with empty password."""
        with patch('security.log_access'):
            result = authenticate("")
            self.assertFalse(result)


class TestProtectedFiles(unittest.TestCase):
    """Test cases for PROTECTED_FILES list."""

    def test_protected_files_not_empty(self):
        """Test that protected files list is defined."""
        self.assertGreater(len(PROTECTED_FILES), 0)

    def test_skill_md_in_list(self):
        """Test that SKILL.md is in protected list."""
        self.assertIn("SKILL.md", PROTECTED_FILES)

    def test_patterns_are_strings(self):
        """Test that all patterns are strings."""
        for pattern in PROTECTED_FILES:
            self.assertIsInstance(pattern, str)


class TestSecurityConstants(unittest.TestCase):
    """Test cases for security module constants."""

    def test_access_key_var_defined(self):
        """Test ACCESS_KEY_VAR is defined."""
        self.assertEqual(ACCESS_KEY_VAR, "VSL_ACCESS_KEY")

    def test_password_hash_var_defined(self):
        """Test PASSWORD_HASH_VAR is defined."""
        self.assertEqual(PASSWORD_HASH_VAR, "VSL_PASSWORD_HASH")


if __name__ == '__main__':
    unittest.main()
