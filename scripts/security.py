#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Security Module
Provides authentication and access control for protected files.
"""

import os
import sys
import hashlib
import functools
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
#                         SECURITY CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Environment variable for access key
ACCESS_KEY_VAR = "VSL_ACCESS_KEY"

# Protected file patterns
PROTECTED_FILES = [
    "SKILL.md",
    "scripts/report_manager.py",
    "scripts/constitutional_test.py",
    "reportes_legales/*.md",
    "cases/**/*"
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

        # In production, compare against stored hash
        # For now, just verify key is set
        if len(key) < 8:
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
    """Verify access key is valid."""
    key = get_access_key()

    if not key:
        print_access_denied("VSL_ACCESS_KEY not set")
        return False

    if len(key) < 8:
        print_access_denied("Invalid access key format")
        return False

    print_access_granted()
    return True


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

def main():
    """CLI interface for security module."""
    if len(sys.argv) < 2:
        print("Venezuela Super Lawyer - Security Module")
        print("\nUsage:")
        print("  python3 security.py verify     # Verify access key")
        print("  python3 security.py check <file>  # Check if file is protected")
        print("  python3 security.py audit      # View audit log")
        return

    command = sys.argv[1]

    if command == "verify":
        verify_access()

    elif command == "check" and len(sys.argv) > 2:
        filepath = sys.argv[2]
        if is_file_protected(filepath):
            print(f"🔒 PROTECTED: {filepath}")
        else:
            print(f"✓ Not protected: {filepath}")

    elif command == "audit":
        if AUDIT_LOG.exists():
            print(AUDIT_LOG.read_text())
        else:
            print("No audit log found.")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
