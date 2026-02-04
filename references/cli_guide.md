# Venezuela Super Lawyer - CLI Reference Guide

Comprehensive command-line interface documentation for all VSL scripts.

## Quick Reference

| Script | Purpose | Example |
|--------|---------|---------|
| `gaceta_verify.py` | Search/verify Gaceta norms | `python3 gaceta_verify.py search hidrocarburos` |
| `tsj_search.py` | Search TSJ jurisprudence | `python3 tsj_search.py search amparo` |
| `voting_map.py` | Legislative feasibility | `python3 voting_map.py analyze "Ley de Amnistía"` |
| `constitution_diff.py` | Constitutional analysis | `python3 constitution_diff.py analyze proyecto.txt` |
| `constitutional_test.py` | Constitutionality test | `python3 constitutional_test.py test proyecto.txt` |
| `report_manager.py` | Generate legal reports | `python3 report_manager.py new "Caso X"` |
| `init_case.py` | Initialize case folder | `python3 init_case.py "Caso Hidrocarburos"` |
| `gaceta_scraper.py` | Scrape Gaceta Oficial | `python3 gaceta_scraper.py search "LOTTT"` |
| `tsj_scraper.py` | Scrape TSJ decisions | `python3 tsj_scraper.py search "amparo"` |
| `security.py` | Authentication module | `python3 security.py verify` |

---

## gaceta_verify.py

Search and verify Venezuelan legal norms in the Gaceta Oficial database.

### Commands

```bash
# Search for norms by keyword
python3 gaceta_verify.py search <keyword>
python3 gaceta_verify.py search "hidrocarburos"
python3 gaceta_verify.py search "trabajo" --type LEY_ORGANICA

# Look up a specific norm
python3 gaceta_verify.py lookup <norm_key>
python3 gaceta_verify.py lookup CRBV
python3 gaceta_verify.py lookup LOTTT

# List norms by type
python3 gaceta_verify.py list --type LEY_ORGANICA
python3 gaceta_verify.py list --type CODIGO
python3 gaceta_verify.py list --type DECRETO

# Get database statistics
python3 gaceta_verify.py stats

# Export database to JSON
python3 gaceta_verify.py export --output norms.json
```

### Options

| Option | Description |
|--------|-------------|
| `--type TYPE` | Filter by norm type (LEY_ORGANICA, CODIGO, DECRETO, etc.) |
| `--max N` | Maximum results to return (default: 10) |
| `--json` | Output in JSON format |
| `-v, --verbose` | Show full details |

### Norm Types

- `CONSTITUCION` - Constitution
- `LEY_ORGANICA` - Organic Law
- `LEY_ORDINARIA` - Ordinary Law
- `CODIGO` - Code
- `DECRETO_LEY` - Decree-Law
- `DECRETO` - Decree
- `REGLAMENTO` - Regulation
- `RESOLUCION` - Resolution

---

## tsj_search.py

Search TSJ (Tribunal Supremo de Justicia) jurisprudence database.

### Commands

```bash
# Search by keyword
python3 tsj_search.py search <keyword>
python3 tsj_search.py search "amparo constitucional"
python3 tsj_search.py search "debido proceso" --sala CONSTITUCIONAL

# Search by Sala (chamber)
python3 tsj_search.py sala CONSTITUCIONAL
python3 tsj_search.py sala POLITICO_ADMINISTRATIVA

# Search binding precedents
python3 tsj_search.py vinculantes
python3 tsj_search.py vinculantes --sala CONSTITUCIONAL

# Search hydrocarbon cases
python3 tsj_search.py hidrocarburos

# Get database statistics
python3 tsj_search.py stats
```

### Options

| Option | Description |
|--------|-------------|
| `--sala SALA` | Filter by TSJ chamber |
| `--max N` | Maximum results (default: 10) |
| `--json` | Output in JSON format |
| `-v, --verbose` | Show full details including resumen |

### Salas (Chambers)

- `CONSTITUCIONAL` - Constitutional Chamber
- `POLITICO_ADMINISTRATIVA` - Administrative-Political Chamber
- `CASACION_CIVIL` - Civil Cassation
- `CASACION_PENAL` - Criminal Cassation
- `CASACION_SOCIAL` - Social Cassation
- `ELECTORAL` - Electoral Chamber
- `PLENA` - Full Court

---

## voting_map.py

Analyze legislative voting requirements and political feasibility.

### Commands

```bash
# Analyze a legislative proposal
python3 voting_map.py analyze <title> [--type TYPE]
python3 voting_map.py analyze "Ley de Amnistía" --type LEY_ORDINARIA
python3 voting_map.py analyze "Reforma Constitucional" --type REFORMA

# Compare majority types
python3 voting_map.py compare
python3 voting_map.py compare --body AN

# Get legislative timeline
python3 voting_map.py timeline <type>
python3 voting_map.py timeline LEY_ORGANICA
python3 voting_map.py timeline ENMIENDA

# Calculate votes needed
python3 voting_map.py votes <type>
python3 voting_map.py votes LEY_ORDINARIA
python3 voting_map.py votes REFORMA
```

### Options

| Option | Description |
|--------|-------------|
| `--type TYPE` | Norm type (LEY_ORDINARIA, LEY_ORGANICA, ENMIENDA, REFORMA) |
| `--favorable N` | Estimated favorable votes (default: 100) |
| `--json` | Output in JSON format |
| `-v, --verbose` | Show detailed analysis |

### Norm Types for Voting

- `LEY_ORDINARIA` - Ordinary Law (simple majority)
- `LEY_ORGANICA` - Organic Law (2/3 majority)
- `LEY_HABILITANTE` - Enabling Law (3/5 majority)
- `ENMIENDA` - Constitutional Amendment (referendum required)
- `REFORMA` - Constitutional Reform (referendum required)
- `CONSTITUYENTE` - Constituent Assembly

---

## constitution_diff.py

Analyze legislative proposals for constitutional conflicts.

### Commands

```bash
# Analyze a legislative text
python3 constitution_diff.py analyze <file>
python3 constitution_diff.py analyze proyecto.txt
python3 constitution_diff.py analyze --text "Texto del proyecto..."

# Get article information
python3 constitution_diff.py article <number>
python3 constitution_diff.py article 49
python3 constitution_diff.py article 302

# Search articles by keyword
python3 constitution_diff.py search <keyword>
python3 constitution_diff.py search "debido proceso"
python3 constitution_diff.py search "hidrocarburos"

# List eternity clauses
python3 constitution_diff.py eternity

# Get database statistics
python3 constitution_diff.py stats
```

### Options

| Option | Description |
|--------|-------------|
| `--text TEXT` | Analyze text directly instead of file |
| `--area AREA` | Filter articles by constitutional area |
| `--json` | Output in JSON format |
| `-v, --verbose` | Show detailed conflict analysis |

### Output Fields

- **Conflicts**: Constitutional conflicts detected
- **Severity**: CRITICAL, HIGH, MEDIUM, LOW
- **Risk Score**: 0.0 to 1.0
- **Compliance**: Percentage of constitutional compliance
- **Recommendations**: Suggested amendments

---

## constitutional_test.py

Run automated constitutionality tests on legislative proposals.

### Commands

```bash
# Run all tests
python3 constitutional_test.py test <file>
python3 constitutional_test.py test proyecto.txt

# Run specific test
python3 constitutional_test.py test proyecto.txt --type SUPREMACY
python3 constitutional_test.py test proyecto.txt --type RIGHTS_IMPACT

# Generate full report
python3 constitutional_test.py report <file> --output informe.md
```

### Test Types

- `SUPREMACY` - Constitutional supremacy test
- `RIGHTS_IMPACT` - Human rights impact assessment
- `COMPETENCE` - Competence verification
- `DUE_PROCESS` - Due process compliance
- `PUBLIC_INTEREST` - Public interest analysis

### Options

| Option | Description |
|--------|-------------|
| `--type TYPE` | Run specific test only |
| `--output FILE` | Save report to file |
| `--json` | Output in JSON format |

---

## report_manager.py

Generate and manage legal reports.

### Commands

```bash
# Create new report
python3 report_manager.py new <title>
python3 report_manager.py new "Análisis Caso Hidrocarburos"

# List all reports
python3 report_manager.py list

# Get latest report
python3 report_manager.py latest

# Append to report
python3 report_manager.py append <report_id> --section "Conclusiones" --content "..."

# Generate table of contents
python3 report_manager.py toc <report_id>
```

### Options

| Option | Description |
|--------|-------------|
| `--section NAME` | Section name for append |
| `--content TEXT` | Content to append |
| `--output DIR` | Output directory |

### Environment Variables

```bash
export VSL_ACCESS_KEY=<your-access-key>  # Required for authentication
```

---

## init_case.py

Initialize a new case folder with standardized structure.

### Commands

```bash
# Initialize new case
python3 init_case.py <case_name>
python3 init_case.py "Caso Petrolera Nacional"
python3 init_case.py "Amparo Constitucional - Cliente X"
```

### Created Structure

```
cases/<case_name>/
├── MANIFEST.md           # Case manifest
├── INTAKE.json          # Client intake form
├── UPDATES.log          # Case updates log
├── docs/                # Case documents
│   ├── pleadings/      # Legal pleadings
│   ├── evidence/       # Evidence files
│   └── correspondence/ # Communications
├── research/           # Legal research
│   ├── jurisprudence/ # TSJ cases
│   ├── legislation/   # Applicable norms
│   └── doctrine/      # Legal doctrine
└── drafts/            # Document drafts
```

---

## gaceta_scraper.py

Scrape Gaceta Oficial for live norm verification.

### Commands

```bash
# Search Gaceta
python3 gaceta_scraper.py search <query>
python3 gaceta_scraper.py search "Ley Orgánica del Trabajo"
python3 gaceta_scraper.py search "hidrocarburos" --tipo LEY_ORGANICA

# Get specific Gaceta
python3 gaceta_scraper.py gaceta <numero>
python3 gaceta_scraper.py gaceta 6.152

# Verify norm publication
python3 gaceta_scraper.py verify <name> --numero <gaceta_num>
python3 gaceta_scraper.py verify "CRBV" --numero 5.908

# Get recent Gacetas
python3 gaceta_scraper.py recent --days 30

# Check scraper status
python3 gaceta_scraper.py status

# Clear cache
python3 gaceta_scraper.py clear-cache
```

### Options

| Option | Description |
|--------|-------------|
| `--tipo TYPE` | Filter by norm type |
| `--max N` | Maximum results |
| `--no-cache` | Skip cache |
| `-v, --verbose` | Show full details |

---

## tsj_scraper.py

Scrape TSJ website for live jurisprudence.

### Commands

```bash
# Search TSJ
python3 tsj_scraper.py search <query>
python3 tsj_scraper.py search "control constitucional"
python3 tsj_scraper.py search "amparo" --sala CONSTITUCIONAL

# Get recent decisions
python3 tsj_scraper.py recent <sala>
python3 tsj_scraper.py recent CONSTITUCIONAL --days 30

# Verify decision exists
python3 tsj_scraper.py verify <numero> <sala>
python3 tsj_scraper.py verify 123 CONSTITUCIONAL --year 2024

# Check scraper status
python3 tsj_scraper.py status

# Clear cache
python3 tsj_scraper.py clear-cache
```

### Options

| Option | Description |
|--------|-------------|
| `--sala SALA` | Filter by TSJ chamber |
| `--days N` | Days back for recent decisions |
| `--max N` | Maximum results |
| `--no-cache` | Skip cache |
| `-v, --verbose` | Show full details |

---

## security.py

Authentication and access control module.

### Commands

```bash
# Verify access key
python3 security.py verify

# Check if file is protected
python3 security.py check <file>
python3 security.py check SKILL.md

# View audit log
python3 security.py audit
```

### Environment Variables

```bash
export VSL_ACCESS_KEY=<your-access-key>  # Set access key
```

---

## Global Options

These options work across all scripts:

| Option | Description |
|--------|-------------|
| `--help, -h` | Show help message |
| `--version` | Show script version |
| `--json` | Output in JSON format (where supported) |
| `-v, --verbose` | Show detailed output |
| `--no-cache` | Skip cache (scrapers only) |

---

## Examples

### Complete Workflow: Analyze Legislative Proposal

```bash
# 1. Initialize case folder
python3 init_case.py "Ley de Amnistía 2024"

# 2. Search related jurisprudence
python3 tsj_search.py search "amnistía" --sala CONSTITUCIONAL -v

# 3. Verify related norms
python3 gaceta_verify.py search "amnistía"

# 4. Run constitutional analysis
python3 constitution_diff.py analyze proyecto_amnistia.txt

# 5. Run constitutionality tests
python3 constitutional_test.py test proyecto_amnistia.txt

# 6. Check voting requirements
python3 voting_map.py analyze "Ley de Amnistía" --type LEY_ORDINARIA

# 7. Generate legal report
python3 report_manager.py new "Análisis Ley de Amnistía"
```

### Research Hydrocarbon Law

```bash
# Find hydrocarbon cases
python3 tsj_search.py hidrocarburos -v

# Search related norms
python3 gaceta_verify.py search "hidrocarburos" --type LEY_ORGANICA

# Get constitutional articles
python3 constitution_diff.py search "hidrocarburos"
python3 constitution_diff.py article 302
python3 constitution_diff.py article 303
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication error |
| 3 | File not found |
| 4 | Network error |
| 5 | Parse error |

---

## Troubleshooting

### Authentication Errors

```bash
# Set access key
export VSL_ACCESS_KEY=<your-key>

# Verify
python3 security.py verify
```

### Cache Issues

```bash
# Clear all caches
python3 gaceta_scraper.py clear-cache
python3 tsj_scraper.py clear-cache
```

### Network Issues

```bash
# Check scraper status
python3 gaceta_scraper.py status
python3 tsj_scraper.py status

# Use --no-cache to bypass cache
python3 gaceta_scraper.py search "test" --no-cache
```
