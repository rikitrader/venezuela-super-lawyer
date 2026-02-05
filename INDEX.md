# Venezuela Super Lawyer - Índice de Componentes

> Sistema Operativo Legal AI para Derecho Venezolano v2.0

---

## Estructura del Skill

```
venezuela-super-lawyer/
├── SKILL.md                    # Documento principal (instrucciones)
├── INDEX.md                    # Este archivo
├── README.md                   # Documentación general
│
├── scripts/                    # Módulos ejecutables
│   ├── init_case.py           # Inicializador de casos
│   ├── constitutional_test.py  # Test de constitucionalidad
│   ├── constitution_diff.py    # Motor de diferencias constitucionales
│   ├── tsj_search.py          # Búsqueda en base de jurisprudencia TSJ
│   ├── gaceta_verify.py       # Verificación de normas en Gaceta
│   ├── tsj_scraper.py         # Scraper web del TSJ
│   ├── gaceta_scraper.py      # Scraper web de Gaceta Oficial
│   ├── report_manager.py      # Gestor de reportes legales
│   └── security.py            # Módulo de seguridad
│
├── references/                 # Documentación de referencia
│   ├── crbv_articles.md       # Artículos clave de la CRBV
│   ├── tsj_salas.md           # Guía de Salas del TSJ
│   ├── hydrocarbons_framework.md  # Marco legal de hidrocarburos
│   ├── legislative_avenues.md # Vías legislativas
│   ├── legal_terminology.md   # Terminología jurídica
│   └── gaceta_guide.md        # Guía de Gaceta Oficial
│
├── assets/
│   ├── templates/             # Plantillas de documentos
│   │   ├── demanda_civil.md
│   │   ├── amparo_constitucional.md
│   │   ├── contestacion.md
│   │   ├── informe_legal.md
│   │   ├── instrumento_legal.md
│   │   ├── contrato_empresas_mixtas.md
│   │   ├── decreto.md
│   │   └── resolucion.md
│   ├── escudo_ascii.txt       # Arte ASCII del escudo
│   └── logo_epic.txt          # Logo del sistema
│
├── reportes_legales/          # Reportes generados
│   └── INDEX.md               # Índice de reportes
│
├── cases/                     # Casos de trabajo
│
├── cache/                     # Cache de scrapers
│   ├── tsj/                   # Cache de TSJ
│   └── gaceta/                # Cache de Gaceta
│
└── logs/                      # Logs del sistema
    └── audit.log              # Log de auditoría
```

---

## Scripts Disponibles

### 1. init_case.py - Inicializador de Casos
```bash
python3 scripts/init_case.py <case_number> <client_name> [--tipo civil|penal|administrativo|constitucional|laboral|mercantil] [base_path]
```
Crea estructura de directorios para un nuevo caso legal.

### 2. constitutional_test.py - Test de Constitucionalidad
```bash
python3 scripts/constitutional_test.py "<descripción de la norma>"
python3 scripts/constitutional_test.py --json <archivo_input.json>
```
Ejecuta batería de 5 tests constitucionales (supremacía, derechos, competencia, debido proceso, interés público).

### 3. constitution_diff.py - Motor de Diferencias
```bash
python3 scripts/constitution_diff.py analyze "Proyecto de Ley" --text "contenido"
python3 scripts/constitution_diff.py analyze "Proyecto" --file proyecto.txt
python3 scripts/constitution_diff.py article 302
python3 scripts/constitution_diff.py eternity
python3 scripts/constitution_diff.py stats
```
Compara legislación propuesta contra la CRBV con análisis de riesgos.

### 4. tsj_search.py - Búsqueda de Jurisprudencia
```bash
python3 scripts/tsj_search.py buscar "control difuso"
python3 scripts/tsj_search.py sala CONSTITUCIONAL
python3 scripts/tsj_search.py caso "168/2008"
python3 scripts/tsj_search.py stats
```
Busca en la base de datos local de 70+ casos emblemáticos del TSJ.

### 5. gaceta_verify.py - Verificación de Normas
```bash
python3 scripts/gaceta_verify.py buscar "hidrocarburos"
python3 scripts/gaceta_verify.py tipo LEY_ORGANICA
python3 scripts/gaceta_verify.py norma "CRBV"
python3 scripts/gaceta_verify.py stats
```
Verifica publicación de normas en la base de datos de 45+ leyes principales.

### 6. tsj_scraper.py - Scraper del TSJ
```bash
python3 scripts/tsj_scraper.py search "amparo constitucional"
python3 scripts/tsj_scraper.py search "expropiación" --sala CONSTITUCIONAL
python3 scripts/tsj_scraper.py recent CONSTITUCIONAL --days 30
python3 scripts/tsj_scraper.py verify 168 CONSTITUCIONAL --year 2023
python3 scripts/tsj_scraper.py status
python3 scripts/tsj_scraper.py clear-cache
```
Scraper web para jurisprudencia en vivo del TSJ (con rate limiting y cache).

### 7. gaceta_scraper.py - Scraper de Gaceta Oficial
```bash
python3 scripts/gaceta_scraper.py search "Ley Orgánica del Trabajo"
python3 scripts/gaceta_scraper.py gaceta 6.152
python3 scripts/gaceta_scraper.py verify "LOTTT" --numero 6.076
python3 scripts/gaceta_scraper.py recent --days 30
python3 scripts/gaceta_scraper.py status
python3 scripts/gaceta_scraper.py clear-cache
```
Scraper web para verificación de normas en Gaceta Oficial.

### 8. report_manager.py - Gestor de Reportes
```bash
python3 scripts/report_manager.py new '<tema>' [--case <caso>] [--client <cliente>]
python3 scripts/report_manager.py append <report_id> <titulo_seccion> <archivo_contenido>
python3 scripts/report_manager.py list
python3 scripts/report_manager.py latest
python3 scripts/report_manager.py toc <report_id>
```
Gestiona la creación, actualización y listado de reportes legales.

### 9. security.py - Módulo de Seguridad
```bash
python3 scripts/security.py verify
python3 scripts/security.py check <archivo>
python3 scripts/security.py audit
```
Control de acceso y auditoría del sistema.

---

## Referencias Disponibles

| Archivo | Contenido | Uso |
|---------|-----------|-----|
| `crbv_articles.md` | Artículos clave de la Constitución | Análisis constitucional |
| `tsj_salas.md` | Estructura y competencias del TSJ | Identificar jurisdicción |
| `hydrocarbons_framework.md` | Marco legal petrolero | Casos de hidrocarburos |
| `legislative_avenues.md` | Vías para crear/modificar leyes | Estrategia legislativa |
| `legal_terminology.md` | Glosario jurídico venezolano | Redacción de documentos |
| `gaceta_guide.md` | Sistema de Gaceta Oficial | Verificación de vigencia |

---

## Plantillas Disponibles

| Plantilla | Descripción |
|-----------|-------------|
| `demanda_civil.md` | Demanda civil genérica |
| `amparo_constitucional.md` | Acción de amparo constitucional |
| `contestacion.md` | Contestación de demanda |
| `informe_legal.md` | Informe/dictamen legal |
| `instrumento_legal.md` | Ley/Código estructurado |
| `contrato_empresas_mixtas.md` | Contrato para empresas mixtas petroleras |
| `decreto.md` | Decreto con fuerza de ley |
| `resolucion.md` | Resolución administrativa |

---

## Bases de Datos Integradas

### Jurisprudencia TSJ (tsj_search.py)
- **70+ casos emblemáticos** de todas las Salas
- Cobertura: Sala Constitucional, SPA, SCC, SCP, SCS, Electoral, Plena
- Incluye: número, fecha, ponente, resumen, principios establecidos
- Búsqueda por: keywords, sala, fecha, materia

### Normativa Vigente (gaceta_verify.py)
- **45+ normas principales** del ordenamiento jurídico
- Incluye: Constitución, 6 Códigos, 20+ Leyes Orgánicas
- Datos: nombre, Gaceta, fecha, status, reformas
- Materias: Constitucional, Procesal, Laboral, Hidrocarburos, Tributaria

### Base Constitucional (constitution_diff.py)
- **40+ artículos clave** de la CRBV analizados
- Identificación de cláusulas pétreas
- Requisitos de ley orgánica
- Análisis de conflictos y riesgos

---

## Módulos del Sistema (SKILL.md)

1. **Legal Issue Brainstormer** - Identificación de problemas legales
2. **Query Expansion Engine** - Expansión de consultas de investigación
3. **Massive Research Engine** - Investigación masiva paralela
4. **TSJ Analyzer** - Análisis estilo TSJ
5. **Constitution Diff** - Comparación constitucional
6. **Gaceta Verificator** - Verificación en Gaceta Oficial
7. **Law Generator** - Generador de leyes
8. **Resolution Generator** - Generador de resoluciones
9. **Voting Map Engine** - Mapa de votación legislativa
10. **Document Drafter** - Redactor de documentos
11. **Case Predictor** - Predicción de resultados judiciales
12. **Citation Formatter** - Formateador de citas legales
13. **Deadline Calculator** - Calculador de plazos procesales
14. **Contract Analyzer** - Analizador de contratos
15. **Compliance Checker** - Verificador de cumplimiento
16. **Report Generator** - Generador de reportes
17. **Knowledge Base** - Base de conocimientos

---

## Configuración del Sistema

### Variables de Entorno
```bash
export VSL_ACCESS_KEY="<clave_de_acceso>"  # Requerido para módulos protegidos
```

### Cache
- TSJ: `cache/tsj/` (expira en 24 horas)
- Gaceta: `cache/gaceta/` (expira en 48 horas)
- Limpiar: `python3 scripts/<scraper>.py clear-cache`

### Logs
- Auditoría: `logs/audit.log`
- Formato: `[timestamp] [status] action | details`

---

## Actualizaciones

### Versión 2.0 (Febrero 2026)
- Expansión de base TSJ a 70+ casos
- Expansión de base Gaceta a 45+ normas
- Nuevo: Constitution Diff Engine
- Nuevo: Web Scrapers (TSJ + Gaceta)
- Nuevas plantillas: Decreto, Resolución
- Sistema de cache mejorado
- Análisis de riesgo constitucional

---

## Soporte

Para reportar problemas o solicitar funcionalidades:
1. Crear issue en el repositorio
2. Incluir: versión, comando ejecutado, error obtenido
3. Adjuntar logs relevantes (sin información sensible)

---

*Venezuela Super Lawyer v2.0 - Sistema Operativo Legal AI*
*Desarrollado para profesionales del derecho venezolano*
