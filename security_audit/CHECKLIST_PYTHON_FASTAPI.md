# Security Checklist - Python FastAPI Stack

## Venezuela Super Lawyer Security Audit

**Audit Date:** 2026-02-04
**Auditor:** Security Test Agent
**Stack:** Python + FastAPI + File System

---

## 1. Authentication & Authorization

### API Authentication

- [ ] **AUTH-001** Verify Bearer token validation cannot be bypassed
- [ ] **AUTH-002** Verify X-API-Key header validation
- [ ] **AUTH-003** Test empty/null API key handling
- [ ] **AUTH-004** Test malformed token formats
- [ ] **AUTH-005** Verify DEFAULT_API_KEY is disabled in production
- [ ] **AUTH-006** Test timing attacks on key comparison

### Password/Hash Security

- [ ] **AUTH-007** Verify SHA-256 hashing is used consistently
- [ ] **AUTH-008** Confirm default dev hash is not used in production
- [ ] **AUTH-009** Test password hash comparison timing safety
- [ ] **AUTH-010** Verify environment variable security for secrets

### Session/Token Management

- [ ] **AUTH-011** Verify API keys have proper entropy (secrets.token_urlsafe)
- [ ] **AUTH-012** Test for token prediction/enumeration
- [ ] **AUTH-013** Verify tier-based access controls work correctly

---

## 2. Input Validation & Injection

### Path Traversal

- [ ] **INJ-001** Test case_name parameter for `../` traversal
- [ ] **INJ-002** Test filename parameter for path injection
- [ ] **INJ-003** Test URL-encoded traversal (`%2e%2e%2f`)
- [ ] **INJ-004** Test double-encoding bypass attempts
- [ ] **INJ-005** Test null byte injection (`%00`)
- [ ] **INJ-006** Verify Path.resolve() or similar canonicalization

### Command Injection

- [ ] **INJ-007** Test for shell command injection in any subprocess calls
- [ ] **INJ-008** Verify no os.system() or subprocess.shell=True usage
- [ ] **INJ-009** Test template injection in report generation

### JSON/Data Injection

- [ ] **INJ-010** Test oversized JSON payloads
- [ ] **INJ-011** Test deeply nested JSON structures
- [ ] **INJ-012** Test JSON with special characters
- [ ] **INJ-013** Verify Pydantic validation catches malformed input
- [ ] **INJ-014** Test enum value injection (invalid workflow types)

### Log Injection

- [ ] **INJ-015** Test newline injection in audit log entries
- [ ] **INJ-016** Test ANSI escape sequence injection in logs

---

## 3. Server-Side Request Forgery (SSRF)

### External API Calls

- [ ] **SSRF-001** Verify URL allowlist for external requests
- [ ] **SSRF-002** Test for redirects to internal IPs (127.0.0.1, 169.254.x.x)
- [ ] **SSRF-003** Test for redirects to cloud metadata (169.254.169.254)
- [ ] **SSRF-004** Verify DNS rebinding protections
- [ ] **SSRF-005** Test scheme restrictions (file://, gopher://)

### Live Data Module

- [ ] **SSRF-006** Verify DATA_SOURCE_URLS cannot be overridden
- [ ] **SSRF-007** Test rate limiting on external requests
- [ ] **SSRF-008** Verify timeout handling for slow/hanging connections

---

## 4. Information Disclosure

### Error Handling

- [ ] **INFO-001** Verify stack traces not exposed in production
- [ ] **INFO-002** Test error messages for path disclosure
- [ ] **INFO-003** Verify debug mode is disabled
- [ ] **INFO-004** Test 500 error responses for sensitive info

### File Content Exposure

- [ ] **INFO-005** Test for arbitrary file read via report endpoints
- [ ] **INFO-006** Verify .env files cannot be accessed
- [ ] **INFO-007** Test access to security.py source code
- [ ] **INFO-008** Verify audit.log cannot be read via API

### API Metadata

- [ ] **INFO-009** Review OpenAPI schema for sensitive info
- [ ] **INFO-010** Verify /docs endpoint is protected in production
- [ ] **INFO-011** Test response headers for version disclosure

---

## 5. Rate Limiting & DoS Protection

### Rate Limiter

- [ ] **DOS-001** Verify rate limit enforcement (100 req/hour standard)
- [ ] **DOS-002** Test rate limit bypass via header manipulation
- [ ] **DOS-003** Test rate limit per-user vs per-IP
- [ ] **DOS-004** Verify rate limit window cleanup
- [ ] **DOS-005** Test rate limit persistence across restarts

### Resource Exhaustion

- [ ] **DOS-006** Test large file upload handling
- [ ] **DOS-007** Test memory exhaustion via large JSON
- [ ] **DOS-008** Test CPU exhaustion via ML predictions
- [ ] **DOS-009** Test disk exhaustion via report generation
- [ ] **DOS-010** Verify timeouts on long-running operations

---

## 6. CORS & Security Headers

### CORS Policy

- [ ] **CORS-001** Verify allow_origins is not "*" in production
- [ ] **CORS-002** Test credentials handling with CORS
- [ ] **CORS-003** Verify allowed methods are appropriate
- [ ] **CORS-004** Test preflight request handling

### Security Headers

- [ ] **HDR-001** Verify X-Content-Type-Options: nosniff
- [ ] **HDR-002** Verify X-Frame-Options or CSP frame-ancestors
- [ ] **HDR-003** Verify Strict-Transport-Security (HSTS)
- [ ] **HDR-004** Test Content-Security-Policy headers
- [ ] **HDR-005** Verify X-XSS-Protection (legacy)

---

## 7. File System Security

### File Operations

- [ ] **FS-001** Verify file permissions on cases/ directory
- [ ] **FS-002** Verify file permissions on reportes_legales/
- [ ] **FS-003** Test symlink following behavior
- [ ] **FS-004** Test race conditions in file operations
- [ ] **FS-005** Verify atomic file writes where needed

### Cache Security

- [ ] **FS-006** Verify cache file permissions
- [ ] **FS-007** Test cache poisoning via modified files
- [ ] **FS-008** Verify cache expiration enforcement
- [ ] **FS-009** Test MAX_CACHE_SIZE_MB enforcement

---

## 8. Dependency Security

### Vulnerability Scanning

- [ ] **DEP-001** Run `pip audit` for known vulnerabilities
- [ ] **DEP-002** Run `safety check` for CVE database
- [ ] **DEP-003** Review Snyk/Dependabot alerts
- [ ] **DEP-004** Verify minimum version constraints

### Supply Chain

- [ ] **DEP-005** Verify requirements.txt hash pinning (pip-compile)
- [ ] **DEP-006** Review optional dependency fallbacks
- [ ] **DEP-007** Test behavior when dependencies unavailable

---

## 9. Cryptography

### Hashing

- [ ] **CRYPTO-001** Verify SHA-256 usage is appropriate (not for passwords in prod)
- [ ] **CRYPTO-002** Consider bcrypt/argon2 for password hashing
- [ ] **CRYPTO-003** Verify token generation uses secrets module

### Transport Security

- [ ] **CRYPTO-004** Verify TLS for external API connections
- [ ] **CRYPTO-005** Test certificate validation is enabled
- [ ] **CRYPTO-006** Verify no SSL warnings are suppressed

---

## 10. Business Logic

### Workflow Security

- [ ] **BIZ-001** Verify workflow type validation
- [ ] **BIZ-002** Test unauthorized workflow access
- [ ] **BIZ-003** Verify sector enum validation
- [ ] **BIZ-004** Test analysis with empty/null inputs

### Data Integrity

- [ ] **BIZ-005** Test report overwrite behavior
- [ ] **BIZ-006** Verify case name uniqueness handling
- [ ] **BIZ-007** Test concurrent analysis requests
- [ ] **BIZ-008** Verify TSJ prediction cannot be manipulated

---

## Audit Summary Template

```
┌────────────────────────────────────────────────────────────────┐
│                    SECURITY AUDIT RESULTS                       │
├────────────────────────────────────────────────────────────────┤
│ Total Checks: ___                                               │
│ Passed: ___                                                     │
│ Failed: ___                                                     │
│ N/A: ___                                                        │
├────────────────────────────────────────────────────────────────┤
│ CRITICAL: ___                                                   │
│ HIGH: ___                                                       │
│ MEDIUM: ___                                                     │
│ LOW: ___                                                        │
│ INFO: ___                                                       │
└────────────────────────────────────────────────────────────────┘
```

---

## Remediation Priority

1. **CRITICAL** - Fix immediately before any deployment
2. **HIGH** - Fix before production deployment
3. **MEDIUM** - Fix within sprint
4. **LOW** - Add to backlog
5. **INFO** - Documentation/awareness only
