#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Security Module
Provides authentication and access control for protected files.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import hashlib
import functools
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
#                         SECURITY CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Environment variables for security
ACCESS_KEY_VAR = "VSL_ACCESS_KEY"
PASSWORD_HASH_VAR = "VSL_PASSWORD_HASH"

# Get password hash from environment (NEVER hardcode in source)
# Default hash is for development only - MUST be set in production
# To generate: python3 -c "import hashlib; print(hashlib.sha256('your-password'.encode()).hexdigest())"
_DEFAULT_DEV_HASH = "cb457be0f71c4d409eeec0146f2baacc33da8f941cb9182680b58805c6b61cee"

def get_valid_password_hash() -> str:
    """Get password hash from environment or use dev default."""
    return os.environ.get(PASSWORD_HASH_VAR, _DEFAULT_DEV_HASH)

# Protected file patterns
PROTECTED_FILES = [
    "SKILL.md",
    "scripts/report_manager.py",
    "scripts/constitutional_test.py",
    "scripts/init_case.py",
    "scripts/gaceta_verify.py",
    "scripts/tsj_search.py",
    "reportes_legales/*.md",
    "cases/**/*",
    "references/*.md",
    "assets/templates/*.md"
]

# Audit log path
AUDIT_LOG = Path(__file__).parent.parent / "logs" / "audit.log"


def get_access_key() -> str:
    """Get the access key from environment."""
    return os.environ.get(ACCESS_KEY_VAR, "")


def hash_key(key: str) -> str:
    """Hash the access key for comparison."""
    return hashlib.sha256(key.encode()).hexdigest()


def log_access(action: str, success: bool, details: str = "") -> None:
    """Log access attempts to audit file."""
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "FAILED"
        log_entry = f"[{timestamp}] [{status}] {action}"
        if details:
            log_entry += f" | {details}"
        log_entry += "\n"

        with open(AUDIT_LOG, "a") as f:
            f.write(log_entry)
    except Exception:
        pass  # Silent fail for logging


def require_auth(func):
    """Decorator to require authentication for protected functions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = get_access_key()

        if not key:
            log_access(f"Call to {func.__name__}", False, "No access key provided")
            print_access_denied("No access key provided. Set VSL_ACCESS_KEY environment variable.")
            sys.exit(1)

        # Verify key against stored hash
        provided_hash = hash_key(key)
        if provided_hash != VALID_PASSWORD_HASH:
            log_access(f"Call to {func.__name__}", False, "Invalid access key")
            print_access_denied("Invalid access key.")
            sys.exit(1)

        log_access(f"Call to {func.__name__}", True)
        return func(*args, **kwargs)

    return wrapper


def print_access_denied(message: str) -> None:
    """Print access denied message with ASCII art."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗   ██╗███████╗██╗                                                     ║
║     ██║   ██║██╔════╝██║                                                     ║
║     ██║   ██║███████╗██║                                                     ║
║     ╚██╗ ██╔╝╚════██║██║                                                     ║
║      ╚████╔╝ ███████║███████╗                                                ║
║       ╚═══╝  ╚══════╝╚══════╝                                                ║
║                                                                              ║
║                    🔒 ACCESS DENIED 🔒                                       ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  This is a PRIVATE application.                                              ║
║                                                                              ║
║  Unauthorized access is prohibited.                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    print(f"  Error: {message}\n")


def print_access_granted() -> None:
    """Print access granted message."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🔓 ACCESS GRANTED 🔓                                  ║
║                    VENEZUELA SUPER LAWYER v2.0                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


def verify_access() -> bool:
    """Verify access key is valid against stored hash."""
    key = get_access_key()

    if not key:
        print_access_denied("VSL_ACCESS_KEY not set. Export VSL_ACCESS_KEY=<password>")
        return False

    # Hash the provided key and compare
    provided_hash = hash_key(key)

    if provided_hash != get_valid_password_hash():
        log_access("Authentication attempt", False, "Invalid password")
        print_access_denied("Invalid access key. Access denied.")
        return False

    log_access("Authentication", True, "Valid credentials")
    print_access_granted()
    return True


def authenticate(password: str = None) -> bool:
    """Authenticate with password directly or from environment."""
    if password:
        provided_hash = hash_key(password)
        if provided_hash == get_valid_password_hash():
            log_access("Direct authentication", True)
            return True
        else:
            log_access("Direct authentication", False, "Invalid password")
            return False
    return verify_access()


def is_file_protected(filepath: str) -> bool:
    """Check if a file is in the protected list."""
    from fnmatch import fnmatch

    filepath = str(filepath)
    for pattern in PROTECTED_FILES:
        if fnmatch(filepath, pattern) or fnmatch(filepath, f"**/{pattern}"):
            return True
    return False


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI interface."""
    parser = argparse.ArgumentParser(
        prog="security.py",
        description="Venezuela Super Lawyer - Security Module",
        epilog="Access control and authentication for protected files"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Verify command
    subparsers.add_parser(
        "verify",
        help="Verify access key and authenticate"
    )

    # Check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check if a file is protected"
    )
    check_parser.add_argument(
        "filepath",
        help="Path to the file to check"
    )

    # Audit command
    audit_parser = subparsers.add_parser(
        "audit",
        help="View audit log"
    )
    audit_parser.add_argument(
        "--tail", "-n",
        type=int,
        default=0,
        help="Show only last N lines"
    )
    audit_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the audit log"
    )

    # Hash command (utility to generate password hashes)
    hash_parser = subparsers.add_parser(
        "hash",
        help="Generate SHA-256 hash for a password"
    )
    hash_parser.add_argument(
        "password",
        nargs="?",
        help="Password to hash (will prompt if not provided)"
    )

    # Version
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser


def main():
    """CLI interface for security module."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "verify":
        verify_access()

    elif args.command == "check":
        if is_file_protected(args.filepath):
            print(f"🔒 PROTECTED: {args.filepath}")
        else:
            print(f"✓ Not protected: {args.filepath}")

    elif args.command == "audit":
        if args.clear:
            if AUDIT_LOG.exists():
                AUDIT_LOG.unlink()
                print("✓ Audit log cleared")
            else:
                print("No audit log to clear")
        elif AUDIT_LOG.exists():
            content = AUDIT_LOG.read_text()
            if args.tail > 0:
                lines = content.strip().split('\n')
                print('\n'.join(lines[-args.tail:]))
            else:
                print(content)
        else:
            print("No audit log found.")

    elif args.command == "hash":
        if args.password:
            password = args.password
        else:
            import getpass
            password = getpass.getpass("Enter password to hash: ")

        hashed = hash_key(password)
        print(f"\nSHA-256 Hash: {hashed}")
        print(f"\nTo use this hash, set the environment variable:")
        print(f"  export {PASSWORD_HASH_VAR}={hashed}")


if __name__ == "__main__":
    main()
