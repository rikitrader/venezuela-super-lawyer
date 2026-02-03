# Venezuela Super Lawyer

```
        ██╗   ██╗███████╗███╗   ██╗███████╗███████╗██╗   ██╗███████╗██╗      █████╗
        ██║   ██║██╔════╝████╗  ██║██╔════╝╚══███╔╝██║   ██║██╔════╝██║     ██╔══██╗
        ██║   ██║█████╗  ██╔██╗ ██║█████╗    ███╔╝ ██║   ██║█████╗  ██║     ███████║
        ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██╔══╝   ███╔╝  ██║   ██║██╔══╝  ██║     ██╔══██║
         ╚████╔╝ ███████╗██║ ╚████║███████╗███████╗╚██████╔╝███████╗███████╗██║  ██║
          ╚═══╝  ╚══════╝╚═╝  ╚═══╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

        ███████╗██╗   ██╗██████╗ ███████╗██████╗     ██╗      █████╗ ██╗    ██╗██╗   ██╗███████╗██████╗
        ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗    ██║     ██╔══██╗██║    ██║╚██╗ ██╔╝██╔════╝██╔══██╗
        ███████╗██║   ██║██████╔╝█████╗  ██████╔╝    ██║     ███████║██║ █╗ ██║ ╚████╔╝ █████╗  ██████╔╝
        ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗    ██║     ██╔══██║██║███╗██║  ╚██╔╝  ██╔══╝  ██╔══██╗
        ███████║╚██████╔╝██║     ███████╗██║  ██║    ███████╗██║  ██║╚███╔███╔╝   ██║   ███████╗██║  ██║
        ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝    ╚═╝   ╚══════╝╚═╝  ╚═╝

    ═══════════════════════════════════════════════════════════════════════════════════════════════════════
    ║                              AI LEGAL OPERATING SYSTEM v2.0                                         ║
    ═══════════════════════════════════════════════════════════════════════════════════════════════════════
```

---

## What is Venezuela Super Lawyer?

**Venezuela Super Lawyer** is an AI-powered legal operating system specialized in Venezuelan law. It provides doctoral-level expertise across multiple legal domains, enabling comprehensive legal research, document drafting, constitutional analysis, and case management.

### Key Capabilities

| Capability | Description |
|------------|-------------|
| **Constitutional Analysis** | Full CRBV analysis with OEA vs SAPI comparison |
| **Legal Document Drafting** | Demandas, amparos, contratos, recursos |
| **TSJ Outcome Prediction** | Probability analysis for Supreme Court cases |
| **Massive Legal Research** | Search across laws, jurisprudence, and Gaceta Oficial |
| **Law Generation Engine** | Draft complete legal instruments with implementation roadmaps |
| **Legislative Feasibility** | Voting requirements and political viability mapping |

---

## System Architecture

### 17 Specialized Modules

| # | Module | Function |
|---|--------|----------|
| 1 | **Claude Code Skill Mode** | Core functions and deterministic outputs |
| 2 | **Instant Brainstorm Engine** | Auto-trigger legal issue identification (10-25 issues) |
| 3 | **Massive Query Expansion** | Generate comprehensive search queries |
| 4 | **Massive Research Engine** | Research across all Venezuelan legal sources |
| 5 | **Constitution Diff Engine** | Compare OEA vs SAPI constitutional texts |
| 6 | **Gaceta Oficial Auto-Updater** | Verify norm currency and amendments |
| 7 | **Hydrocarbons Law Playbook** | Oil, gas, energy sector expertise |
| 8 | **TSJ-Style Analysis Template** | Constitutional analysis framework |
| 9 | **Contract Drafting Assistant** | Venezuelan-compliant contract generation |
| 10 | **Automated Case Output System** | Standardized case folder structure |
| 11 | **TSJ / Gaceta Ingestion** | Jurisprudence and gazette database |
| 12 | **Constitutionality Test Engine** | Automated constitutional compliance tests |
| 13 | **TSJ Decision-Prediction** | Outcome probability with reasoning |
| 14 | **Massive Case Analysis** | End-to-end case analysis pipeline |
| 15 | **Automatic Report Generation** | Markdown reports with timestamps |
| 16 | **Law & Resolution Generation** | Legislative drafting with roadmaps |
| 17 | **Voting Map Engine** | Legislative feasibility and quorum analysis |

---

## Legal Sources

### Primary Constitutional Sources
- **CRBV (OEA)**: https://www.oas.org/dil/esp/constitucion_venezuela.pdf
- **CRBV (SAPI)**: https://sapi.gob.ve/wp-content/uploads/2020/11/CONSTITUCION.pdf

### Subordinate Sources
- Gaceta Oficial (Ordinaria y Extraordinaria)
- TSJ Jurisprudence (all 7 chambers)
- Código Civil, Código de Comercio, Código de Procedimiento Civil
- Ley Orgánica de Amparo, LOPA, Ley de Hidrocarburos
- Sector-specific regulations and resolutions

---

## Installation

### Prerequisites
- Python 3.8+
- Claude Code CLI
- Git

### Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/rikitrader/venezuela-super-lawyer.git
cd venezuela-super-lawyer

# 2. Set password (REQUIRED)
export VSL_ACCESS_KEY="<your_password>"

# 3. Verify access
python3 scripts/security.py verify

# 4. Run
python3 scripts/report_manager.py list
```

---

## Security

### Password Protection

All core scripts require authentication via `VSL_ACCESS_KEY` environment variable.

```
╔═══════════════════════════════════════════════════════════════╗
║                    🔒 PASSWORD PROTECTED 🔒                   ║
╠═══════════════════════════════════════════════════════════════╣
║  • Scripts require VSL_ACCESS_KEY to execute                  ║
║  • Invalid attempts are logged to audit file                  ║
║  • Password verified via SHA-256 hash (not stored plaintext)  ║
╚═══════════════════════════════════════════════════════════════╝
```

### Protected Files
- `SKILL.md` - Core skill definition
- `scripts/*.py` - All Python scripts
- `reportes_legales/*.md` - Generated reports
- `cases/**/*` - Case files

---

## Directory Structure

```
venezuela-super-lawyer/
├── SKILL.md                    # Core skill definition
├── README.md                   # This file
├── LICENSE                     # Proprietary license
├── .env.example                # Environment template
├── scripts/
│   ├── security.py             # Authentication module
│   ├── report_manager.py       # Report generation
│   ├── init_case.py            # Case initialization
│   ├── constitutional_test.py  # Constitutionality tests
│   ├── gaceta_verify.py        # Gaceta verification
│   └── tsj_search.py           # TSJ jurisprudence search
├── references/
│   ├── crbv_articles.md        # Constitutional articles
│   ├── legislative_avenues.md  # 9 legislative avenues guide
│   ├── tsj_salas.md            # TSJ chambers reference
│   └── hydrocarbons_framework.md
├── assets/
│   └── templates/
│       ├── instrumento_legal.md
│       ├── demanda_civil.md
│       └── amparo_constitucional.md
├── reportes_legales/           # Generated reports
├── cases/                      # Case files
└── logs/                       # Audit logs
```

---

## Usage with Claude Code

```bash
# Invoke the skill
/venezuela-super-lawyer

# Or use shorthand
/ven
```

---

## Disclaimers

### Development Status

```
╔═══════════════════════════════════════════════════════════════╗
║                    ALPHA / FUTURE DEVELOPMENT                 ║
╠═══════════════════════════════════════════════════════════════╣
║  • Features may change without notice                         ║
║  • Not recommended for production use                         ║
║  • Designed for future development                            ║
║  Version: 2.0.0-alpha | Updated: 2026-02-03                   ║
╚═══════════════════════════════════════════════════════════════╝
```

### Legal Disclaimer

**THIS SOFTWARE DOES NOT CONSTITUTE LEGAL ADVICE.**

- Information should be verified by a licensed Venezuelan attorney
- Based on publicly available legal sources
- May not reflect the most recent legal changes
- Authors are NOT liable for damages arising from use

---

## Copyright

```
═══════════════════════════════════════════════════════════════════════════════
                         VENEZUELA SUPER LAWYER
                      AI Legal Operating System v2.0
═══════════════════════════════════════════════════════════════════════════════

                         © 2026 All Rights Reserved

            "Supremacía Constitucional • Precisión Jurídica • Soluciones Reales"

═══════════════════════════════════════════════════════════════════════════════
```

---

**Version:** 2.0.0-alpha
**Last Updated:** 2026-02-03
**Status:** Password Protected | Public Repository
