#!/usr/bin/env python3
"""
Unit tests for voting_map.py - Voting Map Engine
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from voting_map import (
    NormType,
    MajorityType,
    VotingBody,
    LegislativePhase,
    FeasibilityLevel,
    VotingRequirement,
    VotingMap,
    calculate_votes_needed,
    calculate_feasibility,
    generate_voting_map,
    analyze_proposal,
    get_majority_comparison,
    get_legislative_timeline,
    AN_TOTAL_MEMBERS,
    VOTING_REQUIREMENTS
)


class TestVotingMapEngine(unittest.TestCase):
    """Test cases for Voting Map Engine."""

    def test_an_total_members_defined(self):
        """AN_TOTAL_MEMBERS should be defined."""
        self.assertGreater(AN_TOTAL_MEMBERS, 0)
        self.assertEqual(AN_TOTAL_MEMBERS, 277)

    def test_voting_requirements_defined(self):
        """VOTING_REQUIREMENTS should be defined for all norm types."""
        expected_types = [
            NormType.LEY_ORDINARIA,
            NormType.LEY_ORGANICA,
            NormType.LEY_HABILITANTE,
            NormType.ENMIENDA,
            NormType.REFORMA,
        ]
        for norm_type in expected_types:
            self.assertIn(norm_type, VOTING_REQUIREMENTS)


class TestCalculateVotesNeeded(unittest.TestCase):
    """Test vote calculation functionality."""

    def test_simple_majority(self):
        """Simple majority calculation."""
        votes, quorum = calculate_votes_needed(277, MajorityType.SIMPLE)
        self.assertGreater(votes, 0)
        self.assertLess(votes, 277)
        self.assertGreater(quorum, 0)

    def test_absolute_majority(self):
        """Absolute majority should be >50% of total."""
        votes, quorum = calculate_votes_needed(277, MajorityType.ABSOLUTA)
        self.assertGreater(votes, 138)  # >50% of 277
        self.assertLessEqual(votes, 145)  # Allow some flexibility in calculation

    def test_qualified_2_3(self):
        """2/3 majority calculation."""
        votes, quorum = calculate_votes_needed(277, MajorityType.CALIFICADA_2_3)
        expected = 185  # ceil(277 * 2/3)
        self.assertEqual(votes, expected)

    def test_qualified_3_5(self):
        """3/5 majority calculation."""
        votes, quorum = calculate_votes_needed(277, MajorityType.CALIFICADA_3_5)
        expected = 167  # ceil(277 * 3/5)
        self.assertEqual(votes, expected)

    def test_unanimity(self):
        """Unanimity should require all votes."""
        votes, quorum = calculate_votes_needed(277, MajorityType.UNANIMIDAD)
        self.assertEqual(votes, 277)


class TestCalculateFeasibility(unittest.TestCase):
    """Test feasibility calculation."""

    def test_high_feasibility(self):
        """High favorable votes should give high feasibility."""
        score, level = calculate_feasibility(100, 150, [])
        self.assertGreater(score, 0.8)
        self.assertEqual(level, FeasibilityLevel.MUY_ALTA)

    def test_low_feasibility(self):
        """Low favorable votes should give low feasibility."""
        score, level = calculate_feasibility(200, 50, [])
        self.assertLess(score, 0.5)

    def test_blockers_reduce_feasibility(self):
        """Blockers should reduce feasibility score."""
        from voting_map import PoliticalBlocker

        blockers = [
            PoliticalBlocker(
                name="Test Blocker",
                description="Test",
                severity="Alta",
                mitigation="Test",
                probability=0.8
            )
        ]

        score_without, _ = calculate_feasibility(100, 150, [])
        score_with, _ = calculate_feasibility(100, 150, blockers)

        self.assertLess(score_with, score_without)


class TestGenerateVotingMap(unittest.TestCase):
    """Test voting map generation."""

    def test_generate_for_ley_ordinaria(self):
        """Generate map for ordinary law."""
        vmap = generate_voting_map(
            NormType.LEY_ORDINARIA,
            "Ley de Prueba",
            "Descripción de prueba"
        )
        self.assertIsInstance(vmap, VotingMap)
        self.assertEqual(vmap.norm_type, NormType.LEY_ORDINARIA)

    def test_generate_for_ley_organica(self):
        """Generate map for organic law."""
        vmap = generate_voting_map(
            NormType.LEY_ORGANICA,
            "Ley Orgánica de Prueba"
        )
        self.assertEqual(vmap.norm_type, NormType.LEY_ORGANICA)
        # Organic law needs 2/3 majority
        self.assertTrue(any(
            vr.majority_type == MajorityType.CALIFICADA_2_3
            for vr in vmap.voting_requirements
        ))

    def test_generate_for_enmienda(self):
        """Generate map for constitutional amendment."""
        vmap = generate_voting_map(
            NormType.ENMIENDA,
            "Enmienda de Prueba"
        )
        self.assertEqual(vmap.norm_type, NormType.ENMIENDA)
        # Amendment needs referendum
        self.assertTrue(any(
            vr.voting_body == VotingBody.PUEBLO
            for vr in vmap.voting_requirements
        ))

    def test_voting_map_has_timeline(self):
        """Voting map should have timeline."""
        vmap = generate_voting_map(NormType.LEY_ORDINARIA, "Test")
        self.assertGreater(len(vmap.timeline), 0)

    def test_voting_map_has_blockers(self):
        """Voting map should have blockers."""
        vmap = generate_voting_map(NormType.LEY_ORDINARIA, "Test")
        self.assertGreater(len(vmap.blockers), 0)

    def test_voting_map_has_feasibility(self):
        """Voting map should have feasibility score."""
        vmap = generate_voting_map(NormType.LEY_ORDINARIA, "Test")
        self.assertGreaterEqual(vmap.feasibility_score, 0)
        self.assertLessEqual(vmap.feasibility_score, 1)


class TestAnalyzeProposal(unittest.TestCase):
    """Test proposal analysis API."""

    def test_analyze_returns_dict(self):
        """analyze_proposal should return dictionary."""
        result = analyze_proposal("Test Proposal", "ordinaria")
        self.assertIsInstance(result, dict)

    def test_analyze_has_required_keys(self):
        """Result should have required keys."""
        result = analyze_proposal("Test", "ordinaria")
        required_keys = [
            'title', 'norm_type', 'voting_requirements',
            'timeline', 'blockers', 'feasibility'
        ]
        for key in required_keys:
            self.assertIn(key, result)


class TestGetMajorityComparison(unittest.TestCase):
    """Test majority comparison functionality."""

    def test_comparison_has_majorities(self):
        """Comparison should include all majority types."""
        comparison = get_majority_comparison()
        self.assertIn('majorities', comparison)
        self.assertGreater(len(comparison['majorities']), 0)

    def test_comparison_has_norm_requirements(self):
        """Comparison should include norm requirements."""
        comparison = get_majority_comparison()
        self.assertIn('norm_requirements', comparison)


class TestEnums(unittest.TestCase):
    """Test enum definitions."""

    def test_norm_type_values(self):
        """NormType should have expected values."""
        self.assertEqual(NormType.LEY_ORDINARIA.value, "Ley Ordinaria")
        self.assertEqual(NormType.LEY_ORGANICA.value, "Ley Orgánica")
        self.assertEqual(NormType.ENMIENDA.value, "Enmienda Constitucional")

    def test_majority_type_values(self):
        """MajorityType should have expected values."""
        self.assertEqual(MajorityType.SIMPLE.value, "Mayoría Simple")
        self.assertEqual(MajorityType.CALIFICADA_2_3.value, "Mayoría Calificada (2/3)")

    def test_feasibility_level_values(self):
        """FeasibilityLevel should have expected values."""
        self.assertEqual(FeasibilityLevel.MUY_ALTA.value, "Muy Alta")
        self.assertEqual(FeasibilityLevel.BAJA.value, "Baja")


if __name__ == '__main__':
    unittest.main()
