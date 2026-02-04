#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Custom Exception Classes
Standardized exception hierarchy for all VSL scripts.

Version: 1.0.0
"""

__version__ = "1.0.0"


class VSLError(Exception):
    """Base exception for all Venezuela Super Lawyer errors."""

    def __init__(self, message: str, code: str = "VSL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(f"[{code}] {message}")


# ═══════════════════════════════════════════════════════════════════════════════
#                         AUTHENTICATION ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class AuthenticationError(VSLError):
    """Authentication-related errors."""

    def __init__(self, message: str):
        super().__init__(message, "AUTH_ERROR")


class AccessDeniedError(AuthenticationError):
    """Access denied due to invalid credentials."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message)
        self.code = "ACCESS_DENIED"


class MissingCredentialsError(AuthenticationError):
    """Missing required credentials."""

    def __init__(self, credential_name: str = "VSL_ACCESS_KEY"):
        super().__init__(f"Missing required credential: {credential_name}")
        self.code = "MISSING_CREDENTIALS"
        self.credential_name = credential_name


# ═══════════════════════════════════════════════════════════════════════════════
#                         DATABASE ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class DatabaseError(VSLError):
    """Database-related errors."""

    def __init__(self, message: str):
        super().__init__(message, "DB_ERROR")


class ArticleNotFoundError(DatabaseError):
    """Constitutional article not found."""

    def __init__(self, article_number: int):
        super().__init__(f"Article {article_number} not found in database")
        self.code = "ARTICLE_NOT_FOUND"
        self.article_number = article_number


class NormNotFoundError(DatabaseError):
    """Legal norm not found."""

    def __init__(self, norm_name: str):
        super().__init__(f"Norm '{norm_name}' not found in database")
        self.code = "NORM_NOT_FOUND"
        self.norm_name = norm_name


class CaseNotFoundError(DatabaseError):
    """TSJ case not found."""

    def __init__(self, case_id: str):
        super().__init__(f"Case '{case_id}' not found in database")
        self.code = "CASE_NOT_FOUND"
        self.case_id = case_id


# ═══════════════════════════════════════════════════════════════════════════════
#                         SCRAPER ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class ScraperError(VSLError):
    """Web scraping errors."""

    def __init__(self, message: str):
        super().__init__(message, "SCRAPER_ERROR")


class NetworkError(ScraperError):
    """Network connectivity issues."""

    def __init__(self, url: str, reason: str = "Connection failed"):
        super().__init__(f"Failed to fetch {url}: {reason}")
        self.code = "NETWORK_ERROR"
        self.url = url
        self.reason = reason


class RateLimitError(ScraperError):
    """Rate limit exceeded."""

    def __init__(self, url: str, retry_after: int = 60):
        super().__init__(f"Rate limit exceeded for {url}. Retry after {retry_after}s")
        self.code = "RATE_LIMIT"
        self.url = url
        self.retry_after = retry_after


class ParseError(ScraperError):
    """HTML/content parsing error."""

    def __init__(self, message: str, content_type: str = "HTML"):
        super().__init__(f"Failed to parse {content_type}: {message}")
        self.code = "PARSE_ERROR"
        self.content_type = content_type


class CacheError(ScraperError):
    """Cache read/write error."""

    def __init__(self, operation: str, path: str):
        super().__init__(f"Cache {operation} failed for {path}")
        self.code = "CACHE_ERROR"
        self.operation = operation
        self.path = path


# ═══════════════════════════════════════════════════════════════════════════════
#                         VALIDATION ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class ValidationError(VSLError):
    """Input validation errors."""

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class InvalidDateError(ValidationError):
    """Invalid date format."""

    def __init__(self, date_string: str, expected_format: str = "DD-MM-YYYY"):
        super().__init__(f"Invalid date '{date_string}'. Expected format: {expected_format}")
        self.code = "INVALID_DATE"
        self.date_string = date_string
        self.expected_format = expected_format


class InvalidNormTypeError(ValidationError):
    """Invalid norm type specified."""

    def __init__(self, norm_type: str, valid_types: list):
        super().__init__(f"Invalid norm type '{norm_type}'. Valid types: {', '.join(valid_types)}")
        self.code = "INVALID_NORM_TYPE"
        self.norm_type = norm_type
        self.valid_types = valid_types


class InvalidSalaError(ValidationError):
    """Invalid TSJ chamber specified."""

    def __init__(self, sala: str, valid_salas: list):
        super().__init__(f"Invalid sala '{sala}'. Valid salas: {', '.join(valid_salas)}")
        self.code = "INVALID_SALA"
        self.sala = sala
        self.valid_salas = valid_salas


# ═══════════════════════════════════════════════════════════════════════════════
#                         ANALYSIS ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class AnalysisError(VSLError):
    """Legal analysis errors."""

    def __init__(self, message: str):
        super().__init__(message, "ANALYSIS_ERROR")


class ConflictDetectionError(AnalysisError):
    """Error during constitutional conflict detection."""

    def __init__(self, message: str):
        super().__init__(f"Conflict detection failed: {message}")
        self.code = "CONFLICT_DETECTION_ERROR"


class FeasibilityCalculationError(AnalysisError):
    """Error calculating legislative feasibility."""

    def __init__(self, message: str):
        super().__init__(f"Feasibility calculation failed: {message}")
        self.code = "FEASIBILITY_ERROR"


class RiskAssessmentError(AnalysisError):
    """Error during risk assessment."""

    def __init__(self, message: str):
        super().__init__(f"Risk assessment failed: {message}")
        self.code = "RISK_ASSESSMENT_ERROR"


# ═══════════════════════════════════════════════════════════════════════════════
#                         REPORT ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class ReportError(VSLError):
    """Report generation errors."""

    def __init__(self, message: str):
        super().__init__(message, "REPORT_ERROR")


class ReportNotFoundError(ReportError):
    """Report file not found."""

    def __init__(self, report_path: str):
        super().__init__(f"Report not found: {report_path}")
        self.code = "REPORT_NOT_FOUND"
        self.report_path = report_path


class ReportGenerationError(ReportError):
    """Error generating report."""

    def __init__(self, report_type: str, reason: str):
        super().__init__(f"Failed to generate {report_type} report: {reason}")
        self.code = "REPORT_GENERATION_ERROR"
        self.report_type = report_type
        self.reason = reason


# ═══════════════════════════════════════════════════════════════════════════════
#                         FILE ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class FileError(VSLError):
    """File operation errors."""

    def __init__(self, message: str):
        super().__init__(message, "FILE_ERROR")


class FileNotFoundError(FileError):
    """Required file not found."""

    def __init__(self, file_path: str):
        super().__init__(f"File not found: {file_path}")
        self.code = "FILE_NOT_FOUND"
        self.file_path = file_path


class FileWriteError(FileError):
    """Failed to write file."""

    def __init__(self, file_path: str, reason: str = ""):
        message = f"Failed to write file: {file_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)
        self.code = "FILE_WRITE_ERROR"
        self.file_path = file_path


# ═══════════════════════════════════════════════════════════════════════════════
#                         TEMPLATE ERRORS
# ═══════════════════════════════════════════════════════════════════════════════

class TemplateError(VSLError):
    """Template-related errors."""

    def __init__(self, message: str):
        super().__init__(message, "TEMPLATE_ERROR")


class TemplateNotFoundError(TemplateError):
    """Template file not found."""

    def __init__(self, template_name: str):
        super().__init__(f"Template not found: {template_name}")
        self.code = "TEMPLATE_NOT_FOUND"
        self.template_name = template_name


class TemplatePlaceholderError(TemplateError):
    """Missing required placeholder in template."""

    def __init__(self, template_name: str, placeholder: str):
        super().__init__(f"Missing placeholder '{placeholder}' in template '{template_name}'")
        self.code = "TEMPLATE_PLACEHOLDER_ERROR"
        self.template_name = template_name
        self.placeholder = placeholder


# ═══════════════════════════════════════════════════════════════════════════════
#                         UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def format_error_message(error: VSLError, include_code: bool = True) -> str:
    """Format error message for display."""
    if include_code:
        return f"[{error.code}] {error.message}"
    return error.message


def is_recoverable(error: VSLError) -> bool:
    """Check if an error is potentially recoverable."""
    recoverable_codes = {
        "NETWORK_ERROR",
        "RATE_LIMIT",
        "CACHE_ERROR",
        "PARSE_ERROR",
    }
    return error.code in recoverable_codes


def get_error_suggestion(error: VSLError) -> str:
    """Get a helpful suggestion for resolving the error."""
    suggestions = {
        "ACCESS_DENIED": "Verify your VSL_ACCESS_KEY environment variable is set correctly.",
        "MISSING_CREDENTIALS": "Set the VSL_ACCESS_KEY environment variable: export VSL_ACCESS_KEY=<your-key>",
        "NETWORK_ERROR": "Check your internet connection and try again.",
        "RATE_LIMIT": "Wait a moment before retrying. The server is limiting requests.",
        "ARTICLE_NOT_FOUND": "Check the article number. Valid articles are 1-350.",
        "INVALID_DATE": "Use the format DD-MM-YYYY (e.g., 15-03-2024).",
        "CACHE_ERROR": "Try clearing the cache with the --no-cache flag.",
    }
    return suggestions.get(error.code, "Please check the error details and try again.")


# ═══════════════════════════════════════════════════════════════════════════════
#                         EXCEPTION HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

def handle_exception(error: Exception, verbose: bool = False) -> None:
    """Standard exception handler for CLI scripts."""
    import sys

    if isinstance(error, VSLError):
        print(f"\n❌ Error: {error.message}", file=sys.stderr)
        suggestion = get_error_suggestion(error)
        if suggestion:
            print(f"   💡 Suggestion: {suggestion}", file=sys.stderr)
        if verbose:
            print(f"   📋 Code: {error.code}", file=sys.stderr)
    else:
        print(f"\n❌ Unexpected error: {error}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()

    sys.exit(1)


if __name__ == "__main__":
    # Demo/test the exception hierarchy
    print("Venezuela Super Lawyer - Exception Classes")
    print("=" * 50)

    exceptions = [
        AccessDeniedError(),
        MissingCredentialsError(),
        ArticleNotFoundError(999),
        NetworkError("http://example.com", "Timeout"),
        RateLimitError("http://example.com", 60),
        InvalidDateError("2024/01/15"),
        ConflictDetectionError("Analysis timeout"),
    ]

    for exc in exceptions:
        print(f"\n{exc.__class__.__name__}:")
        print(f"  Message: {exc.message}")
        print(f"  Code: {exc.code}")
        print(f"  Suggestion: {get_error_suggestion(exc)}")
        print(f"  Recoverable: {is_recoverable(exc)}")
