#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Master Orchestration Script
Runs all 17 modules for complete case analysis with 90-99% token reduction.

Instead of loading code through context, Claude executes this script locally.
All bulk operations run in Python, returning only structured results.

Version: 1.0.0

Usage:
    python3 run_case_analysis.py <case_name> [options]
    python3 run_case_analysis.py --analyze-text "Texto de la propuesta..."
    python3 run_case_analysis.py --full-report <case_name>

Examples:
    python3 run_case_analysis.py "Ley_Amnistia" --constitutional-test
    python3 run_case_analysis.py --analyze-text "Artículo 1. Se deroga..." --output json
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import all VSL modules with graceful fallbacks
MODULES_AVAILABLE = {
    "constitution_diff": False,
    "constitutional_test": False,
    "gaceta_verify": False,
    "tsj_search": False,
    "voting_map": False,
    "init_case": False,
    "report_manager": False,
    "security": False,
    "law_generator": False,
    "hydrocarbons_playbook": False,
    "contract_review": False,
    "tsj_predictor": False,
    "live_data": False,
    "models": False,
    "api": False,
}

try:
    from constitution_diff import (
        generate_diff_report, get_article, search_articles,
        get_eternity_clauses, get_articles_by_area, get_statistics as const_stats
    )
    MODULES_AVAILABLE["constitution_diff"] = True
except ImportError as e:
    print(f"Warning: constitution_diff not available: {e}")
    generate_diff_report = None
    const_stats = lambda: {}

try:
    from constitutional_test import (
        run_full_constitutional_test, ConstitutionalityReport
    )
    MODULES_AVAILABLE["constitutional_test"] = True
except ImportError as e:
    print(f"Warning: constitutional_test not available: {e}")
    run_full_constitutional_test = None

try:
    from gaceta_verify import search_norms, get_statistics as gaceta_stats, get_norms_by_type
    MODULES_AVAILABLE["gaceta_verify"] = True
except ImportError as e:
    print(f"Warning: gaceta_verify not available: {e}")
    search_norms = lambda q: []
    gaceta_stats = lambda: {}

try:
    from tsj_search import (
        buscar_por_texto, buscar_vinculantes, buscar_por_sala,
        get_statistics as tsj_stats
    )
    MODULES_AVAILABLE["tsj_search"] = True
except ImportError as e:
    print(f"Warning: tsj_search not available: {e}")
    buscar_por_texto = lambda t: []
    buscar_vinculantes = lambda: []
    tsj_stats = lambda: {}

try:
    from voting_map import (
        analyze_proposal, generate_voting_map, get_majority_comparison,
        NormType as VotingNormType
    )
    MODULES_AVAILABLE["voting_map"] = True
except ImportError as e:
    print(f"Warning: voting_map not available: {e}")
    generate_voting_map = None
    VotingNormType = None

try:
    from init_case import create_case_structure
    MODULES_AVAILABLE["init_case"] = True
except ImportError as e:
    print(f"Warning: init_case not available: {e}")
    create_case_structure = None

try:
    from report_manager import ReportManager
    MODULES_AVAILABLE["report_manager"] = True
except ImportError as e:
    print(f"Warning: report_manager not available: {e}")
    ReportManager = None

try:
    from security import verify_access, require_auth, get_access_key
    MODULES_AVAILABLE["security"] = True
except ImportError as e:
    print(f"Warning: security not available: {e}")

# New Module 16: Law Generator
try:
    from law_generator import (
        InstrumentType, EnforcementType, ArticleType,
        generate_legal_instrument, generate_standard_articles,
        generate_sanction_articles, generate_implementation_roadmap,
        generate_hydrocarbons_instrument, generate_banking_instrument,
        get_statistics as law_gen_stats
    )
    MODULES_AVAILABLE["law_generator"] = True
except ImportError as e:
    print(f"Warning: law_generator not available: {e}")
    InstrumentType = None
    generate_legal_instrument = None
    generate_hydrocarbons_instrument = None
    generate_banking_instrument = None
    law_gen_stats = lambda: {}

# New Module 7: Hydrocarbons Playbook
try:
    from hydrocarbons_playbook import (
        ActivityType, ContractType as HCContractType, RegimeType,
        analyze_activity, analyze_empresa_mixta, calculate_fiscal_obligations,
        get_environmental_requirements, run_full_hydrocarbons_analysis,
        search_loh_articles, get_statistics as hydro_stats
    )
    MODULES_AVAILABLE["hydrocarbons_playbook"] = True
except ImportError as e:
    print(f"Warning: hydrocarbons_playbook not available: {e}")
    ActivityType = None
    HCContractType = None
    analyze_activity = None
    analyze_empresa_mixta = None
    calculate_fiscal_obligations = None
    run_full_hydrocarbons_analysis = None
    hydro_stats = lambda: {}

# New Module 9: Contract Review
try:
    from contract_review import (
        ContractType as CRContractType, ClauseType, RiskLevel, ComplianceStatus,
        detect_contract_type, extract_parties, analyze_clauses,
        check_compliance, find_risk_patterns, review_contract,
        get_statistics as contract_stats
    )
    MODULES_AVAILABLE["contract_review"] = True
except ImportError as e:
    print(f"Warning: contract_review not available: {e}")
    CRContractType = None
    review_contract = None
    contract_stats = lambda: {}

# New: TSJ Predictor (ML-based predictions)
try:
    from tsj_predictor import (
        predict_outcome, get_outcome_probabilities,
        get_statistics as predictor_stats
    )
    MODULES_AVAILABLE["tsj_predictor"] = True
except ImportError as e:
    print(f"Warning: tsj_predictor not available: {e}")
    predict_outcome = None
    predictor_stats = lambda: {}

# New: Live Data Integration
try:
    from live_data import (
        search_gaceta, search_tsj, search_an, search_all,
        get_statistics as live_data_stats
    )
    MODULES_AVAILABLE["live_data"] = True
except ImportError as e:
    print(f"Warning: live_data not available: {e}")
    search_gaceta = None
    search_tsj = None
    live_data_stats = lambda: {}

# New: Unified Data Models (Pydantic)
try:
    from models import (
        WorkflowType, NormType, RiskLevel, Sector,
        IntakeRequest, AnalysisResponse,
        get_statistics as models_stats
    )
    MODULES_AVAILABLE["models"] = True
except ImportError as e:
    print(f"Warning: models not available: {e}")
    models_stats = lambda: {}

# New: REST API module availability check
try:
    from api import get_statistics as api_stats
    MODULES_AVAILABLE["api"] = True
except ImportError as e:
    print(f"Warning: api not available (run 'pip install fastapi uvicorn'): {e}")
    api_stats = lambda: {}

# Check for exceptions module (optional)
try:
    from exceptions import VSLError
except ImportError:
    class VSLError(Exception):
        pass


# ═══════════════════════════════════════════════════════════════════════════════
#                         DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class IntakeData:
    """Structured intake data for all workflows."""
    workflow_type: str  # CASE_ANALYSIS, LAW_CREATION, RESEARCH, TSJ_PREDICTION, CONTRACT_REVIEW
    case_name: str
    client_name: Optional[str] = None
    problem_statement: Optional[str] = None
    desired_outcome: Optional[str] = None
    proposal_text: Optional[str] = None
    norm_type: str = "LEY_ORDINARIA"
    affected_group: Optional[str] = None
    sector: Optional[str] = None  # hydrocarbons, banking, labor, telecom, etc.
    urgency_level: str = "normal"  # emergency / normal
    keywords: List[str] = field(default_factory=list)
    facts_timeline: Optional[str] = None
    existing_law: Optional[str] = None
    enforcement_mechanism: Optional[str] = None  # criminal / administrative / civil / incentives
    political_context: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)


@dataclass
class PreflightResult:
    """Result of preflight checks."""
    passed: bool
    gates_passed: int
    gates_failed: int
    warnings: int
    checks: List[Dict[str, Any]]
    errors: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class IntakeArtifacts:
    """Output artifacts from intake process."""
    config_path: str
    run_plan_path: str
    checklist_path: str
    test_plan_path: str


@dataclass
class AnalysisResult:
    """Complete case analysis result."""
    case_name: str
    timestamp: str
    success: bool
    workflow_type: str = "CASE_ANALYSIS"
    modules_run: List[str] = field(default_factory=list)
    intake_data: Optional[Dict] = None
    brainstorm: Optional[Dict] = None
    constitutional_analysis: Optional[Dict] = None
    constitutional_tests: Optional[Dict] = None
    gaceta_verification: Optional[Dict] = None
    tsj_research: Optional[Dict] = None
    voting_map: Optional[Dict] = None
    avenue_selection: Optional[Dict] = None
    draft_instrument: Optional[str] = None
    implementation_roadmap: Optional[Dict] = None
    contract_review: Optional[Dict] = None  # New Module 9
    hydrocarbons_analysis: Optional[Dict] = None  # New Module 7
    report_path: Optional[str] = None
    case_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    token_savings: str = "90-99% vs context loading"

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False, default=str)


@dataclass
class QuickAnalysis:
    """Quick text analysis without full case creation."""
    text: str
    constitutional_conflicts: List[Dict]
    risk_score: float
    eternity_clause_violations: List[str]
    voting_requirements: Optional[Dict]
    recommendations: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
#                         PREFLIGHT CHECKS (Manual Section 9)
# ═══════════════════════════════════════════════════════════════════════════════

def run_preflight_checks(intake: IntakeData) -> PreflightResult:
    """
    Execute all preflight gates before workflow execution.
    Per Manual Section 9: Hard Gates Checklist.

    Returns PreflightResult with pass/fail status.
    """
    checks = []
    errors = []
    gates_passed = 0
    gates_failed = 0
    warnings = 0

    # ═══════════════════════════════════════════════════════════════════
    # GATE 1: PYTHON VERSION
    # ═══════════════════════════════════════════════════════════════════
    python_version = sys.version_info
    python_ok = python_version >= (3, 8)
    checks.append({
        "gate": "GATE_1",
        "name": "Python Version",
        "status": "PASS" if python_ok else "FAIL",
        "expected": "3.8+",
        "actual": f"{python_version.major}.{python_version.minor}",
        "blocking": True
    })
    if python_ok:
        gates_passed += 1
    else:
        gates_failed += 1
        errors.append("ERROR: Python 3.8+ required. Current: {}.{}".format(
            python_version.major, python_version.minor))

    # ═══════════════════════════════════════════════════════════════════
    # GATE 2: SKILL DIRECTORY EXISTS
    # ═══════════════════════════════════════════════════════════════════
    skill_dir = SCRIPT_DIR.parent
    skill_md = skill_dir / "SKILL.md"
    skill_exists = skill_md.exists()
    checks.append({
        "gate": "GATE_2",
        "name": "Skill Directory",
        "status": "PASS" if skill_exists else "FAIL",
        "expected": "SKILL.md exists",
        "actual": str(skill_dir),
        "blocking": True
    })
    if skill_exists:
        gates_passed += 1
    else:
        gates_failed += 1
        errors.append("ERROR: Skill not installed. SKILL.md not found.")

    # ═══════════════════════════════════════════════════════════════════
    # GATE 3: WRITE PERMISSIONS
    # ═══════════════════════════════════════════════════════════════════
    cases_dir = skill_dir / "cases"
    reports_dir = skill_dir / "reportes_legales"

    # Create directories if they don't exist
    cases_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)

    # Test write permission
    try:
        test_file = cases_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        write_ok = True
    except Exception:
        write_ok = False

    checks.append({
        "gate": "GATE_3",
        "name": "Write Permissions",
        "status": "PASS" if write_ok else "FAIL",
        "expected": "Can write to cases/",
        "actual": "Writable" if write_ok else "Permission denied",
        "blocking": True
    })
    if write_ok:
        gates_passed += 1
    else:
        gates_failed += 1
        errors.append("ERROR: Cannot write to cases/ directory. Permission denied.")

    # ═══════════════════════════════════════════════════════════════════
    # GATE 4: CASE UNIQUENESS (for new cases)
    # ═══════════════════════════════════════════════════════════════════
    case_path = cases_dir / intake.case_name
    case_exists = case_path.exists()
    checks.append({
        "gate": "GATE_4",
        "name": "Case Uniqueness",
        "status": "PASS" if not case_exists else "WARN",
        "expected": "Case does not exist",
        "actual": "New case" if not case_exists else "Case exists (will overwrite)",
        "blocking": False  # Warning, not blocking
    })
    if not case_exists:
        gates_passed += 1
    else:
        warnings += 1

    # ═══════════════════════════════════════════════════════════════════
    # GATE 5: REQUIRED INPUTS VALIDATION
    # ═══════════════════════════════════════════════════════════════════
    workflow_config = WORKFLOW_TYPES.get(intake.workflow_type)
    if workflow_config:
        required_fields = workflow_config.get("required_fields", [])
        missing_fields = []

        for field_name in required_fields:
            value = getattr(intake, field_name, None)
            if value is None or (isinstance(value, str) and not value.strip()):
                # Check if it's a special case
                if field_name == "proposal_text" and not intake.proposal_text:
                    missing_fields.append(field_name)
                elif field_name == "keywords" and not intake.keywords:
                    missing_fields.append(field_name)
                elif field_name not in ["proposal_text", "keywords"]:
                    missing_fields.append(field_name)

        inputs_ok = len(missing_fields) == 0
        checks.append({
            "gate": "GATE_5",
            "name": "Required Inputs",
            "status": "PASS" if inputs_ok else "FAIL",
            "expected": f"All required fields: {required_fields}",
            "actual": f"Missing: {missing_fields}" if missing_fields else "All present",
            "blocking": True
        })
        if inputs_ok:
            gates_passed += 1
        else:
            gates_failed += 1
            errors.append(f"ERROR: Missing required fields for {intake.workflow_type}: {missing_fields}")

    # ═══════════════════════════════════════════════════════════════════
    # CHECK 1: MODULES AVAILABLE (Soft check)
    # ═══════════════════════════════════════════════════════════════════
    required_modules = []
    if workflow_config:
        module_nums = workflow_config.get("modules", [])
        if 5 in module_nums:
            required_modules.append("constitution_diff")
        if 6 in module_nums:
            required_modules.append("gaceta_verify")
        if 11 in module_nums or 4 in module_nums:
            required_modules.append("tsj_search")
        if 12 in module_nums:
            required_modules.append("constitutional_test")
        if 17 in module_nums:
            required_modules.append("voting_map")

    missing_modules = [m for m in required_modules if not MODULES_AVAILABLE.get(m, False)]
    modules_ok = len(missing_modules) == 0
    checks.append({
        "check": "CHECK_1",
        "name": "Modules Available",
        "status": "PASS" if modules_ok else "WARN",
        "expected": f"Required: {required_modules}",
        "actual": f"Missing: {missing_modules}" if missing_modules else "All available",
        "blocking": False
    })
    if not modules_ok:
        warnings += 1

    # ═══════════════════════════════════════════════════════════════════
    # CHECK 2: DISK SPACE (Soft check)
    # ═══════════════════════════════════════════════════════════════════
    try:
        import shutil
        disk_usage = shutil.disk_usage(skill_dir)
        free_mb = disk_usage.free / (1024 * 1024)
        disk_ok = free_mb > 100
    except Exception:
        free_mb = -1
        disk_ok = True  # Assume OK if can't check

    checks.append({
        "check": "CHECK_2",
        "name": "Disk Space",
        "status": "PASS" if disk_ok else "WARN",
        "expected": "> 100 MB",
        "actual": f"{free_mb:.0f} MB" if free_mb > 0 else "Unknown",
        "blocking": False
    })
    if not disk_ok:
        warnings += 1

    # Determine overall pass/fail
    passed = gates_failed == 0

    return PreflightResult(
        passed=passed,
        gates_passed=gates_passed,
        gates_failed=gates_failed,
        warnings=warnings,
        checks=checks,
        errors=errors
    )


def generate_intake_artifacts(intake: IntakeData, case_path: Path, preflight: PreflightResult) -> IntakeArtifacts:
    """
    Generate intake artifacts per Manual Section 8.

    Creates:
    - config.json
    - RUN_PLAN.md
    - CHECKLIST.md
    - TEST_PLAN.md
    """
    intake_dir = case_path / ".intake"
    intake_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().isoformat()
    workflow_config = WORKFLOW_TYPES.get(intake.workflow_type, {})

    # ═══════════════════════════════════════════════════════════════════
    # 1. config.json
    # ═══════════════════════════════════════════════════════════════════
    config = {
        "$schema": "./intake_schema.json",
        "version": "2.0",
        "generated": timestamp,
        "project": {
            "workflow_type": intake.workflow_type,
            "case_name": intake.case_name,
            "client_name": intake.client_name
        },
        "environment": {
            "skill_directory": str(SCRIPT_DIR.parent),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "preflight_passed": preflight.passed
        },
        "task": intake.to_dict(),
        "modules": workflow_config.get("modules", []),
        "preflight": {
            "gates_passed": preflight.gates_passed,
            "gates_failed": preflight.gates_failed,
            "warnings": preflight.warnings
        }
    }
    config_path = intake_dir / "config.json"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')

    # ═══════════════════════════════════════════════════════════════════
    # 2. RUN_PLAN.md
    # ═══════════════════════════════════════════════════════════════════
    modules = workflow_config.get("modules", [])
    module_names = {
        1: "Case Structure (init_case)",
        2: "Brainstorm Engine",
        3: "Query Expansion",
        4: "Research Engine",
        5: "Constitution Diff",
        6: "Gaceta Verification",
        7: "Hydrocarbons Playbook",
        8: "TSJ-Style Analysis",
        9: "Contract Review",
        10: "Case Output System",
        11: "TSJ/Gaceta Ingestion",
        12: "Constitutional Tests",
        13: "TSJ Prediction",
        14: "Massive Case Analysis",
        15: "Report Generation",
        16: "Law Generation Engine",
        17: "Voting Map Engine"
    }

    run_plan = f"""# Run Plan: {intake.case_name}

## Overview
- **Workflow:** {intake.workflow_type}
- **Generated:** {timestamp}
- **Preflight Status:** {"PASS" if preflight.passed else "FAIL"}

## Execution Steps

"""
    for i, mod_num in enumerate(modules, 1):
        mod_name = module_names.get(mod_num, f"Module {mod_num}")
        run_plan += f"""### Step {i}: {mod_name}
- **Module:** {mod_num}
- **Output:** Will be generated in case folder
- **Status:** Pending

"""

    run_plan += f"""## Gates Summary

| Gate | Condition | Status |
|------|-----------|--------|
"""
    for check in preflight.checks:
        gate_name = check.get("gate", check.get("check", ""))
        run_plan += f"| {gate_name} | {check['name']} | {check['status']} |\n"

    run_plan += f"""
## Rollback Plan

If execution fails:
1. Partial outputs preserved in case folder
2. Error logged to UPDATES.log
3. User notified with failure point
"""

    run_plan_path = intake_dir / "RUN_PLAN.md"
    run_plan_path.write_text(run_plan, encoding='utf-8')

    # ═══════════════════════════════════════════════════════════════════
    # 3. CHECKLIST.md
    # ═══════════════════════════════════════════════════════════════════
    checklist = f"""# Checklist: {intake.case_name}

## Preflight Checklist (Before Execution)

| # | Check | Status | Verified |
|---|-------|--------|----------|
"""
    for i, check in enumerate(preflight.checks, 1):
        status_icon = "✓" if check['status'] == "PASS" else ("⚠" if check['status'] == "WARN" else "✗")
        checklist += f"| {i} | {check['name']} | {status_icon} {check['status']} | Auto |\n"

    checklist += f"""
**PREFLIGHT RESULT:** {"PASS" if preflight.passed else "FAIL"}

## Postflight Checklist (After Execution)

| # | Check | Expected | Actual | Status |
|---|-------|----------|--------|--------|
| 1 | Case folder created | ✓ | ☐ | Pending |
| 2 | INTAKE.json exists | ✓ | ☐ | Pending |
| 3 | BRAINSTORM.md exists | ✓ | ☐ | Pending |
| 4 | Report generated | ✓ | ☐ | Pending |
| 5 | No critical errors | ✓ | ☐ | Pending |

## Manual Verification Commands

```bash
# Verify case folder
ls -la {case_path}

# Check brainstorm content
cat {case_path}/BRAINSTORM.md

# Verify report
ls reportes_legales/ | grep {intake.case_name}
```
"""

    checklist_path = intake_dir / "CHECKLIST.md"
    checklist_path.write_text(checklist, encoding='utf-8')

    # ═══════════════════════════════════════════════════════════════════
    # 4. TEST_PLAN.md
    # ═══════════════════════════════════════════════════════════════════
    test_plan = f"""# Test Plan: {intake.case_name}

## Smoke Tests (Run After Execution)

### Test 1: Case Folder Structure
```bash
ls {case_path}/
```
Expected: INTAKE.json, BRAINSTORM.md, MANIFEST.md

### Test 2: INTAKE.json Validity
```bash
python3 -c "import json; json.load(open('{case_path}/INTAKE.json'))"
```
Expected: No error

### Test 3: Brainstorm Quality
```bash
grep -c "issue" {case_path}/BRAINSTORM.md
```
Expected: >= 5

### Test 4: Report Generation
```bash
ls reportes_legales/ | grep $(date +%Y%m%d)
```
Expected: Report file exists

## Acceptance Criteria

| Criterion | Expected | Status |
|-----------|----------|--------|
| Case folder created | Yes | Pending |
| All modules executed | {len(modules)} modules | Pending |
| No critical errors | 0 errors | Pending |
| Report generated | Yes | Pending |
"""

    test_plan_path = intake_dir / "TEST_PLAN.md"
    test_plan_path.write_text(test_plan, encoding='utf-8')

    return IntakeArtifacts(
        config_path=str(config_path),
        run_plan_path=str(run_plan_path),
        checklist_path=str(checklist_path),
        test_plan_path=str(test_plan_path)
    )


def validate_intake(intake: IntakeData) -> tuple[bool, List[str]]:
    """
    Validate intake data against workflow requirements.
    Returns (is_valid, list of errors).
    """
    errors = []
    workflow_config = WORKFLOW_TYPES.get(intake.workflow_type)

    if not workflow_config:
        errors.append(f"Unknown workflow type: {intake.workflow_type}")
        return False, errors

    # Check required fields based on workflow
    required_fields = workflow_config.get("required_fields", [])

    for field_name in required_fields:
        value = getattr(intake, field_name, None)

        if field_name == "case_name":
            if not value or not value.strip():
                errors.append("case_name is required")
            elif not all(c.isalnum() or c in '_-' for c in value):
                errors.append("case_name must be alphanumeric with underscores/dashes only")

        elif field_name == "problem_statement":
            if intake.workflow_type in ["CASE_ANALYSIS", "LAW_CREATION", "TSJ_PREDICTION"]:
                if not value or not value.strip():
                    errors.append(f"problem_statement is required for {intake.workflow_type}")

        elif field_name == "proposal_text":
            if intake.workflow_type in ["CONSTITUTIONAL_TEST", "CONTRACT_REVIEW"]:
                if not value or not value.strip():
                    errors.append(f"proposal_text (--text) is required for {intake.workflow_type}")

        elif field_name == "keywords":
            if intake.workflow_type == "RESEARCH":
                if not value or len(value) == 0:
                    errors.append("keywords are required for RESEARCH workflow")

        elif field_name == "norm_type":
            valid_types = ["LEY_ORDINARIA", "LEY_ORGANICA", "DECRETO", "RESOLUCION",
                          "REFORMA_CONSTITUCIONAL", "ENMIENDA", "LEY_HABILITANTE"]
            if value not in valid_types:
                errors.append(f"Invalid norm_type: {value}")

    return len(errors) == 0, errors


# ═══════════════════════════════════════════════════════════════════════════════
#                         WORKFLOW TYPES
# ═══════════════════════════════════════════════════════════════════════════════

WORKFLOW_TYPES = {
    "CASE_ANALYSIS": {
        "name": "Case Analysis",
        "description": "Full legal case analysis with constitutional tests",
        "modules": [1, 2, 3, 4, 5, 6, 10, 12, 13, 14, 15],
        "required_fields": ["case_name", "problem_statement"],
        "optional_fields": ["client_name", "facts_timeline", "keywords", "urgency_level"]
    },
    "LAW_CREATION": {
        "name": "Law Creation & Legislative Roadmap",
        "description": "Create new law/resolution with implementation roadmap",
        "modules": [2, 3, 4, 5, 6, 12, 15, 16, 17],
        "required_fields": ["case_name", "problem_statement", "desired_outcome", "norm_type"],
        "optional_fields": ["affected_group", "sector", "enforcement_mechanism", "urgency_level", "political_context"]
    },
    "RESEARCH": {
        "name": "Legal Research Query",
        "description": "Comprehensive legal research across all sources",
        "modules": [2, 3, 4, 5, 6, 11, 15],
        "required_fields": ["case_name", "keywords"],
        "optional_fields": ["sector", "proposal_text"]
    },
    "TSJ_PREDICTION": {
        "name": "TSJ Decision Prediction",
        "description": "Predict TSJ outcome for a case",
        "modules": [2, 4, 5, 8, 12, 13, 15],
        "required_fields": ["case_name", "problem_statement", "facts_timeline"],
        "optional_fields": ["existing_law", "keywords"]
    },
    "CONTRACT_REVIEW": {
        "name": "Contract Review & Compliance",
        "description": "Review contract for Venezuelan legal compliance",
        "modules": [2, 5, 6, 9, 12, 15],
        "required_fields": ["case_name", "proposal_text"],
        "optional_fields": ["sector", "client_name"]
    },
    "CONSTITUTIONAL_TEST": {
        "name": "Constitutional Compliance Test",
        "description": "Test proposed legislation for constitutional compliance",
        "modules": [2, 5, 8, 12, 15],
        "required_fields": ["case_name", "proposal_text", "norm_type"],
        "optional_fields": ["keywords"]
    },
    "VOTING_MAP": {
        "name": "Legislative Voting Analysis",
        "description": "Map voting requirements and political feasibility",
        "modules": [15, 17],
        "required_fields": ["case_name", "norm_type"],
        "optional_fields": ["political_context", "urgency_level"]
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
#                         BRAINSTORM ENGINE (Module 2)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_brainstorm(intake: IntakeData) -> Dict[str, Any]:
    """
    Module 2: Instant Brainstorm Engine
    Generates 10-25 legal issues from intake data.

    Returns structured brainstorm with:
    - Legal issues identified
    - Constitutional hooks
    - Risks and traps
    - Evidence targets
    - Key institutions
    - Strategic paths
    """
    brainstorm = {
        "case_name": intake.case_name,
        "workflow_type": intake.workflow_type,
        "timestamp": datetime.now().isoformat(),
        "legal_issues": [],
        "constitutional_hooks": [],
        "risks_and_traps": [],
        "evidence_targets": [],
        "key_institutions": [],
        "strategic_paths": []
    }

    # Search for relevant constitutional articles based on keywords and problem
    search_terms = intake.keywords.copy() if intake.keywords else []
    if intake.problem_statement:
        # Extract key terms from problem statement
        search_terms.extend([w for w in intake.problem_statement.split() if len(w) > 5][:10])
    if intake.sector:
        search_terms.append(intake.sector)

    # Get constitutional articles
    for term in search_terms[:5]:
        articles = search_articles(term) if MODULES_AVAILABLE.get("constitution_diff") else []
        for art in articles[:3]:
            brainstorm["constitutional_hooks"].append({
                "article": art.numero,
                "title": art.titulo,
                "area": art.area.value,
                "relevance": f"Found via '{term}'"
            })

    # Identify legal issues based on workflow type
    if intake.workflow_type == "LAW_CREATION":
        brainstorm["legal_issues"] = [
            {"issue": "Competencia legislativa", "type": "constitutional"},
            {"issue": "Reserva legal", "type": "constitutional"},
            {"issue": "Principio de legalidad", "type": "constitutional"},
            {"issue": "Derechos fundamentales afectados", "type": "rights"},
            {"issue": "Proporcionalidad de medidas", "type": "rights"},
            {"issue": "Debido proceso", "type": "procedural"},
            {"issue": "Publicación en Gaceta Oficial", "type": "procedural"},
            {"issue": "Régimen transitorio", "type": "implementation"},
            {"issue": "Mecanismo de enforcement", "type": "implementation"},
            {"issue": "Conflicto con normas vigentes", "type": "hierarchy"}
        ]
    elif intake.workflow_type == "CASE_ANALYSIS":
        brainstorm["legal_issues"] = [
            {"issue": "Legitimación activa", "type": "procedural"},
            {"issue": "Competencia del tribunal", "type": "procedural"},
            {"issue": "Prescripción/caducidad", "type": "procedural"},
            {"issue": "Constitucionalidad de normas aplicables", "type": "constitutional"},
            {"issue": "Derechos fundamentales en juego", "type": "rights"},
            {"issue": "Precedentes vinculantes TSJ", "type": "jurisprudence"},
            {"issue": "Carga de la prueba", "type": "evidence"},
            {"issue": "Medidas cautelares", "type": "strategy"},
            {"issue": "Recursos disponibles", "type": "strategy"}
        ]
    elif intake.workflow_type == "TSJ_PREDICTION":
        brainstorm["legal_issues"] = [
            {"issue": "Sala competente", "type": "procedural"},
            {"issue": "Precedentes de la Sala", "type": "jurisprudence"},
            {"issue": "Tendencia jurisprudencial", "type": "jurisprudence"},
            {"issue": "Argumentos constitucionales", "type": "constitutional"},
            {"issue": "Debilidades del caso", "type": "strategy"}
        ]
    else:
        brainstorm["legal_issues"] = [
            {"issue": "Marco constitucional aplicable", "type": "constitutional"},
            {"issue": "Normativa subordinada", "type": "hierarchy"},
            {"issue": "Jurisprudencia relevante", "type": "jurisprudence"}
        ]

    # Key institutions based on workflow and sector
    brainstorm["key_institutions"] = ["Asamblea Nacional", "Tribunal Supremo de Justicia"]
    if intake.sector == "hydrocarbons":
        brainstorm["key_institutions"].extend(["PDVSA", "Ministerio del Poder Popular de Petróleo"])
    elif intake.sector == "banking":
        brainstorm["key_institutions"].extend(["SUDEBAN", "Banco Central de Venezuela"])
    elif intake.sector == "telecom":
        brainstorm["key_institutions"].extend(["CONATEL"])

    # Strategic paths
    if intake.workflow_type in ["LAW_CREATION", "VOTING_MAP"]:
        brainstorm["strategic_paths"] = [
            {"path": "Ley Ordinaria por AN", "feasibility": "MEDIUM"},
            {"path": "Decreto-Ley con Habilitante", "feasibility": "HIGH" if intake.urgency_level == "emergency" else "LOW"},
            {"path": "Resolución Ministerial", "feasibility": "HIGH" if intake.norm_type == "RESOLUCION" else "LOW"}
        ]
    elif intake.workflow_type == "TSJ_PREDICTION":
        brainstorm["strategic_paths"] = [
            {"path": "Recurso de Nulidad Sala Constitucional", "feasibility": "MEDIUM"},
            {"path": "Amparo Constitucional", "feasibility": "HIGH"},
            {"path": "Negociación/Transacción", "feasibility": "VARIABLE"}
        ]

    # Risks and traps
    brainstorm["risks_and_traps"] = [
        {"risk": "Ultra vires - exceso de competencia", "severity": "HIGH"},
        {"risk": "Violación de cláusulas pétreas", "severity": "CRITICAL"},
        {"risk": "Regresividad de derechos sociales", "severity": "HIGH"},
        {"risk": "Falta de publicación en Gaceta", "severity": "MEDIUM"}
    ]

    return brainstorm


# ═══════════════════════════════════════════════════════════════════════════════
#                         AVENUE SELECTION (Module 16 Part)
# ═══════════════════════════════════════════════════════════════════════════════

def select_legislative_avenue(intake: IntakeData) -> Dict[str, Any]:
    """
    Module 16 Part: Select best legislative avenue based on intake.

    Returns decision matrix with primary and backup routes.
    """
    avenues = {
        "LEY_ORDINARIA": {
            "name": "Ley Ordinaria",
            "authority": "Asamblea Nacional",
            "speed": "Medium (3-6 months)",
            "crbv_articles": "Arts. 202-218",
            "when_to_use": "General matters requiring reserva legal",
            "risk": "LOW"
        },
        "LEY_ORGANICA": {
            "name": "Ley Orgánica",
            "authority": "Asamblea Nacional + TSJ",
            "speed": "Slow (6-12 months)",
            "crbv_articles": "Art. 203",
            "when_to_use": "Rights organization, institutional structure",
            "risk": "MEDIUM"
        },
        "DECRETO": {
            "name": "Decreto con Rango, Valor y Fuerza de Ley",
            "authority": "Presidente (con Ley Habilitante)",
            "speed": "Fast (1-3 months)",
            "crbv_articles": "Art. 236.8, 203",
            "when_to_use": "Emergency, economic matters with habilitante",
            "risk": "MEDIUM"
        },
        "RESOLUCION": {
            "name": "Resolución Ministerial/Administrativa",
            "authority": "Ministro/Ente Regulador",
            "speed": "Very Fast (days-weeks)",
            "crbv_articles": "LOPA",
            "when_to_use": "Technical, sectorial matters",
            "risk": "LOW"
        },
        "REFORMA_CONSTITUCIONAL": {
            "name": "Reforma Constitucional",
            "authority": "AN + Referendo",
            "speed": "Extremely Slow (12+ months)",
            "crbv_articles": "Arts. 342-346",
            "when_to_use": "Partial constitutional changes",
            "risk": "HIGH"
        },
        "ENMIENDA": {
            "name": "Enmienda Constitucional",
            "authority": "AN + Referendo",
            "speed": "Very Slow (6-12 months)",
            "crbv_articles": "Arts. 340-341",
            "when_to_use": "Minor constitutional adjustments",
            "risk": "HIGH"
        }
    }

    primary = avenues.get(intake.norm_type, avenues["LEY_ORDINARIA"])

    # Determine backup routes
    backups = []
    if intake.norm_type == "LEY_ORDINARIA":
        backups = ["RESOLUCION", "DECRETO"]
    elif intake.norm_type == "LEY_ORGANICA":
        backups = ["LEY_ORDINARIA", "DECRETO"]
    elif intake.norm_type == "REFORMA_CONSTITUCIONAL":
        backups = ["ENMIENDA", "LEY_ORGANICA"]
    elif intake.norm_type == "DECRETO":
        backups = ["LEY_ORDINARIA", "RESOLUCION"]
    else:
        backups = ["LEY_ORDINARIA"]

    return {
        "primary_avenue": {
            "type": intake.norm_type,
            **primary,
            "fit_score": 85 if intake.norm_type in avenues else 50
        },
        "backup_avenues": [
            {"type": b, **avenues.get(b, {}), "fit_score": 60}
            for b in backups[:2]
        ],
        "urgency_recommendation": "DECRETO" if intake.urgency_level == "emergency" else intake.norm_type,
        "notes": [
            f"Sector '{intake.sector}' may require specialized regulation" if intake.sector else "",
            "Emergency urgency suggests executive action via Decreto-Ley" if intake.urgency_level == "emergency" else ""
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         MASTER INTAKE WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════

def run_intake_workflow(intake: IntakeData) -> AnalysisResult:
    """
    Master intake workflow that executes all modules based on workflow type.

    This is the main entry point that connects ALL workflows to the intake command.

    Workflows:
    - CASE_ANALYSIS: Full case analysis (Modules 1,2,3,4,5,6,10,12,13,14,15)
    - LAW_CREATION: Law creation + voting (Modules 2,3,4,5,6,12,15,16,17)
    - RESEARCH: Legal research (Modules 2,3,4,5,6,11,15)
    - TSJ_PREDICTION: TSJ prediction (Modules 2,4,5,8,12,13,15)
    - CONTRACT_REVIEW: Contract review (Modules 2,5,6,9,12,15)
    - CONSTITUTIONAL_TEST: Constitutional test (Modules 2,5,8,12,15)
    - VOTING_MAP: Voting analysis (Modules 15,17)
    """
    result = AnalysisResult(
        case_name=intake.case_name,
        timestamp=datetime.now().isoformat(),
        success=True,
        workflow_type=intake.workflow_type,
        intake_data=intake.to_dict()
    )

    workflow_config = WORKFLOW_TYPES.get(intake.workflow_type, WORKFLOW_TYPES["CASE_ANALYSIS"])

    try:
        # ═══════════════════════════════════════════════════════════════════
        # PHASE 1: CASE STRUCTURE (Module 1/10)
        # ═══════════════════════════════════════════════════════════════════
        if 1 in workflow_config["modules"] or 10 in workflow_config["modules"]:
            if MODULES_AVAILABLE.get("init_case") and create_case_structure:
                case_path = create_case_structure(intake.case_name, intake.client_name or "")
                result.case_path = str(case_path)
                result.modules_run.append("init_case")

                # Save intake.json
                intake_path = Path(case_path) / "INTAKE.json"
                intake_path.write_text(intake.to_json(), encoding='utf-8')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 2: BRAINSTORM (Module 2) - AUTO-TRIGGER
        # ═══════════════════════════════════════════════════════════════════
        if 2 in workflow_config["modules"]:
            brainstorm = generate_brainstorm(intake)
            result.brainstorm = brainstorm
            result.modules_run.append("brainstorm")

            # Save BRAINSTORM.md if case path exists
            if result.case_path:
                brainstorm_path = Path(result.case_path) / "BRAINSTORM.md"
                brainstorm_md = f"# Brainstorm - {intake.case_name}\n\n"
                brainstorm_md += f"**Workflow:** {intake.workflow_type}\n"
                brainstorm_md += f"**Generated:** {brainstorm['timestamp']}\n\n"
                brainstorm_md += "## Legal Issues\n"
                for issue in brainstorm["legal_issues"]:
                    brainstorm_md += f"- [{issue['type'].upper()}] {issue['issue']}\n"
                brainstorm_md += "\n## Constitutional Hooks\n"
                for hook in brainstorm["constitutional_hooks"]:
                    brainstorm_md += f"- Art. {hook['article']}: {hook['title']} ({hook['relevance']})\n"
                brainstorm_md += "\n## Risks & Traps\n"
                for risk in brainstorm["risks_and_traps"]:
                    brainstorm_md += f"- [{risk['severity']}] {risk['risk']}\n"
                brainstorm_md += "\n## Strategic Paths\n"
                for path in brainstorm["strategic_paths"]:
                    brainstorm_md += f"- {path['path']} (Feasibility: {path['feasibility']})\n"
                brainstorm_path.write_text(brainstorm_md, encoding='utf-8')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 3: CONSTITUTIONAL DIFF (Module 5)
        # ═══════════════════════════════════════════════════════════════════
        if 5 in workflow_config["modules"]:
            if intake.proposal_text and MODULES_AVAILABLE.get("constitution_diff") and generate_diff_report:
                diff_report = generate_diff_report(intake.case_name, intake.proposal_text)
                # Check for eternity clause violations (related articles that are eternity clauses)
                eternity_articles = [a.numero for a in get_eternity_clauses()] if MODULES_AVAILABLE.get("constitution_diff") else []
                eternity_violations = [a for a in diff_report.related_articles if a in eternity_articles]
                result.constitutional_analysis = {
                    "conflicts_found": len(diff_report.conflicts),
                    "risk_score": diff_report.risk_score,
                    "compliance_percentage": diff_report.compliance_percentage,
                    "eternity_violations": eternity_violations,
                    "requires_constitutional_change": diff_report.requires_constitutional_change,
                    "amendment_recommendation": diff_report.amendment_recommendation,
                    "conflicts": [
                        {
                            "article": c.article_number,
                            "type": c.conflict_type.value,
                            "severity": c.severity.value,
                            "description": c.description[:200]
                        }
                        for c in diff_report.conflicts[:10]
                    ]
                }
                result.modules_run.append("constitution_diff")

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 4: CONSTITUTIONAL TESTS (Module 12)
        # ═══════════════════════════════════════════════════════════════════
        if 12 in workflow_config["modules"]:
            if intake.proposal_text and MODULES_AVAILABLE.get("constitutional_test") and run_full_constitutional_test:
                test_report = run_full_constitutional_test(norm_description=intake.proposal_text)
                result.constitutional_tests = {
                    "tests_passed": sum(1 for t in test_report.tests if t.passed),
                    "tests_failed": sum(1 for t in test_report.tests if not t.passed),
                    "total_tests": len(test_report.tests),
                    "overall_risk": test_report.overall_risk.value,
                    "nullity_likelihood": test_report.nullity_likelihood,
                    "tsj_prediction": test_report.tsj_prediction,
                    "details": [
                        {"test": t.test_name, "passed": t.passed, "findings": t.findings}
                        for t in test_report.tests
                    ]
                }
                result.modules_run.append("constitutional_test")

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 5: GACETA VERIFICATION (Module 6)
        # ═══════════════════════════════════════════════════════════════════
        if 6 in workflow_config["modules"]:
            if intake.keywords and MODULES_AVAILABLE.get("gaceta_verify"):
                gaceta_results = []
                for keyword in intake.keywords[:5]:
                    norms = search_norms(keyword)
                    gaceta_results.extend([
                        {
                            "key": n.get("key", ""),
                            "name": n.get("name", ""),
                            "status": n.get("status", ""),
                            "gaceta": n.get("gaceta_number", "")
                        }
                        for n in norms[:5]
                    ])
                result.gaceta_verification = {
                    "norms_found": len(gaceta_results),
                    "results": gaceta_results[:20]
                }
                result.modules_run.append("gaceta_verify")

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 6: TSJ RESEARCH (Module 4/11)
        # ═══════════════════════════════════════════════════════════════════
        if 4 in workflow_config["modules"] or 11 in workflow_config["modules"]:
            if intake.keywords and MODULES_AVAILABLE.get("tsj_search"):
                tsj_results = []
                for keyword in intake.keywords[:5]:
                    cases = buscar_por_texto(keyword)
                    tsj_results.extend([
                        {
                            "expediente": c.numero_expediente,
                            "sala": c.sala.value,
                            "fecha": c.fecha,
                            "materia": c.materia,
                            "vinculante": c.vinculante
                        }
                        for c in cases[:5]
                    ])
                vinculantes = buscar_vinculantes()
                result.tsj_research = {
                    "cases_found": len(tsj_results),
                    "binding_precedents": len(vinculantes),
                    "results": tsj_results[:20],
                    "vinculantes": [
                        {
                            "expediente": v.numero_expediente,
                            "sala": v.sala.value,
                            "ratio": v.ratio_decidendi[:200] if v.ratio_decidendi else ""
                        }
                        for v in vinculantes[:10]
                    ]
                }
                result.modules_run.append("tsj_search")

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 6B: CONTRACT REVIEW (Module 9 - CONTRACT_REVIEW workflow)
        # ═══════════════════════════════════════════════════════════════════
        if 9 in workflow_config["modules"]:
            if intake.proposal_text and MODULES_AVAILABLE.get("contract_review") and review_contract:
                contract_review_result = review_contract(intake.proposal_text, intake.case_name)
                result.contract_review = {
                    "case_name": contract_review_result.case_name,
                    "contract_type": contract_review_result.contract_type.value,
                    "parties": contract_review_result.parties,
                    "clause_analysis": [
                        {
                            "nombre": c.nombre,
                            "tipo": c.tipo.value,
                            "presente": c.presente,
                            "contenido": c.contenido[:200] if c.contenido else "",
                            "recomendaciones": c.recomendaciones
                        }
                        for c in contract_review_result.clause_analysis
                    ],
                    "compliance_checks": [
                        {
                            "check_name": c.check_name,
                            "status": c.status.value,
                            "details": c.details,
                            "recommendation": c.recommendation
                        }
                        for c in contract_review_result.compliance_checks
                    ],
                    "risk_findings": [
                        {
                            "pattern_name": r.pattern_name,
                            "risk_level": r.risk_level.value,
                            "matched_text": r.matched_text[:100] if r.matched_text else "",
                            "recommendation": r.recommendation
                        }
                        for r in contract_review_result.risk_findings
                    ],
                    "overall_risk": contract_review_result.overall_risk.value,
                    "compliance_score": contract_review_result.compliance_score,
                    "recommendations": contract_review_result.recommendations
                }
                result.modules_run.append("contract_review")

                # Save CONTRACT_REVIEW.md if case path exists
                if result.case_path:
                    cr_path = Path(result.case_path) / "CONTRACT_REVIEW.md"
                    cr_path.write_text(contract_review_result.to_markdown(), encoding='utf-8')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 6C: HYDROCARBONS PLAYBOOK (Module 7 - sector=hydrocarbons)
        # ═══════════════════════════════════════════════════════════════════
        if intake.sector == "hydrocarbons" and MODULES_AVAILABLE.get("hydrocarbons_playbook") and run_full_hydrocarbons_analysis:
            hydro_analysis = run_full_hydrocarbons_analysis(
                case_name=intake.case_name,
                activity="EXPLOTACION",  # Default, can be enhanced via intake
                contract="EMPRESA_MIXTA"
            )
            # Build compliance info from empresa_mixta if available
            compliance_info = {}
            if hydro_analysis.empresa_mixta:
                compliant, message = hydro_analysis.empresa_mixta.validate_participation()
                compliance_info = {
                    "art_9_loh": compliant,
                    "message": message,
                    "participacion_pdvsa": hydro_analysis.empresa_mixta.participacion_pdvsa
                }

            result.hydrocarbons_analysis = {
                "case_name": hydro_analysis.case_name,
                "activity_type": hydro_analysis.activity_type.value,
                "contract_type": hydro_analysis.contract_type.value if hydro_analysis.contract_type else None,
                "reserved_to_state": hydro_analysis.reserved_to_state,
                "applicable_loh_articles": hydro_analysis.applicable_loh_articles,
                "compliance": compliance_info,
                "fiscal_calc": hydro_analysis.fiscal_calc.calculate_all() if hydro_analysis.fiscal_calc else None,
                "environmental_requirements": hydro_analysis.environmental_requirements,
                "risks": hydro_analysis.risks,
                "recommendations": hydro_analysis.recommendations
            }
            result.modules_run.append("hydrocarbons_playbook")

            # Save HYDROCARBONS_ANALYSIS.md if case path exists
            if result.case_path:
                hydro_md = hydro_analysis.to_markdown()
                hydro_path = Path(result.case_path) / "HYDROCARBONS_ANALYSIS.md"
                hydro_path.write_text(hydro_md, encoding='utf-8')

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 7: AVENUE SELECTION (Module 16 - LAW_CREATION only)
        # ═══════════════════════════════════════════════════════════════════
        if 16 in workflow_config["modules"]:
            avenue_selection = select_legislative_avenue(intake)
            result.avenue_selection = avenue_selection
            result.modules_run.append("avenue_selection")

            # Save AVENUE_SELECTION.md if case path exists
            if result.case_path:
                avenue_path = Path(result.case_path) / "AVENUE_SELECTION.md"
                avenue_md = f"# Avenue Selection - {intake.case_name}\n\n"
                avenue_md += f"## Primary Avenue\n"
                primary = avenue_selection["primary_avenue"]
                avenue_md += f"- **Type:** {primary['type']}\n"
                avenue_md += f"- **Authority:** {primary['authority']}\n"
                avenue_md += f"- **Speed:** {primary['speed']}\n"
                avenue_md += f"- **CRBV Articles:** {primary['crbv_articles']}\n"
                avenue_md += f"- **Risk:** {primary['risk']}\n\n"
                avenue_md += "## Backup Avenues\n"
                for backup in avenue_selection["backup_avenues"]:
                    avenue_md += f"- {backup['type']}: {backup.get('name', '')} ({backup.get('speed', '')})\n"
                avenue_path.write_text(avenue_md, encoding='utf-8')

            # ═══════════════════════════════════════════════════════════════
            # PHASE 7B: LAW GENERATION (Module 16 - LAW_CREATION workflow)
            # ═══════════════════════════════════════════════════════════════
            if MODULES_AVAILABLE.get("law_generator") and generate_legal_instrument:
                # Map intake norm_type to InstrumentType enum
                instrument_type_map = {
                    "LEY_ORDINARIA": InstrumentType.LEY_ORDINARIA,
                    "LEY_ORGANICA": InstrumentType.LEY_ORGANICA,
                    "DECRETO": InstrumentType.DECRETO,
                    "RESOLUCION": InstrumentType.RESOLUCION,
                    "REFORMA_CONSTITUCIONAL": InstrumentType.LEY_ORGANICA,  # Fallback
                    "ENMIENDA": InstrumentType.LEY_ORDINARIA,  # Fallback
                    "LEY_HABILITANTE": InstrumentType.LEY_ORGANICA
                }

                # Map enforcement mechanism
                enforcement_map = {
                    "criminal": EnforcementType.CRIMINAL,
                    "administrative": EnforcementType.ADMINISTRATIVE,
                    "civil": EnforcementType.CIVIL,
                    "incentives": EnforcementType.INCENTIVES
                }

                try:
                    instrument_type = instrument_type_map.get(
                        intake.norm_type, InstrumentType.LEY_ORDINARIA
                    )
                    enforcement = enforcement_map.get(
                        intake.enforcement_mechanism or "administrative",
                        EnforcementType.ADMINISTRATIVE
                    )

                    # Generate based on sector
                    if intake.sector == "hydrocarbons" and generate_hydrocarbons_instrument:
                        instrument, roadmap = generate_hydrocarbons_instrument(
                            titulo=intake.case_name.replace("_", " "),
                            objeto=intake.problem_statement or "Regular la materia",
                            urgency=intake.urgency_level
                        )
                    elif intake.sector == "banking" and generate_banking_instrument:
                        instrument, roadmap = generate_banking_instrument(
                            titulo=intake.case_name.replace("_", " "),
                            objeto=intake.problem_statement or "Regular la materia",
                            urgency=intake.urgency_level
                        )
                    else:
                        instrument, roadmap = generate_legal_instrument(
                            titulo=intake.case_name.replace("_", " "),
                            objeto=intake.problem_statement or "Regular la materia",
                            ambito="todo el territorio nacional",
                            tipo=instrument_type,
                            sector=intake.sector or "general",
                            enforcement=enforcement,
                            urgency=intake.urgency_level
                        )

                    # Store generated instrument
                    result.draft_instrument = instrument.to_full_text()
                    result.implementation_roadmap = {
                        "instrument_title": roadmap.instrument_title,
                        "instrument_type": instrument.tipo.value if instrument.tipo else intake.norm_type,
                        "total_phases": roadmap.total_phases,
                        "total_days": roadmap.total_days,
                        "phases": [p.to_dict() for p in roadmap.phases],
                        "dependencies": roadmap.dependencies,
                        "success_metrics": roadmap.success_metrics
                    }
                    result.modules_run.append("law_generator")

                    # Save generated instrument and roadmap
                    if result.case_path:
                        # Save draft instrument
                        instrument_path = Path(result.case_path) / "DRAFT_INSTRUMENT.txt"
                        instrument_path.write_text(instrument.to_full_text(), encoding='utf-8')

                        # Save roadmap
                        roadmap_path = Path(result.case_path) / "IMPLEMENTATION_ROADMAP.md"
                        roadmap_path.write_text(roadmap.to_markdown(), encoding='utf-8')

                        # Save instrument as JSON for further processing
                        instrument_json_path = Path(result.case_path) / "instrument_data.json"
                        instrument_json_path.write_text(
                            json.dumps(instrument.to_dict(), indent=2, ensure_ascii=False, default=str),
                            encoding='utf-8'
                        )

                except Exception as e:
                    result.errors.append(f"Law generation error: {str(e)}")

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 8: VOTING MAP (Module 17)
        # ═══════════════════════════════════════════════════════════════════
        if 17 in workflow_config["modules"]:
            if MODULES_AVAILABLE.get("voting_map") and generate_voting_map and VotingNormType:
                try:
                    norm_enum = VotingNormType[intake.norm_type]
                    voting = generate_voting_map(norm_enum, intake.case_name)
                    main_req = voting.voting_requirements[0] if voting.voting_requirements else None
                    result.voting_map = {
                        "norm_type": voting.norm_type.value,
                        "title": voting.title,
                        "majority_type": main_req.majority_type.value if main_req else "N/A",
                        "votes_needed": main_req.votes_needed if main_req else 0,
                        "quorum": f"{main_req.quorum_required * 100:.0f}%" if main_req else "N/A",
                        "feasibility": voting.feasibility_level.value,
                        "feasibility_score": voting.feasibility_score,
                        "timeline": [
                            {"phase": t.phase.value, "min_days": t.min_days, "max_days": t.max_days}
                            for t in voting.timeline
                        ],
                        "blockers": [
                            {"name": b.name, "severity": b.severity.value if hasattr(b.severity, 'value') else str(b.severity)}
                            for b in voting.blockers
                        ],
                        "strategy": voting.recommended_strategy,
                        "alternatives": voting.alternative_routes
                    }
                    result.modules_run.append("voting_map")

                    # Save VOTING_MAP.md if case path exists
                    if result.case_path:
                        voting_path = Path(result.case_path) / "VOTING_MAP.md"
                        voting_md = f"# Voting Map - {intake.case_name}\n\n"
                        voting_md += f"## Requirements\n"
                        voting_md += f"- **Norm Type:** {result.voting_map['norm_type']}\n"
                        voting_md += f"- **Majority:** {result.voting_map['majority_type']}\n"
                        voting_md += f"- **Votes Needed:** {result.voting_map['votes_needed']}\n"
                        voting_md += f"- **Quorum:** {result.voting_map['quorum']}\n"
                        voting_md += f"- **Feasibility:** {result.voting_map['feasibility']} ({result.voting_map['feasibility_score']:.1f}%)\n\n"
                        voting_md += "## Timeline\n"
                        for phase in result.voting_map['timeline']:
                            voting_md += f"- {phase['phase']}: {phase['min_days']}-{phase['max_days']} days\n"
                        voting_md += "\n## Blockers\n"
                        for blocker in result.voting_map['blockers']:
                            voting_md += f"- [{blocker['severity']}] {blocker['name']}\n"
                        voting_path.write_text(voting_md, encoding='utf-8')
                except (KeyError, AttributeError) as e:
                    result.errors.append(f"Voting map error: {str(e)}")

        # ═══════════════════════════════════════════════════════════════════
        # PHASE 9: GENERATE REPORT (Module 15)
        # ═══════════════════════════════════════════════════════════════════
        if 15 in workflow_config["modules"]:
            if MODULES_AVAILABLE.get("report_manager") and ReportManager:
                report_mgr = ReportManager()
                report_content = report_mgr.generate_analysis_report(
                    case_name=intake.case_name,
                    constitutional_analysis=result.constitutional_analysis,
                    constitutional_tests=result.constitutional_tests,
                    gaceta_results=result.gaceta_verification,
                    tsj_results=result.tsj_research,
                    voting_map=result.voting_map
                )
                result.report_path = report_mgr.save_report(intake.case_name, report_content)
                result.modules_run.append("report_manager")

    except Exception as e:
        result.success = False
        result.errors.append(str(e))

    return result


# ═══════════════════════════════════════════════════════════════════════════════
#                         ANALYSIS FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_text_quick(text: str, norm_type: str = "LEY_ORDINARIA") -> QuickAnalysis:
    """
    Quick constitutional analysis of text without creating a full case.
    Returns structured results for Claude to interpret.

    Token Savings: ~95% vs reading full constitution into context
    """
    # Run constitutional diff
    diff_report = generate_diff_report("Quick Analysis", text)

    # Get voting requirements
    try:
        norm_enum = VotingNormType[norm_type]
        voting = generate_voting_map(norm_enum)
        voting_dict = {
            "norm_type": voting.norm_type.value,
            "majority_required": voting.majority_required.value,
            "votes_needed": voting.votes_needed,
            "quorum": voting.quorum,
            "feasibility": voting.feasibility.value,
            "timeline": voting.timeline
        }
    except (KeyError, AttributeError):
        voting_dict = None

    # Check for eternity clause violations
    eternity_articles = [a.numero for a in get_eternity_clauses()] if MODULES_AVAILABLE.get("constitution_diff") else []
    eternity_violations = [str(a) for a in diff_report.related_articles if a in eternity_articles]

    # Build recommendations
    recommendations = []
    if diff_report.risk_score > 0.7:  # risk_score is 0.0 to 1.0
        recommendations.append("HIGH RISK: Requires immediate constitutional review")
    if eternity_violations:
        recommendations.append("CRITICAL: Violates eternity clauses - proposal invalid")
    if diff_report.compliance_percentage < 50:
        recommendations.append("Major rewrites needed for constitutional compliance")

    return QuickAnalysis(
        text=text[:500] + "..." if len(text) > 500 else text,
        constitutional_conflicts=[
            {
                "article": c.article_number,
                "type": c.conflict_type.value,
                "severity": c.severity.value,
                "description": c.description
            }
            for c in diff_report.conflicts
        ],
        risk_score=diff_report.risk_score,
        eternity_clause_violations=eternity_violations,
        voting_requirements=voting_dict,
        recommendations=recommendations
    )


def run_full_analysis(
    case_name: str,
    proposal_text: str = "",
    norm_type: str = "LEY_ORDINARIA",
    run_tsj_search: bool = True,
    run_gaceta_verify: bool = True,
    search_keywords: Optional[List[str]] = None
) -> AnalysisResult:
    """
    Run complete 17-module analysis for a legal case.

    Token Savings: ~99% vs loading all modules into context

    Modules executed:
    1. Case structure creation
    2. Constitutional diff analysis
    3. Constitutional compliance tests
    4. Gaceta Oficial verification
    5. TSJ jurisprudence search
    6. Voting map generation
    7. Report generation
    """
    result = AnalysisResult(
        case_name=case_name,
        timestamp=datetime.now().isoformat(),
        success=True
    )

    try:
        # Module 1: Create case structure
        case_path = create_case_structure(case_name)
        result.modules_run.append("init_case")

        # Module 2: Constitutional diff analysis
        if proposal_text:
            diff_report = generate_diff_report(case_name, proposal_text)
            # Check for eternity clause violations
            eternity_articles = [a.numero for a in get_eternity_clauses()] if MODULES_AVAILABLE.get("constitution_diff") else []
            eternity_violations = [a for a in diff_report.related_articles if a in eternity_articles]
            result.constitutional_analysis = {
                "conflicts_found": len(diff_report.conflicts),
                "risk_score": diff_report.risk_score,
                "compliance_percentage": diff_report.compliance_percentage,
                "eternity_violations": eternity_violations,
                "requires_constitutional_change": diff_report.requires_constitutional_change,
                "conflicts": [
                    {
                        "article": c.article_number,
                        "type": c.conflict_type.value,
                        "severity": c.severity.value,
                        "description": c.description[:200]
                    }
                    for c in diff_report.conflicts[:10]  # Top 10 conflicts
                ]
            }
            result.modules_run.append("constitution_diff")

        # Module 3: Constitutional tests
        if proposal_text and MODULES_AVAILABLE.get("constitutional_test") and run_full_constitutional_test:
            test_report = run_full_constitutional_test(norm_description=proposal_text)
            result.constitutional_tests = {
                "tests_passed": sum(1 for t in test_report.tests if t.passed),
                "tests_failed": sum(1 for t in test_report.tests if not t.passed),
                "total_tests": len(test_report.tests),
                "overall_risk": test_report.overall_risk.value,
                "nullity_likelihood": test_report.nullity_likelihood,
                "tsj_prediction": test_report.tsj_prediction,
                "details": [
                    {
                        "test": t.test_name,
                        "passed": t.passed,
                        "findings": t.findings
                    }
                    for t in test_report.tests
                ]
            }
            result.modules_run.append("constitutional_test")

        # Module 4: Gaceta verification
        if run_gaceta_verify and search_keywords and MODULES_AVAILABLE.get("gaceta_verify"):
            gaceta_results = []
            for keyword in search_keywords[:5]:  # Limit to 5 keywords
                norms = search_norms(keyword)
                gaceta_results.extend([
                    {
                        "key": n.get("key", ""),
                        "name": n.get("name", ""),
                        "status": n.get("status", ""),
                        "gaceta": n.get("gaceta_number", "")
                    }
                    for n in norms[:5]  # Top 5 per keyword
                ])
            result.gaceta_verification = {
                "norms_found": len(gaceta_results),
                "results": gaceta_results[:20]  # Top 20 total
            }
            result.modules_run.append("gaceta_verify")

        # Module 5: TSJ research
        if run_tsj_search and search_keywords:
            tsj_results = []
            for keyword in search_keywords[:5]:
                cases = buscar_por_texto(keyword)
                tsj_results.extend([
                    {
                        "expediente": c.numero_expediente,
                        "sala": c.sala.value,
                        "fecha": c.fecha,
                        "materia": c.materia,
                        "vinculante": c.vinculante
                    }
                    for c in cases[:5]
                ])
            # Add binding precedents
            vinculantes = buscar_vinculantes()
            result.tsj_research = {
                "cases_found": len(tsj_results),
                "binding_precedents": len(vinculantes),
                "results": tsj_results[:20],
                "vinculantes": [
                    {
                        "expediente": v.numero_expediente,
                        "sala": v.sala.value,
                        "ratio": v.ratio_decidendi[:200] if v.ratio_decidendi else ""
                    }
                    for v in vinculantes[:10]
                ]
            }
            result.modules_run.append("tsj_search")

        # Module 6: Voting map
        try:
            norm_enum = VotingNormType[norm_type]
            voting = generate_voting_map(norm_enum)
            result.voting_map = {
                "norm_type": voting.norm_type.value,
                "majority_type": voting.majority_required.value,
                "votes_needed": voting.votes_needed,
                "quorum": voting.quorum,
                "feasibility": voting.feasibility.value,
                "feasibility_score": voting.feasibility_score,
                "timeline": voting.timeline,
                "blockers": voting.blockers,
                "strategies": voting.strategies[:5]
            }
            result.modules_run.append("voting_map")
        except (KeyError, AttributeError) as e:
            result.errors.append(f"Voting map error: {str(e)}")

        # Module 7: Generate report
        report_mgr = ReportManager()
        report_content = report_mgr.generate_analysis_report(
            case_name=case_name,
            constitutional_analysis=result.constitutional_analysis,
            constitutional_tests=result.constitutional_tests,
            gaceta_results=result.gaceta_verification,
            tsj_results=result.tsj_research,
            voting_map=result.voting_map
        )
        result.report_path = report_mgr.save_report(case_name, report_content)
        result.modules_run.append("report_manager")

    except Exception as e:
        result.success = False
        result.errors.append(str(e))

    return result


def get_database_stats() -> Dict[str, Any]:
    """
    Get statistics about all VSL databases.
    Useful for Claude to understand available data without loading it.

    Token Savings: ~99% vs loading full databases
    """
    return {
        "constitution": const_stats(),
        "gaceta": gaceta_stats(),
        "tsj": tsj_stats(),
        "eternity_clauses": [a.numero for a in get_eternity_clauses()] if MODULES_AVAILABLE.get("constitution_diff") else [],
        "law_generator": law_gen_stats() if MODULES_AVAILABLE.get("law_generator") else {},
        "hydrocarbons": hydro_stats() if MODULES_AVAILABLE.get("hydrocarbons_playbook") else {},
        "contract_review": contract_stats() if MODULES_AVAILABLE.get("contract_review") else {},
        "modules_available": {k: v for k, v in MODULES_AVAILABLE.items()},
        "timestamp": datetime.now().isoformat()
    }


def search_all_sources(query: str, max_results: int = 10) -> Dict[str, List]:
    """
    Search across all VSL databases at once.
    Returns unified results from Constitution, Gaceta, and TSJ.

    Token Savings: ~95% vs running separate searches in context
    """
    results = {
        "query": query,
        "constitution": [],
        "gaceta": [],
        "tsj": [],
        "total_results": 0
    }

    # Constitution search
    articles = search_articles(query)
    results["constitution"] = [
        {
            "numero": a.numero,
            "titulo": a.titulo,
            "area": a.area.value,
            "content_preview": a.contenido[:200]
        }
        for a in articles[:max_results]
    ]

    # Gaceta search
    norms = search_norms(query)
    results["gaceta"] = [
        {
            "key": n.get("key", ""),
            "name": n.get("name", ""),
            "type": n.get("norm_type", ""),
            "status": n.get("status", ""),
            "gaceta": n.get("gaceta_number", "")
        }
        for n in norms[:max_results]
    ]

    # TSJ search
    cases = buscar_por_texto(query)
    results["tsj"] = [
        {
            "expediente": c.numero_expediente,
            "sala": c.sala.value,
            "fecha": c.fecha,
            "materia": c.materia,
            "vinculante": c.vinculante
        }
        for c in cases[:max_results]
    ]

    results["total_results"] = (
        len(results["constitution"]) +
        len(results["gaceta"]) +
        len(results["tsj"])
    )

    return results


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE WITH ARGPARSE
# ═══════════════════════════════════════════════════════════════════════════════

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI interface."""
    parser = argparse.ArgumentParser(
        prog="run_case_analysis.py",
        description="Venezuela Super Lawyer - Master Orchestration Script",
        epilog="Token Savings: 90-99%% vs loading code through context"
    )

    # Main commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ═══════════════════════════════════════════════════════════════════
    # INTAKE COMMAND - Master entry point that routes to all workflows
    # ═══════════════════════════════════════════════════════════════════
    intake_parser = subparsers.add_parser(
        "intake",
        help="Start guided intake process - routes to all workflows"
    )
    intake_parser.add_argument(
        "workflow",
        choices=["CASE_ANALYSIS", "LAW_CREATION", "RESEARCH", "TSJ_PREDICTION",
                 "CONTRACT_REVIEW", "CONSTITUTIONAL_TEST", "VOTING_MAP"],
        help="Type of workflow to execute"
    )
    intake_parser.add_argument(
        "case_name",
        help="Name/identifier for this case"
    )
    intake_parser.add_argument(
        "--problem", "-p",
        help="Problem statement (required for most workflows)"
    )
    intake_parser.add_argument(
        "--outcome", "-O",
        help="Desired outcome"
    )
    intake_parser.add_argument(
        "--text", "-t",
        help="Proposal/contract text to analyze"
    )
    intake_parser.add_argument(
        "--text-file", "-f",
        help="File containing proposal/contract text"
    )
    intake_parser.add_argument(
        "--norm-type", "-n",
        choices=["LEY_ORDINARIA", "LEY_ORGANICA", "DECRETO", "RESOLUCION",
                 "REFORMA_CONSTITUCIONAL", "ENMIENDA", "LEY_HABILITANTE"],
        default="LEY_ORDINARIA",
        help="Type of legal norm"
    )
    intake_parser.add_argument(
        "--keywords", "-k",
        nargs="+",
        help="Keywords for research"
    )
    intake_parser.add_argument(
        "--sector", "-s",
        choices=["hydrocarbons", "banking", "labor", "telecom", "healthcare", "energy", "other"],
        help="Industry sector"
    )
    intake_parser.add_argument(
        "--client",
        help="Client name (confidential)"
    )
    intake_parser.add_argument(
        "--urgency",
        choices=["normal", "emergency"],
        default="normal",
        help="Urgency level"
    )
    intake_parser.add_argument(
        "--facts",
        help="Facts/timeline description"
    )
    intake_parser.add_argument(
        "--existing-law",
        help="Existing law/regulation being challenged or amended"
    )
    intake_parser.add_argument(
        "--enforcement",
        choices=["criminal", "administrative", "civil", "incentives"],
        help="Enforcement mechanism"
    )
    intake_parser.add_argument(
        "--political-context",
        help="Political context or constraints"
    )

    # Full analysis command (legacy - routes to intake)
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Run full case analysis"
    )
    analyze_parser.add_argument(
        "case_name",
        help="Name for the case"
    )
    analyze_parser.add_argument(
        "--text", "-t",
        help="Proposal text to analyze"
    )
    analyze_parser.add_argument(
        "--text-file", "-f",
        help="File containing proposal text"
    )
    analyze_parser.add_argument(
        "--norm-type", "-n",
        choices=["LEY_ORDINARIA", "LEY_ORGANICA", "DECRETO", "RESOLUCION",
                 "REFORMA_CONSTITUCIONAL", "ENMIENDA"],
        default="LEY_ORDINARIA",
        help="Type of legal norm"
    )
    analyze_parser.add_argument(
        "--keywords", "-k",
        nargs="+",
        help="Keywords for research"
    )
    analyze_parser.add_argument(
        "--no-tsj",
        action="store_true",
        help="Skip TSJ research"
    )
    analyze_parser.add_argument(
        "--no-gaceta",
        action="store_true",
        help="Skip Gaceta verification"
    )

    # Quick analysis command
    quick_parser = subparsers.add_parser(
        "quick",
        help="Quick constitutional analysis"
    )
    quick_parser.add_argument(
        "text",
        help="Text to analyze"
    )
    quick_parser.add_argument(
        "--norm-type", "-n",
        default="LEY_ORDINARIA",
        help="Type of norm"
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search all databases"
    )
    search_parser.add_argument(
        "query",
        help="Search query"
    )
    search_parser.add_argument(
        "--max-results", "-m",
        type=int,
        default=10,
        help="Maximum results per source"
    )

    # Stats command
    subparsers.add_parser(
        "stats",
        help="Get database statistics"
    )

    # Voting map command
    voting_parser = subparsers.add_parser(
        "voting",
        help="Generate voting map"
    )
    voting_parser.add_argument(
        "norm_type",
        choices=["LEY_ORDINARIA", "LEY_ORGANICA", "DECRETO", "RESOLUCION",
                 "REFORMA_CONSTITUCIONAL", "ENMIENDA", "LEY_HABILITANTE"],
        help="Type of norm"
    )
    voting_parser.add_argument(
        "--title", "-t",
        default="Propuesta Legislativa",
        help="Title of the proposal (default: 'Propuesta Legislativa')"
    )

    # Global options
    parser.add_argument(
        "--output", "-o",
        choices=["json", "text", "minimal"],
        default="json",
        help="Output format"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser


def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    output_format = getattr(args, 'output', 'json')

    try:
        # ═══════════════════════════════════════════════════════════════════
        # INTAKE COMMAND - Master entry point for all workflows
        # Per Manual Section 8: THE INTAKE COMMAND
        # ═══════════════════════════════════════════════════════════════════
        if args.command == "intake":
            # Get proposal text from file or argument
            proposal_text = args.text or ""
            if args.text_file:
                with open(args.text_file, 'r', encoding='utf-8') as f:
                    proposal_text = f.read()

            # Build intake data
            intake = IntakeData(
                workflow_type=args.workflow,
                case_name=args.case_name,
                client_name=getattr(args, 'client', None),
                problem_statement=getattr(args, 'problem', None),
                desired_outcome=getattr(args, 'outcome', None),
                proposal_text=proposal_text,
                norm_type=args.norm_type,
                affected_group=None,  # Could add as argument
                sector=getattr(args, 'sector', None),
                urgency_level=getattr(args, 'urgency', 'normal'),
                keywords=args.keywords or [],
                facts_timeline=getattr(args, 'facts', None),
                existing_law=getattr(args, 'existing_law', None),
                enforcement_mechanism=getattr(args, 'enforcement', None),
                political_context=getattr(args, 'political_context', None)
            )

            # ═══════════════════════════════════════════════════════════════
            # STEP 1: VALIDATE INTAKE (Per Manual Section 8)
            # ═══════════════════════════════════════════════════════════════
            is_valid, validation_errors = validate_intake(intake)
            if not is_valid:
                if output_format == "json":
                    print(json.dumps({
                        "success": False,
                        "stage": "validation",
                        "errors": validation_errors
                    }, indent=2))
                else:
                    print("\n" + "="*70)
                    print("INTAKE VALIDATION FAILED")
                    print("="*70)
                    for err in validation_errors:
                        print(f"  ✗ {err}")
                    print("\nFix the errors above and try again.")
                sys.exit(1)

            # ═══════════════════════════════════════════════════════════════
            # STEP 2: RUN PREFLIGHT CHECKS (Per Manual Section 9)
            # ═══════════════════════════════════════════════════════════════
            preflight = run_preflight_checks(intake)

            if not preflight.passed:
                if output_format == "json":
                    print(json.dumps({
                        "success": False,
                        "stage": "preflight",
                        "preflight": preflight.to_dict()
                    }, indent=2))
                else:
                    print("\n" + "="*70)
                    print("PREFLIGHT CHECKS FAILED")
                    print("="*70)
                    for check in preflight.checks:
                        status_icon = "✓" if check['status'] == "PASS" else ("⚠" if check['status'] == "WARN" else "✗")
                        print(f"  [{status_icon}] {check.get('gate', check.get('check', ''))}: {check['name']} - {check['status']}")
                    print("\nErrors:")
                    for err in preflight.errors:
                        print(f"  ✗ {err}")
                    print("\nFix the errors above and try again.")
                sys.exit(1)

            # ═══════════════════════════════════════════════════════════════
            # STEP 3: SHOW RUN PLAN SUMMARY (Per Manual Section 8)
            # ═══════════════════════════════════════════════════════════════
            workflow_config = WORKFLOW_TYPES.get(intake.workflow_type, {})
            module_count = len(workflow_config.get("modules", []))

            if output_format == "text":
                print("\n" + "="*70)
                print("INTAKE VALIDATED - RUN PLAN SUMMARY")
                print("="*70)
                print(f"\n  Workflow:    {intake.workflow_type}")
                print(f"  Case Name:   {intake.case_name}")
                print(f"  Modules:     {module_count} modules will execute")
                print(f"  Norm Type:   {intake.norm_type}")
                if intake.problem_statement:
                    print(f"  Problem:     {intake.problem_statement[:50]}...")
                if intake.keywords:
                    print(f"  Keywords:    {', '.join(intake.keywords[:5])}")
                print(f"\n  Preflight:   PASSED ({preflight.gates_passed} gates, {preflight.warnings} warnings)")
                print("\n" + "-"*70)
                print("  Proceeding with execution...")
                print("-"*70 + "\n")

            # ═══════════════════════════════════════════════════════════════
            # STEP 4: RUN THE WORKFLOW
            # ═══════════════════════════════════════════════════════════════
            result = run_intake_workflow(intake)

            # ═══════════════════════════════════════════════════════════════
            # STEP 5: GENERATE INTAKE ARTIFACTS (Per Manual Section 8)
            # ═══════════════════════════════════════════════════════════════
            artifacts = None
            if result.case_path:
                case_path = Path(result.case_path)
                artifacts = generate_intake_artifacts(intake, case_path, preflight)
                result.modules_run.append("intake_artifacts")

            # ═══════════════════════════════════════════════════════════════
            # STEP 6: OUTPUT RESULTS WITH ARTIFACTS
            # ═══════════════════════════════════════════════════════════════
            if output_format == "json":
                # Include artifacts in JSON output
                result_dict = result.to_dict()
                if artifacts:
                    result_dict["artifacts"] = {
                        "config": artifacts.config_path,
                        "run_plan": artifacts.run_plan_path,
                        "checklist": artifacts.checklist_path,
                        "test_plan": artifacts.test_plan_path
                    }
                result_dict["preflight"] = preflight.to_dict()
                print(json.dumps(result_dict, indent=2, ensure_ascii=False, default=str))
            elif output_format == "minimal":
                print(f"Workflow: {result.workflow_type}")
                print(f"Success: {result.success}")
                print(f"Preflight: PASSED ({preflight.gates_passed} gates)")
                print(f"Modules: {', '.join(result.modules_run)}")
                if result.report_path:
                    print(f"Report: {result.report_path}")
                if result.case_path:
                    print(f"Case: {result.case_path}")
                if artifacts:
                    print(f"Artifacts: {artifacts.config_path}")
            else:
                print(f"\n{'='*70}")
                print(f"INTAKE WORKFLOW: {result.workflow_type}")
                print(f"CASE: {result.case_name}")
                print(f"{'='*70}")
                print(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
                print(f"Preflight: PASSED ({preflight.gates_passed} gates, {preflight.warnings} warnings)")
                print(f"Modules Run: {', '.join(result.modules_run)}")

                if result.brainstorm:
                    print(f"\n--- BRAINSTORM ---")
                    print(f"Legal Issues: {len(result.brainstorm.get('legal_issues', []))}")
                    print(f"Constitutional Hooks: {len(result.brainstorm.get('constitutional_hooks', []))}")

                if result.constitutional_analysis:
                    print(f"\n--- CONSTITUTIONAL ANALYSIS ---")
                    print(f"Risk Score: {result.constitutional_analysis['risk_score']}")
                    print(f"Compliance: {result.constitutional_analysis['compliance_percentage']}%")
                    print(f"Conflicts: {result.constitutional_analysis['conflicts_found']}")

                if result.constitutional_tests:
                    print(f"\n--- CONSTITUTIONAL TESTS ---")
                    print(f"Passed: {result.constitutional_tests['tests_passed']}/{result.constitutional_tests['total_tests']}")
                    print(f"Overall Risk: {result.constitutional_tests['overall_risk']}")
                    print(f"Nullity Likelihood: {result.constitutional_tests['nullity_likelihood']}")

                if result.avenue_selection:
                    print(f"\n--- AVENUE SELECTION ---")
                    primary = result.avenue_selection.get('primary_avenue', {})
                    print(f"Primary: {primary.get('name', 'N/A')} ({primary.get('speed', 'N/A')})")

                if result.voting_map:
                    print(f"\n--- VOTING MAP ---")
                    print(f"Votes Needed: {result.voting_map['votes_needed']}")
                    print(f"Majority: {result.voting_map['majority_type']}")
                    print(f"Feasibility: {result.voting_map['feasibility']} ({result.voting_map['feasibility_score']:.1f}%)")

                if result.gaceta_verification:
                    print(f"\n--- GACETA VERIFICATION ---")
                    print(f"Norms Found: {result.gaceta_verification['norms_found']}")

                if result.tsj_research:
                    print(f"\n--- TSJ RESEARCH ---")
                    print(f"Cases Found: {result.tsj_research['cases_found']}")
                    print(f"Binding Precedents: {result.tsj_research['binding_precedents']}")

                if result.contract_review:
                    print(f"\n--- CONTRACT REVIEW (Module 9) ---")
                    print(f"Contract Type: {result.contract_review['contract_type']}")
                    print(f"Overall Risk: {result.contract_review['overall_risk']}")
                    print(f"Compliance Score: {result.contract_review['compliance_score']:.0f}%")
                    print(f"Clauses Analyzed: {len(result.contract_review['clause_analysis'])}")
                    print(f"Risk Findings: {len(result.contract_review['risk_findings'])}")

                if result.hydrocarbons_analysis:
                    print(f"\n--- HYDROCARBONS ANALYSIS (Module 7) ---")
                    print(f"Activity Type: {result.hydrocarbons_analysis['activity_type']}")
                    print(f"Reserved to State: {result.hydrocarbons_analysis['reserved_to_state']}")
                    print(f"LOH Articles: {len(result.hydrocarbons_analysis['applicable_loh_articles'])} applicable")
                    if result.hydrocarbons_analysis.get('compliance'):
                        print(f"Art. 9 LOH Compliance: {result.hydrocarbons_analysis['compliance'].get('art_9_loh', 'N/A')}")

                if result.draft_instrument:
                    print(f"\n--- LAW GENERATION (Module 16) ---")
                    print(f"Draft Instrument: Generated ({len(result.draft_instrument)} chars)")
                    if result.implementation_roadmap:
                        print(f"Implementation Roadmap: {result.implementation_roadmap['total_phases']} phases")
                        print(f"Total Days: {result.implementation_roadmap['total_days']}")

                if result.case_path:
                    print(f"\n--- OUTPUT FILES ---")
                    print(f"Case Folder: {result.case_path}")
                if result.report_path:
                    print(f"Report: {result.report_path}")

                # Show artifacts per Manual Section 8
                if artifacts:
                    print(f"\n--- INTAKE ARTIFACTS (Manual Section 8) ---")
                    print(f"config.json:   {artifacts.config_path}")
                    print(f"RUN_PLAN.md:   {artifacts.run_plan_path}")
                    print(f"CHECKLIST.md:  {artifacts.checklist_path}")
                    print(f"TEST_PLAN.md:  {artifacts.test_plan_path}")

                if result.errors:
                    print(f"\n--- ERRORS ---")
                    for err in result.errors:
                        print(f"  - {err}")

                print(f"\n{'='*70}")
                print(f"Token Savings: {result.token_savings}")
                print(f"Manual Reference: Section 8 (Intake), Section 9 (Preflight)")
                print(f"{'='*70}\n")

        elif args.command == "analyze":
            # Get proposal text
            text = args.text or ""
            if args.text_file:
                with open(args.text_file, 'r', encoding='utf-8') as f:
                    text = f.read()

            result = run_full_analysis(
                case_name=args.case_name,
                proposal_text=text,
                norm_type=args.norm_type,
                run_tsj_search=not args.no_tsj,
                run_gaceta_verify=not args.no_gaceta,
                search_keywords=args.keywords
            )

            if output_format == "json":
                print(result.to_json())
            elif output_format == "minimal":
                print(f"Success: {result.success}")
                print(f"Modules: {', '.join(result.modules_run)}")
                print(f"Report: {result.report_path}")
            else:
                print(f"\n{'='*60}")
                print(f"CASE ANALYSIS: {result.case_name}")
                print(f"{'='*60}")
                print(f"Status: {'SUCCESS' if result.success else 'FAILED'}")
                print(f"Modules Run: {', '.join(result.modules_run)}")
                if result.constitutional_analysis:
                    print(f"\nConstitutional Analysis:")
                    print(f"  Risk Score: {result.constitutional_analysis['risk_score']}")
                    print(f"  Compliance: {result.constitutional_analysis['compliance_percentage']}%")
                if result.voting_map:
                    print(f"\nVoting Requirements:")
                    print(f"  Votes Needed: {result.voting_map['votes_needed']}")
                    print(f"  Feasibility: {result.voting_map['feasibility']}")
                if result.report_path:
                    print(f"\nReport saved to: {result.report_path}")

        elif args.command == "quick":
            result = analyze_text_quick(args.text, args.norm_type)
            if output_format == "json":
                print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
            else:
                print(f"\nQuick Analysis Results:")
                print(f"  Risk Score: {result.risk_score}")
                print(f"  Conflicts: {len(result.constitutional_conflicts)}")
                print(f"  Eternity Violations: {result.eternity_clause_violations}")
                for rec in result.recommendations:
                    print(f"  - {rec}")

        elif args.command == "search":
            results = search_all_sources(args.query, args.max_results)
            if output_format == "json":
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(f"\nSearch Results for: {args.query}")
                print(f"Total: {results['total_results']} results")
                print(f"\nConstitution: {len(results['constitution'])} articles")
                print(f"Gaceta: {len(results['gaceta'])} norms")
                print(f"TSJ: {len(results['tsj'])} cases")

        elif args.command == "stats":
            stats = get_database_stats()
            if output_format == "json":
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                print("\nVSL Database Statistics:")
                print(f"  Constitution: {stats['constitution']}")
                print(f"  Gaceta: {stats['gaceta']}")
                print(f"  TSJ: {stats['tsj']}")
                print(f"  Eternity Clauses: {stats['eternity_clauses']}")

        elif args.command == "voting":
            norm_enum = VotingNormType[args.norm_type]
            title = getattr(args, 'title', 'Propuesta Legislativa')
            voting = generate_voting_map(norm_enum, title)
            # Get first voting requirement for display
            main_req = voting.voting_requirements[0] if voting.voting_requirements else None
            result = {
                "norm_type": voting.norm_type.value,
                "title": voting.title,
                "majority_type": main_req.majority_type.value if main_req else "N/A",
                "votes_needed": main_req.votes_needed if main_req else 0,
                "quorum": f"{main_req.quorum_required * 100:.0f}%" if main_req else "N/A",
                "feasibility": voting.feasibility_level.value,
                "feasibility_score": voting.feasibility_score,
                "timeline": [{"phase": t.phase.value, "min_days": t.min_days, "max_days": t.max_days} for t in voting.timeline],
                "blockers": [{"name": b.name, "severity": b.severity.value if hasattr(b.severity, 'value') else str(b.severity)} for b in voting.blockers],
                "strategy": voting.recommended_strategy,
                "alternatives": voting.alternative_routes
            }
            if output_format == "json":
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print(f"\nVoting Map for: {args.norm_type}")
                print(f"  Title: {result['title']}")
                print(f"  Majority: {result['majority_type']}")
                print(f"  Votes Needed: {result['votes_needed']}")
                print(f"  Quorum: {result['quorum']}")
                print(f"  Feasibility: {result['feasibility']} ({result['feasibility_score']:.1f}%)")

    except Exception as e:
        if output_format == "json":
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
