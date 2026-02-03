#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Constitutional Test Engine
Runs automated constitutionality tests on legal instruments.
"""

import json
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional


class RiskLevel(Enum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class TestResult:
    test_name: str
    passed: bool
    risk_level: RiskLevel
    findings: str
    crbv_articles: List[str]
    recommendations: List[str]


@dataclass
class ConstitutionalityReport:
    norm_under_review: str
    review_date: str
    overall_risk: RiskLevel
    nullity_likelihood: str
    tsj_prediction: str
    tests: List[TestResult]
    corrective_actions: List[str]
    summary: str


def run_supremacy_test(norm_description: str, constitutional_conflicts: List[str]) -> TestResult:
    """Test 1: Does the norm contradict any CRBV provision?"""

    if not constitutional_conflicts:
        return TestResult(
            test_name="Supremacy Test (Supremacía Constitucional)",
            passed=True,
            risk_level=RiskLevel.NONE,
            findings="No constitutional conflicts identified.",
            crbv_articles=[],
            recommendations=[]
        )

    risk = RiskLevel.CRITICAL if len(constitutional_conflicts) > 2 else RiskLevel.HIGH

    return TestResult(
        test_name="Supremacy Test (Supremacía Constitucional)",
        passed=False,
        risk_level=risk,
        findings=f"Potential conflicts with {len(constitutional_conflicts)} constitutional provisions.",
        crbv_articles=constitutional_conflicts,
        recommendations=[
            "Review each conflicting provision for material inconsistency",
            "Consider constitutional interpretation that harmonizes norms",
            "Assess need for legislative reform or constitutional action"
        ]
    )


def run_rights_impact_test(affected_rights: List[str]) -> TestResult:
    """Test 2: Does the norm affect fundamental rights?"""

    if not affected_rights:
        return TestResult(
            test_name="Rights Impact Test (Impacto en Derechos Fundamentales)",
            passed=True,
            risk_level=RiskLevel.NONE,
            findings="No fundamental rights affected.",
            crbv_articles=[],
            recommendations=[]
        )

    risk = RiskLevel.HIGH if len(affected_rights) > 1 else RiskLevel.MEDIUM

    return TestResult(
        test_name="Rights Impact Test (Impacto en Derechos Fundamentales)",
        passed=False,
        risk_level=risk,
        findings=f"Affects {len(affected_rights)} fundamental rights. Pro persona analysis required.",
        crbv_articles=affected_rights,
        recommendations=[
            "Apply pro persona principle - interpret in favor of rights",
            "Verify proportionality of any rights restriction",
            "Check for non-regression in social rights (Art. 19 CRBV)"
        ]
    )


def run_competence_test(issuing_authority: str, legal_basis: str, has_reserva_legal: bool) -> TestResult:
    """Test 3: Was the issuing authority competent?"""

    if has_reserva_legal and issuing_authority and legal_basis:
        return TestResult(
            test_name="Competence Test (Competencia del Órgano Emisor)",
            passed=True,
            risk_level=RiskLevel.NONE,
            findings=f"Authority: {issuing_authority}. Legal basis: {legal_basis}. Reserva legal satisfied.",
            crbv_articles=["Art. 137", "Art. 156", "Art. 187"],
            recommendations=[]
        )

    findings = []
    if not issuing_authority:
        findings.append("Issuing authority not clearly identified")
    if not legal_basis:
        findings.append("Legal basis not established")
    if not has_reserva_legal:
        findings.append("Reserva legal potentially violated - matter requires legislative action")

    return TestResult(
        test_name="Competence Test (Competencia del Órgano Emisor)",
        passed=False,
        risk_level=RiskLevel.HIGH,
        findings="; ".join(findings),
        crbv_articles=["Art. 137", "Art. 156", "Art. 187"],
        recommendations=[
            "Verify constitutional/legal attribution of competence",
            "Check if matter is subject to reserva legal",
            "Review delegation chain if applicable"
        ]
    )


def run_due_process_test(published_in_gaceta: bool, proper_procedure: bool, notification_given: bool) -> TestResult:
    """Test 4: Were procedural requirements met?"""

    issues = []
    if not published_in_gaceta:
        issues.append("Not published in Gaceta Oficial")
    if not proper_procedure:
        issues.append("Procedural irregularities detected")
    if not notification_given:
        issues.append("Required notifications not completed")

    if not issues:
        return TestResult(
            test_name="Due Process Test (Debido Proceso)",
            passed=True,
            risk_level=RiskLevel.NONE,
            findings="All procedural requirements satisfied.",
            crbv_articles=["Art. 49", "Art. 215"],
            recommendations=[]
        )

    risk = RiskLevel.HIGH if not published_in_gaceta else RiskLevel.MEDIUM

    return TestResult(
        test_name="Due Process Test (Debido Proceso)",
        passed=False,
        risk_level=risk,
        findings="; ".join(issues),
        crbv_articles=["Art. 49", "Art. 215"],
        recommendations=[
            "Verify publication in Gaceta Oficial for effectiveness",
            "Review procedural steps for compliance",
            "Ensure all affected parties were properly notified"
        ]
    )


def run_public_interest_test(serves_public_interest: bool, is_proportional: bool, reasoning: str) -> TestResult:
    """Test 5: Does the norm serve legitimate public interest?"""

    if serves_public_interest and is_proportional:
        return TestResult(
            test_name="Public Interest Test (Interés Público y Proporcionalidad)",
            passed=True,
            risk_level=RiskLevel.NONE,
            findings=f"Public interest justified. {reasoning}",
            crbv_articles=["Art. 2", "Art. 3", "Art. 141"],
            recommendations=[]
        )

    issues = []
    if not serves_public_interest:
        issues.append("Public interest justification weak or absent")
    if not is_proportional:
        issues.append("Measure appears disproportionate to stated objective")

    return TestResult(
        test_name="Public Interest Test (Interés Público y Proporcionalidad)",
        passed=False,
        risk_level=RiskLevel.MEDIUM,
        findings="; ".join(issues) + f". Analysis: {reasoning}",
        crbv_articles=["Art. 2", "Art. 3", "Art. 141"],
        recommendations=[
            "Strengthen public interest justification",
            "Apply proportionality test (suitability, necessity, proportionality stricto sensu)",
            "Document rational basis for the measure"
        ]
    )


def calculate_overall_risk(tests: List[TestResult]) -> RiskLevel:
    """Calculate overall risk based on individual test results."""

    risk_weights = {
        RiskLevel.NONE: 0,
        RiskLevel.LOW: 1,
        RiskLevel.MEDIUM: 2,
        RiskLevel.HIGH: 3,
        RiskLevel.CRITICAL: 4
    }

    max_risk = max(risk_weights[t.risk_level] for t in tests)
    failed_count = sum(1 for t in tests if not t.passed)

    if max_risk >= 4 or failed_count >= 3:
        return RiskLevel.CRITICAL
    elif max_risk >= 3 or failed_count >= 2:
        return RiskLevel.HIGH
    elif max_risk >= 2 or failed_count >= 1:
        return RiskLevel.MEDIUM
    elif max_risk >= 1:
        return RiskLevel.LOW
    return RiskLevel.NONE


def calculate_nullity_likelihood(overall_risk: RiskLevel, tests: List[TestResult]) -> str:
    """Estimate likelihood of nullity based on test results."""

    failed_critical = sum(1 for t in tests if not t.passed and t.risk_level == RiskLevel.CRITICAL)
    failed_high = sum(1 for t in tests if not t.passed and t.risk_level == RiskLevel.HIGH)

    if failed_critical >= 1:
        return "85-95% - Very High"
    elif failed_high >= 2:
        return "70-85% - High"
    elif failed_high >= 1:
        return "50-70% - Moderate"
    elif overall_risk == RiskLevel.MEDIUM:
        return "25-50% - Low-Moderate"
    elif overall_risk == RiskLevel.LOW:
        return "10-25% - Low"
    return "0-10% - Minimal"


def generate_tsj_prediction(overall_risk: RiskLevel, tests: List[TestResult]) -> str:
    """Generate TSJ outcome prediction."""

    failed_tests = [t for t in tests if not t.passed]

    if overall_risk == RiskLevel.CRITICAL:
        return "Sala Constitucional likely to declare unconstitutionality. Immediate legal risk."
    elif overall_risk == RiskLevel.HIGH:
        return "Significant risk of adverse TSJ ruling. Constitutional challenge likely to succeed."
    elif overall_risk == RiskLevel.MEDIUM:
        return "TSJ outcome uncertain. Depends on specific facts and argumentation quality."
    elif overall_risk == RiskLevel.LOW:
        return "TSJ likely to uphold norm. Low risk of successful constitutional challenge."
    return "TSJ expected to uphold constitutionality. Minimal litigation risk."


def run_full_constitutional_test(
    norm_description: str,
    constitutional_conflicts: List[str] = None,
    affected_rights: List[str] = None,
    issuing_authority: str = "",
    legal_basis: str = "",
    has_reserva_legal: bool = True,
    published_in_gaceta: bool = True,
    proper_procedure: bool = True,
    notification_given: bool = True,
    serves_public_interest: bool = True,
    is_proportional: bool = True,
    public_interest_reasoning: str = ""
) -> ConstitutionalityReport:
    """Run complete constitutional test battery."""

    constitutional_conflicts = constitutional_conflicts or []
    affected_rights = affected_rights or []

    tests = [
        run_supremacy_test(norm_description, constitutional_conflicts),
        run_rights_impact_test(affected_rights),
        run_competence_test(issuing_authority, legal_basis, has_reserva_legal),
        run_due_process_test(published_in_gaceta, proper_procedure, notification_given),
        run_public_interest_test(serves_public_interest, is_proportional, public_interest_reasoning)
    ]

    overall_risk = calculate_overall_risk(tests)
    nullity_likelihood = calculate_nullity_likelihood(overall_risk, tests)
    tsj_prediction = generate_tsj_prediction(overall_risk, tests)

    # Generate corrective actions
    corrective_actions = []
    for test in tests:
        if not test.passed:
            corrective_actions.extend(test.recommendations)

    # Remove duplicates while preserving order
    seen = set()
    unique_actions = []
    for action in corrective_actions:
        if action not in seen:
            seen.add(action)
            unique_actions.append(action)

    # Generate summary
    passed_count = sum(1 for t in tests if t.passed)
    summary = f"""
Constitutional Review Summary for: {norm_description}

Tests Passed: {passed_count}/5
Overall Risk Level: {overall_risk.value}
Nullity Likelihood: {nullity_likelihood}

TSJ Prediction: {tsj_prediction}

{'⚠️ IMMEDIATE ATTENTION REQUIRED' if overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL] else '✅ Risk within acceptable parameters' if overall_risk in [RiskLevel.NONE, RiskLevel.LOW] else '⚡ Monitor and address identified issues'}
"""

    return ConstitutionalityReport(
        norm_under_review=norm_description,
        review_date=datetime.now().isoformat(),
        overall_risk=overall_risk,
        nullity_likelihood=nullity_likelihood,
        tsj_prediction=tsj_prediction,
        tests=tests,
        corrective_actions=unique_actions,
        summary=summary.strip()
    )


def report_to_markdown(report: ConstitutionalityReport) -> str:
    """Convert report to markdown format."""

    md = f"""# Constitutional Test Report

**Norm Under Review:** {report.norm_under_review}
**Review Date:** {report.review_date}

---

## Executive Summary

{report.summary}

---

## Overall Assessment

| Metric | Value |
|--------|-------|
| **Overall Risk Level** | {report.overall_risk.value} |
| **Nullity Likelihood** | {report.nullity_likelihood} |
| **TSJ Prediction** | {report.tsj_prediction} |

---

## Individual Test Results

"""

    for i, test in enumerate(report.tests, 1):
        status = "✅ PASSED" if test.passed else "❌ FAILED"
        md += f"""### Test {i}: {test.test_name}

**Status:** {status}
**Risk Level:** {test.risk_level.value}

**Findings:**
{test.findings}

**CRBV Articles:** {', '.join(test.crbv_articles) if test.crbv_articles else 'N/A'}

"""
        if test.recommendations:
            md += "**Recommendations:**\n"
            for rec in test.recommendations:
                md += f"- {rec}\n"
        md += "\n---\n\n"

    if report.corrective_actions:
        md += "## Corrective Actions Required\n\n"
        for i, action in enumerate(report.corrective_actions, 1):
            md += f"{i}. {action}\n"

    return md


def main():
    """Main function for CLI usage."""

    if len(sys.argv) < 2:
        print("Venezuela Super Lawyer - Constitutional Test Engine")
        print("\nUsage:")
        print("  python3 constitutional_test.py <norm_description>")
        print("  python3 constitutional_test.py --interactive")
        print("  python3 constitutional_test.py --json <input_file.json>")
        print("\nExample:")
        print("  python3 constitutional_test.py 'Decreto 4.567 sobre control de precios'")
        sys.exit(0)

    if sys.argv[1] == "--interactive":
        print("Interactive mode not yet implemented. Use --json with input file.")
        sys.exit(1)

    if sys.argv[1] == "--json" and len(sys.argv) > 2:
        with open(sys.argv[2], 'r') as f:
            params = json.load(f)
        report = run_full_constitutional_test(**params)
    else:
        # Basic test with just norm description
        norm_description = sys.argv[1]
        report = run_full_constitutional_test(norm_description=norm_description)

    # Output markdown report
    print(report_to_markdown(report))


if __name__ == "__main__":
    main()
