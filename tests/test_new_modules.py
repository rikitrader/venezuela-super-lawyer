#!/usr/bin/env python3
"""
Tests for new Venezuela Super Lawyer modules:
- Module 7: Hydrocarbons Playbook
- Module 9: Contract Review
- Module 16: Law Generator

Version: 1.0.0
"""

import sys
import unittest
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


class TestLawGenerator(unittest.TestCase):
    """Tests for Module 16: Law Generator."""

    def setUp(self):
        """Set up test fixtures."""
        from law_generator import (
            InstrumentType, EnforcementType, ArticleType,
            generate_legal_instrument, generate_standard_articles,
            generate_sanction_articles, generate_implementation_roadmap,
            generate_hydrocarbons_instrument
        )
        self.InstrumentType = InstrumentType
        self.EnforcementType = EnforcementType
        self.ArticleType = ArticleType
        self.generate_legal_instrument = generate_legal_instrument
        self.generate_standard_articles = generate_standard_articles
        self.generate_sanction_articles = generate_sanction_articles
        self.generate_implementation_roadmap = generate_implementation_roadmap
        self.generate_hydrocarbons_instrument = generate_hydrocarbons_instrument

    def test_generate_standard_articles(self):
        """Test standard article generation."""
        articles = self.generate_standard_articles(
            objeto="regular la actividad X",
            ambito="todo el territorio nacional",
            definiciones={"Término": "Definición del término"},
            principios=["Legalidad", "Transparencia"],
            sector="general"
        )

        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)
        self.assertEqual(articles[0].numero, 1)
        self.assertEqual(articles[0].tipo, self.ArticleType.OBJETO)

    def test_generate_sanction_articles_administrative(self):
        """Test administrative sanction article generation."""
        articles = self.generate_sanction_articles(
            enforcement=self.EnforcementType.ADMINISTRATIVE,
            base_article_num=20
        )

        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)
        self.assertEqual(articles[0].tipo, self.ArticleType.SANCIONES)

    def test_generate_sanction_articles_criminal(self):
        """Test criminal sanction article generation."""
        articles = self.generate_sanction_articles(
            enforcement=self.EnforcementType.CRIMINAL,
            base_article_num=20
        )

        self.assertIsInstance(articles, list)
        self.assertGreater(len(articles), 0)

    def test_generate_implementation_roadmap(self):
        """Test implementation roadmap generation."""
        roadmap = self.generate_implementation_roadmap(
            instrument_title="Ley de Prueba",
            instrument_type=self.InstrumentType.LEY_ORDINARIA,
            sector="general",
            urgency="normal"
        )

        self.assertEqual(roadmap.instrument_title, "Ley de Prueba")
        self.assertGreater(roadmap.total_phases, 0)
        self.assertGreater(roadmap.total_days, 0)
        self.assertIsInstance(roadmap.phases, list)

    def test_generate_legal_instrument(self):
        """Test complete legal instrument generation."""
        instrument, roadmap = self.generate_legal_instrument(
            titulo="Ley de Prueba",
            objeto="regular las pruebas automatizadas",
            ambito="todo el territorio nacional",
            tipo=self.InstrumentType.LEY_ORDINARIA,
            sector="general",
            enforcement=self.EnforcementType.ADMINISTRATIVE
        )

        self.assertEqual(instrument.titulo, "Ley de Prueba")
        self.assertEqual(instrument.tipo, self.InstrumentType.LEY_ORDINARIA)
        self.assertGreater(len(instrument.articulos), 0)
        self.assertGreater(len(instrument.considerandos), 0)

        # Test text generation
        text = instrument.to_full_text()
        self.assertIn("LEY ORDINARIA", text)
        self.assertIn("Ley de Prueba", text)

        # Test dict conversion
        data = instrument.to_dict()
        self.assertEqual(data["titulo"], "Ley de Prueba")

    def test_generate_hydrocarbons_instrument(self):
        """Test hydrocarbons-specific instrument generation."""
        instrument, roadmap = self.generate_hydrocarbons_instrument(
            titulo="Reforma LOH",
            objeto="reformar el régimen de hidrocarburos"
        )

        self.assertEqual(instrument.titulo, "Reforma LOH")
        # Should have hydrocarbons-specific definitions
        definitions_article = next(
            (a for a in instrument.articulos if a.tipo == self.ArticleType.DEFINICIONES),
            None
        )
        self.assertIsNotNone(definitions_article)

    def test_roadmap_markdown_generation(self):
        """Test roadmap markdown generation."""
        roadmap = self.generate_implementation_roadmap(
            instrument_title="Ley Test",
            instrument_type=self.InstrumentType.LEY_ORDINARIA
        )

        markdown = roadmap.to_markdown()
        self.assertIn("# Hoja de Ruta", markdown)
        self.assertIn("Fase 1:", markdown)


class TestHydrocarbonsPlaybook(unittest.TestCase):
    """Tests for Module 7: Hydrocarbons Playbook."""

    def setUp(self):
        """Set up test fixtures."""
        from hydrocarbons_playbook import (
            ActivityType, ContractType as HCContractType, RegimeType,
            analyze_activity, analyze_empresa_mixta, calculate_fiscal_obligations,
            get_environmental_requirements, run_full_hydrocarbons_analysis,
            search_loh_articles, get_statistics
        )
        self.ActivityType = ActivityType
        self.HCContractType = HCContractType
        self.RegimeType = RegimeType
        self.analyze_activity = analyze_activity
        self.analyze_empresa_mixta = analyze_empresa_mixta
        self.calculate_fiscal_obligations = calculate_fiscal_obligations
        self.get_environmental_requirements = get_environmental_requirements
        self.run_full_hydrocarbons_analysis = run_full_hydrocarbons_analysis
        self.search_loh_articles = search_loh_articles
        self.get_statistics = get_statistics

    def test_analyze_activity_exploration(self):
        """Test exploration activity analysis."""
        analysis = self.analyze_activity(self.ActivityType.EXPLORACION)

        self.assertTrue(analysis["reserved_to_state"])
        self.assertTrue(analysis["empresa_mixta_required"])
        self.assertIn(3, analysis["applicable_loh_articles"])

    def test_analyze_activity_secondary(self):
        """Test secondary activity analysis."""
        analysis = self.analyze_activity(self.ActivityType.REFINACION)

        self.assertFalse(analysis["reserved_to_state"])
        self.assertFalse(analysis["empresa_mixta_required"])

    def test_analyze_empresa_mixta_compliant(self):
        """Test compliant empresa mixta analysis."""
        analysis = self.analyze_empresa_mixta(
            nombre="Petrozuata",
            participacion_pdvsa=60.0,
            socio_privado="Chevron",
            produccion_bpd=100000
        )

        self.assertTrue(analysis["compliance"]["art_9_loh"])
        self.assertIn("PDVSA mantiene control", analysis["compliance"]["message"])

    def test_analyze_empresa_mixta_non_compliant(self):
        """Test non-compliant empresa mixta analysis."""
        analysis = self.analyze_empresa_mixta(
            nombre="Empresa Test",
            participacion_pdvsa=40.0,
            socio_privado="Privado",
            produccion_bpd=50000
        )

        self.assertFalse(analysis["compliance"]["art_9_loh"])
        self.assertIn("risks", analysis)

    def test_calculate_fiscal_obligations(self):
        """Test fiscal obligation calculation."""
        result = self.calculate_fiscal_obligations(
            produccion_bpd=100000,
            precio_barril_usd=70.0,
            area_km2=100,
            dias=30
        )

        self.assertEqual(result["produccion_total_barriles"], 3000000)
        self.assertIn("obligaciones", result)
        self.assertIn("regalia_30", result["obligaciones"])
        self.assertGreater(result["total_carga_fiscal_estimada_usd"], 0)

    def test_get_environmental_requirements(self):
        """Test environmental requirements retrieval."""
        requirements = self.get_environmental_requirements(self.ActivityType.EXPLOTACION)

        self.assertEqual(requirements["activity"], "Explotación")
        self.assertIn("permits", requirements)
        self.assertIn("penalties", requirements)

    def test_run_full_analysis(self):
        """Test full hydrocarbons analysis."""
        analysis = self.run_full_hydrocarbons_analysis(
            case_name="Test_Case",
            activity="EXPLOTACION",
            contract="EMPRESA_MIXTA",
            produccion_bpd=50000,
            precio_barril=75.0,
            participacion_pdvsa=60.0
        )

        self.assertEqual(analysis.case_name, "Test_Case")
        self.assertEqual(analysis.activity_type, self.ActivityType.EXPLOTACION)
        self.assertGreater(len(analysis.applicable_loh_articles), 0)
        self.assertIsNotNone(analysis.empresa_mixta)
        self.assertIsNotNone(analysis.fiscal_calc)

    def test_search_loh_articles(self):
        """Test LOH article search."""
        results = self.search_loh_articles("regalía")

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.get_statistics()

        self.assertIn("loh_articles_indexed", stats)
        self.assertIn("fiscal_obligations_tracked", stats)


class TestContractReview(unittest.TestCase):
    """Tests for Module 9: Contract Review."""

    def setUp(self):
        """Set up test fixtures."""
        from contract_review import (
            ContractType, ClauseType, RiskLevel, ComplianceStatus,
            detect_contract_type, extract_parties, analyze_clauses,
            check_compliance, find_risk_patterns, review_contract,
            get_statistics
        )
        self.ContractType = ContractType
        self.ClauseType = ClauseType
        self.RiskLevel = RiskLevel
        self.ComplianceStatus = ComplianceStatus
        self.detect_contract_type = detect_contract_type
        self.extract_parties = extract_parties
        self.analyze_clauses = analyze_clauses
        self.check_compliance = check_compliance
        self.find_risk_patterns = find_risk_patterns
        self.review_contract = review_contract
        self.get_statistics = get_statistics

    def test_detect_contract_type_compraventa(self):
        """Test compraventa contract detection."""
        text = "Contrato de compraventa de inmueble. El vendedor se obliga a..."
        result = self.detect_contract_type(text)
        self.assertEqual(result, self.ContractType.COMPRAVENTA)

    def test_detect_contract_type_arrendamiento(self):
        """Test arrendamiento contract detection."""
        text = "Contrato de arrendamiento. El arrendador cede en uso al inquilino..."
        result = self.detect_contract_type(text)
        self.assertEqual(result, self.ContractType.ARRENDAMIENTO)

    def test_detect_contract_type_trabajo(self):
        """Test trabajo contract detection."""
        text = "Contrato de trabajo. El empleador contrata al trabajador con un salario de..."
        result = self.detect_contract_type(text)
        self.assertEqual(result, self.ContractType.TRABAJO)

    def test_analyze_clauses(self):
        """Test clause analysis."""
        text = """
        CLÁUSULA PRIMERA: OBJETO DEL CONTRATO
        El objeto del presente contrato es la prestación de servicios.

        CLÁUSULA SEGUNDA: PLAZO
        El plazo del contrato es de un año.

        CLÁUSULA TERCERA: JURISDICCIÓN
        Los tribunales de Venezuela serán competentes.
        """
        clauses = self.analyze_clauses(text, self.ContractType.SERVICIO)

        self.assertIsInstance(clauses, list)
        self.assertGreater(len(clauses), 0)

        # Check objeto clause was found
        objeto_clause = next((c for c in clauses if c.tipo == self.ClauseType.OBJETO), None)
        self.assertIsNotNone(objeto_clause)
        self.assertTrue(objeto_clause.presente)

    def test_check_compliance(self):
        """Test compliance checking."""
        text = "El pago se realizará en dólares americanos (USD)."
        checks = self.check_compliance(text, self.ContractType.SERVICIO, ["Parte A", "Parte B"])

        self.assertIsInstance(checks, list)
        self.assertGreater(len(checks), 0)

        # Check for currency check
        currency_check = next((c for c in checks if c.check_name == "Moneda de Pago"), None)
        self.assertIsNotNone(currency_check)
        self.assertEqual(currency_check.status, self.ComplianceStatus.REQUIRES_REVIEW)

    def test_find_risk_patterns(self):
        """Test risk pattern finding."""
        text = "La parte renuncia a todo derecho de reclamación sin límite de responsabilidad."
        findings = self.find_risk_patterns(text)

        self.assertIsInstance(findings, list)
        self.assertGreater(len(findings), 0)

    def test_review_contract_complete(self):
        """Test complete contract review."""
        text = """
        CONTRATO DE COMPRAVENTA

        Entre EMPRESA ABC, C.A., en adelante EL VENDEDOR, y EMPRESA XYZ, C.A.,
        en adelante EL COMPRADOR.

        CLÁUSULA PRIMERA: OBJETO
        El objeto del presente contrato es la venta del inmueble ubicado en Caracas.

        CLÁUSULA SEGUNDA: PRECIO
        El precio es de USD 500,000 pagaderos en dólares americanos.

        CLÁUSULA TERCERA: PLAZO
        La entrega se realizará en 30 días.

        CLÁUSULA CUARTA: JURISDICCIÓN
        Los tribunales de Venezuela serán los competentes.

        CLÁUSULA QUINTA: LEY APLICABLE
        Se aplicará la legislación venezolana.
        """

        result = self.review_contract(text, "Test Contract Review")

        self.assertEqual(result.case_name, "Test Contract Review")
        self.assertEqual(result.contract_type, self.ContractType.COMPRAVENTA)
        self.assertGreater(len(result.clause_analysis), 0)
        self.assertGreater(len(result.compliance_checks), 0)
        self.assertIsInstance(result.overall_risk, self.RiskLevel)
        self.assertGreater(result.compliance_score, 0)

        # Test markdown generation
        markdown = result.to_markdown()
        self.assertIn("# Contract Review", markdown)

    def test_get_statistics(self):
        """Test statistics retrieval."""
        stats = self.get_statistics()

        self.assertIn("contract_types_supported", stats)
        self.assertIn("clause_types_analyzed", stats)
        self.assertIn("compliance_checks_available", stats)


class TestModuleIntegration(unittest.TestCase):
    """Integration tests for all modules."""

    def test_law_generator_with_hydrocarbons(self):
        """Test law generator with hydrocarbons playbook."""
        from law_generator import generate_hydrocarbons_instrument
        from hydrocarbons_playbook import run_full_hydrocarbons_analysis

        # Generate a hydrocarbons law
        instrument, roadmap = generate_hydrocarbons_instrument(
            titulo="Reforma LOH 2026",
            objeto="reformar el régimen de participación en empresas mixtas"
        )

        # Analyze it with hydrocarbons playbook
        analysis = run_full_hydrocarbons_analysis(
            case_name="Reforma_LOH_Analysis",
            activity="EXPLOTACION",
            contract="EMPRESA_MIXTA",
            participacion_pdvsa=60.0
        )

        self.assertIsNotNone(instrument)
        self.assertIsNotNone(analysis)
        self.assertGreater(len(instrument.articulos), 0)
        self.assertGreater(len(analysis.applicable_loh_articles), 0)

    def test_contract_review_with_hydrocarbons(self):
        """Test contract review for hydrocarbons contract."""
        from contract_review import review_contract
        from hydrocarbons_playbook import analyze_empresa_mixta

        # Simulate a hydrocarbons contract
        contract_text = """
        CONTRATO DE EMPRESA MIXTA

        Entre Petróleos de Venezuela S.A. (PDVSA) con una participación del 60%,
        y Chevron Corporation con una participación del 40%.

        CLÁUSULA PRIMERA: OBJETO
        El objeto es la explotación del campo petrolero Petroboscan.

        CLÁUSULA SEGUNDA: JURISDICCIÓN
        Los tribunales de Venezuela serán exclusivamente competentes.
        """

        review = review_contract(contract_text, "Empresa Mixta Review")

        # Also analyze with hydrocarbons playbook
        empresa_analysis = analyze_empresa_mixta(
            nombre="Petroboscan",
            participacion_pdvsa=60.0,
            socio_privado="Chevron"
        )

        self.assertIsNotNone(review)
        self.assertTrue(empresa_analysis["compliance"]["art_9_loh"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
