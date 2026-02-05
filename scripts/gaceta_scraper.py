#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Gaceta Oficial Web Scraper Module
Scrapes the Gaceta Oficial de Venezuela for norm verification.

Gaceta Website: http://www.tsj.gob.ve/gaceta-oficial
Alternative: https://pandectasdigital.com/
"""

import os
import sys
import json
import time
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from urllib.parse import urljoin, quote_plus, urlencode
import html

# ═══════════════════════════════════════════════════════════════════════════════
#                         CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Base URLs for Gaceta Oficial
GACETA_TSJ_URL = "http://www.tsj.gob.ve/gaceta-oficial"
GACETA_SEARCH_URL = "http://www.tsj.gob.ve/gaceta-oficial/-/gacetas"

# Alternative source (often more reliable)
PANDECTAS_URL = "https://pandectasdigital.com"
PANDECTAS_SEARCH = f"{PANDECTAS_URL}/busqueda"

# Rate limiting
MIN_REQUEST_INTERVAL = 2.0  # Minimum seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # Seconds to wait before retry

# Cache configuration
CACHE_DIR = Path(__file__).parent.parent / "cache" / "gaceta"
CACHE_EXPIRY_HOURS = 48  # Longer cache for Gaceta (norms change less frequently)

# ═══════════════════════════════════════════════════════════════════════════════
#                         DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class GacetaType(Enum):
    """Types of Gaceta Oficial."""
    ORDINARIA = "Gaceta Oficial Ordinaria"
    EXTRAORDINARIA = "Gaceta Oficial Extraordinaria"
    OFICIAL = "Gaceta Oficial"


class NormType(Enum):
    """Types of legal norms."""
    CONSTITUCION = "Constitución"
    LEY_ORGANICA = "Ley Orgánica"
    LEY_ORDINARIA = "Ley Ordinaria"
    CODIGO = "Código"
    DECRETO_LEY = "Decreto con Rango, Valor y Fuerza de Ley"
    DECRETO = "Decreto"
    REGLAMENTO = "Reglamento"
    RESOLUCION = "Resolución"
    PROVIDENCIA = "Providencia Administrativa"
    AVISO = "Aviso Oficial"
    OTRO = "Otro"


class NormStatus(Enum):
    """Status of a norm."""
    VIGENTE = "Vigente"
    DEROGADA = "Derogada"
    REFORMADA = "Reformada"
    PARCIALMENTE_DEROGADA = "Parcialmente Derogada"
    DESCONOCIDO = "Desconocido"


@dataclass
class GacetaEntry:
    """Represents a Gaceta Oficial entry."""
    numero: str
    fecha: str
    tipo: GacetaType
    contenido: List[str] = field(default_factory=list)
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


@dataclass
class ScrapedNorm:
    """Represents a norm scraped from Gaceta Oficial."""
    nombre: str
    tipo: NormType
    gaceta_numero: str
    gaceta_fecha: str
    gaceta_tipo: GacetaType
    fecha_publicacion: str
    status: NormStatus = NormStatus.DESCONOCIDO
    resumen: str = ""
    articulos_clave: List[str] = field(default_factory=list)
    reformas: List[str] = field(default_factory=list)
    url: str = ""
    pdf_url: str = ""
    texto_parcial: str = ""
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


@dataclass
class GacetaSearchResult:
    """Search results container."""
    query: str
    tipo_norm: Optional[NormType]
    fecha_desde: Optional[str]
    fecha_hasta: Optional[str]
    total_results: int
    norms: List[ScrapedNorm]
    gacetas: List[GacetaEntry]
    search_time: float
    cached: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
#                         CACHE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def get_cache_path(key: str) -> Path:
    """Get cache file path for a given key."""
    hash_key = hashlib.md5(key.encode()).hexdigest()
    return CACHE_DIR / f"{hash_key}.json"


def is_cache_valid(cache_path: Path) -> bool:
    """Check if cache file exists and is not expired."""
    if not cache_path.exists():
        return False

    mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
    expiry = mtime + timedelta(hours=CACHE_EXPIRY_HOURS)
    return datetime.now() < expiry


def read_cache(key: str) -> Optional[Dict[str, Any]]:
    """Read data from cache if valid."""
    cache_path = get_cache_path(key)
    if is_cache_valid(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def write_cache(key: str, data: Dict[str, Any]) -> None:
    """Write data to cache."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path = get_cache_path(key)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # Silent fail for cache write


def clear_cache() -> int:
    """Clear all cached data. Returns number of files removed."""
    count = 0
    if CACHE_DIR.exists():
        for file in CACHE_DIR.glob("*.json"):
            try:
                file.unlink()
                count += 1
            except Exception:
                pass
    return count


# ═══════════════════════════════════════════════════════════════════════════════
#                         RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """Simple rate limiter for HTTP requests."""

    def __init__(self, min_interval: float = MIN_REQUEST_INTERVAL):
        self.min_interval = min_interval
        self.last_request = 0.0

    def wait(self) -> None:
        """Wait if necessary to respect rate limit."""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()


# Global rate limiter instance
_rate_limiter = RateLimiter()


# ═══════════════════════════════════════════════════════════════════════════════
#                         HTTP CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_url(url: str, use_cache: bool = True, timeout: int = 30) -> Optional[str]:
    """
    Fetch URL content with rate limiting, caching, and retry logic.

    Args:
        url: URL to fetch
        use_cache: Whether to use cached response if available
        timeout: Request timeout in seconds

    Returns:
        Response text or None if failed
    """
    # Check cache first
    if use_cache:
        cached = read_cache(url)
        if cached:
            return cached.get('content')

    try:
        import urllib.request
        import urllib.error
        import ssl
    except ImportError:
        print("ERROR: urllib not available", file=sys.stderr)
        return None

    for attempt in range(MAX_RETRIES):
        try:
            _rate_limiter.wait()

            # Create SSL context with certificate verification enabled
            ssl_context = ssl.create_default_context()

            # Create request with browser-like headers
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'es-VE,es;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'identity',
                    'Connection': 'keep-alive',
                }
            )

            with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
                # Try different encodings
                content = response.read()
                for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        text = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    text = content.decode('utf-8', errors='replace')

                # Cache successful response
                if use_cache:
                    write_cache(url, {'content': text, 'fetched_at': datetime.now().isoformat()})

                return text

        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {url}", file=sys.stderr)
            if e.code == 429:  # Too Many Requests
                time.sleep(RETRY_DELAY * (attempt + 1))
            elif e.code >= 500:  # Server error
                time.sleep(RETRY_DELAY)
            else:
                return None

        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}", file=sys.stderr)
            time.sleep(RETRY_DELAY)

        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            time.sleep(RETRY_DELAY)

    return None


# ═══════════════════════════════════════════════════════════════════════════════
#                         HTML PARSING
# ═══════════════════════════════════════════════════════════════════════════════

def clean_html_text(text: str) -> str:
    """Clean HTML text, removing tags and normalizing whitespace."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = html.unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def detect_norm_type(text: str) -> NormType:
    """Detect norm type from text."""
    text_lower = text.lower()

    if 'constitución' in text_lower:
        return NormType.CONSTITUCION
    elif 'ley orgánica' in text_lower or 'ley organica' in text_lower:
        return NormType.LEY_ORGANICA
    elif 'código' in text_lower or 'codigo' in text_lower:
        return NormType.CODIGO
    elif 'decreto con rango' in text_lower or 'decreto-ley' in text_lower:
        return NormType.DECRETO_LEY
    elif 'decreto' in text_lower:
        return NormType.DECRETO
    elif 'reglamento' in text_lower:
        return NormType.REGLAMENTO
    elif 'resolución' in text_lower or 'resolucion' in text_lower:
        return NormType.RESOLUCION
    elif 'providencia' in text_lower:
        return NormType.PROVIDENCIA
    elif 'aviso' in text_lower:
        return NormType.AVISO
    elif 'ley' in text_lower:
        return NormType.LEY_ORDINARIA
    else:
        return NormType.OTRO


def detect_gaceta_type(text: str) -> GacetaType:
    """Detect Gaceta type from text."""
    text_lower = text.lower()
    if 'extraordinari' in text_lower:
        return GacetaType.EXTRAORDINARIA
    elif 'ordinari' in text_lower:
        return GacetaType.ORDINARIA
    else:
        return GacetaType.OFICIAL


def parse_date(text: str) -> Optional[str]:
    """Parse date from various formats to DD-MM-YYYY."""
    # Pattern: DD de MES de YYYY
    months = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }

    # Try Spanish format
    match = re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})', text, re.IGNORECASE)
    if match:
        day, month_name, year = match.groups()
        month = months.get(month_name.lower())
        if month:
            return f"{day.zfill(2)}-{month}-{year}"

    # Try DD/MM/YYYY
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if match:
        day, month, year = match.groups()
        return f"{day.zfill(2)}-{month.zfill(2)}-{year}"

    # Try YYYY-MM-DD
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', text)
    if match:
        year, month, day = match.groups()
        return f"{day}-{month}-{year}"

    return None


def parse_gaceta_number(text: str) -> Tuple[Optional[str], Optional[GacetaType]]:
    """Extract Gaceta number and type from text."""
    # Pattern: N° 6.XXX Extraordinario/Ordinario
    match = re.search(
        r'[NnºÚúo°]\s*[°º]?\s*(\d{1,3}(?:[.,]\d{3})*)',
        text
    )
    if match:
        numero = match.group(1).replace(',', '.').replace(' ', '')
        tipo = detect_gaceta_type(text)
        return numero, tipo
    return None, None


def parse_tsj_gaceta_page(html_content: str) -> List[GacetaEntry]:
    """Parse TSJ Gaceta listing page."""
    gacetas = []

    # Look for Gaceta entries - TSJ uses table-based layout
    # Pattern to find individual Gaceta entries
    entry_pattern = re.compile(
        r'<tr[^>]*>.*?'
        r'(?:N[°º]\s*)?(\d{1,3}(?:\.\d{3})*)\s*'
        r'.*?(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{1,2}\s+de\s+\w+\s+de\s+\d{4}).*?'
        r'</tr>',
        re.IGNORECASE | re.DOTALL
    )

    # Find links to PDFs
    pdf_pattern = re.compile(
        r'href=["\']([^"\']*?\.pdf)["\']',
        re.IGNORECASE
    )

    # Try to extract entries
    for match in entry_pattern.finditer(html_content):
        numero = match.group(1)
        fecha_raw = match.group(2)
        fecha = parse_date(fecha_raw) or fecha_raw

        # Determine type
        tipo = detect_gaceta_type(match.group(0))

        # Look for PDF link in this section
        pdf_match = pdf_pattern.search(match.group(0))
        pdf_url = pdf_match.group(1) if pdf_match else None

        gaceta = GacetaEntry(
            numero=numero,
            fecha=fecha,
            tipo=tipo,
            pdf_url=pdf_url
        )
        gacetas.append(gaceta)

    return gacetas


def parse_search_results(html_content: str) -> List[ScrapedNorm]:
    """Parse search results for norms."""
    norms = []

    # Generic pattern for legal document entries
    # This needs to be adapted based on actual HTML structure
    doc_pattern = re.compile(
        r'<(?:div|tr|li)[^>]*class=["\'][^"\']*(?:resultado|item|entry)[^"\']*["\'][^>]*>'
        r'(.*?)'
        r'</(?:div|tr|li)>',
        re.IGNORECASE | re.DOTALL
    )

    for match in doc_pattern.finditer(html_content):
        content = match.group(1)
        content_clean = clean_html_text(content)

        if len(content_clean) < 20:
            continue

        # Extract title/name
        title_match = re.search(
            r'<(?:h[1-6]|strong|b)[^>]*>(.*?)</(?:h[1-6]|strong|b)>',
            content,
            re.IGNORECASE | re.DOTALL
        )
        nombre = clean_html_text(title_match.group(1)) if title_match else content_clean[:100]

        # Extract Gaceta reference
        gaceta_numero, gaceta_tipo = parse_gaceta_number(content)
        gaceta_fecha = parse_date(content)

        # Detect norm type
        tipo = detect_norm_type(nombre)

        # Extract link
        link_match = re.search(r'href=["\']([^"\']+)["\']', content)
        url = link_match.group(1) if link_match else ""

        norm = ScrapedNorm(
            nombre=nombre,
            tipo=tipo,
            gaceta_numero=gaceta_numero or "",
            gaceta_fecha=gaceta_fecha or "",
            gaceta_tipo=gaceta_tipo or GacetaType.OFICIAL,
            fecha_publicacion=gaceta_fecha or "",
            url=url,
            resumen=content_clean[:500] if len(content_clean) > 500 else content_clean
        )
        norms.append(norm)

    return norms


# ═══════════════════════════════════════════════════════════════════════════════
#                         PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def search_gaceta(
    query: str,
    tipo_norm: Optional[NormType] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    max_results: int = 20,
    use_cache: bool = True
) -> GacetaSearchResult:
    """
    Search Gaceta Oficial for norms.

    Args:
        query: Search terms (norm name, topic, etc.)
        tipo_norm: Filter by norm type
        fecha_desde: Start date (DD-MM-YYYY)
        fecha_hasta: End date (DD-MM-YYYY)
        max_results: Maximum results to return
        use_cache: Whether to use cached results

    Returns:
        GacetaSearchResult object
    """
    start_time = time.time()

    # Build cache key
    cache_key = f"search:{query}:{tipo_norm}:{fecha_desde}:{fecha_hasta}"

    # Check cache
    if use_cache:
        cached = read_cache(cache_key)
        if cached:
            norms = [
                ScrapedNorm(
                    tipo=NormType(n['tipo']),
                    gaceta_tipo=GacetaType(n['gaceta_tipo']),
                    status=NormStatus(n['status']),
                    **{k: v for k, v in n.items() if k not in ['tipo', 'gaceta_tipo', 'status']}
                )
                for n in cached.get('norms', [])
            ]
            gacetas = [
                GacetaEntry(
                    tipo=GacetaType(g['tipo']),
                    **{k: v for k, v in g.items() if k != 'tipo'}
                )
                for g in cached.get('gacetas', [])
            ]
            return GacetaSearchResult(
                query=query,
                tipo_norm=tipo_norm,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                total_results=len(norms),
                norms=norms[:max_results],
                gacetas=gacetas,
                search_time=0.0,
                cached=True
            )

    all_norms = []
    all_gacetas = []

    # Build search URL for TSJ
    search_query = quote_plus(query)
    search_url = f"{GACETA_SEARCH_URL}?palabra={search_query}"

    # Fetch from TSJ
    html_content = fetch_url(search_url, use_cache=use_cache)
    if html_content:
        norms = parse_search_results(html_content)
        gacetas = parse_tsj_gaceta_page(html_content)
        all_norms.extend(norms)
        all_gacetas.extend(gacetas)

    # Filter by norm type if specified
    if tipo_norm:
        all_norms = [n for n in all_norms if n.tipo == tipo_norm]

    # Limit results
    all_norms = all_norms[:max_results]

    # Cache results
    if use_cache and (all_norms or all_gacetas):
        write_cache(cache_key, {
            'norms': [
                {**asdict(n), 'tipo': n.tipo.value, 'gaceta_tipo': n.gaceta_tipo.value, 'status': n.status.value}
                for n in all_norms
            ],
            'gacetas': [
                {**asdict(g), 'tipo': g.tipo.value}
                for g in all_gacetas
            ]
        })

    elapsed = time.time() - start_time

    return GacetaSearchResult(
        query=query,
        tipo_norm=tipo_norm,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total_results=len(all_norms),
        norms=all_norms,
        gacetas=all_gacetas,
        search_time=elapsed,
        cached=False
    )


def get_gaceta_by_number(
    numero: str,
    tipo: Optional[GacetaType] = None,
    use_cache: bool = True
) -> Optional[GacetaEntry]:
    """
    Get specific Gaceta by number.

    Args:
        numero: Gaceta number (e.g., "6.152")
        tipo: Gaceta type (Ordinaria/Extraordinaria)
        use_cache: Whether to use cache

    Returns:
        GacetaEntry if found, None otherwise
    """
    # Normalize number format
    numero = numero.replace(',', '.').replace(' ', '')

    cache_key = f"gaceta:{numero}:{tipo}"

    if use_cache:
        cached = read_cache(cache_key)
        if cached:
            return GacetaEntry(
                tipo=GacetaType(cached['tipo']),
                **{k: v for k, v in cached.items() if k != 'tipo'}
            )

    # Search for the specific Gaceta
    result = search_gaceta(numero, use_cache=use_cache, max_results=20)

    for gaceta in result.gacetas:
        if numero in gaceta.numero:
            if tipo is None or gaceta.tipo == tipo:
                if use_cache:
                    write_cache(cache_key, {**asdict(gaceta), 'tipo': gaceta.tipo.value})
                return gaceta

    return None


def verify_norm_publication(
    nombre: str,
    gaceta_numero: Optional[str] = None,
    gaceta_fecha: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify if a norm was published in Gaceta Oficial.

    Args:
        nombre: Name of the norm
        gaceta_numero: Expected Gaceta number
        gaceta_fecha: Expected publication date

    Returns:
        Verification result dict
    """
    result = {
        "verified": False,
        "nombre": nombre,
        "expected_gaceta": gaceta_numero,
        "expected_fecha": gaceta_fecha,
        "found_matches": [],
        "confidence": 0.0,
        "message": ""
    }

    # Search for the norm
    search_result = search_gaceta(nombre, max_results=10)

    if not search_result.norms:
        result["message"] = "No se encontraron resultados para esta norma"
        return result

    # Check for matches
    for norm in search_result.norms:
        match_score = 0.0

        # Name similarity (basic)
        if nombre.lower() in norm.nombre.lower() or norm.nombre.lower() in nombre.lower():
            match_score += 0.5

        # Gaceta number match
        if gaceta_numero and gaceta_numero in norm.gaceta_numero:
            match_score += 0.3

        # Date match
        if gaceta_fecha and gaceta_fecha == norm.gaceta_fecha:
            match_score += 0.2

        if match_score > 0:
            result["found_matches"].append({
                "nombre": norm.nombre,
                "gaceta_numero": norm.gaceta_numero,
                "gaceta_fecha": norm.gaceta_fecha,
                "match_score": match_score,
                "url": norm.url
            })

    # Sort by match score
    result["found_matches"].sort(key=lambda x: x["match_score"], reverse=True)

    if result["found_matches"]:
        best_match = result["found_matches"][0]
        result["confidence"] = best_match["match_score"]

        if best_match["match_score"] >= 0.7:
            result["verified"] = True
            result["message"] = f"Norma verificada con alta confianza ({best_match['match_score']:.0%})"
        elif best_match["match_score"] >= 0.5:
            result["verified"] = True
            result["message"] = f"Norma encontrada con confianza media ({best_match['match_score']:.0%})"
        else:
            result["message"] = f"Posible coincidencia encontrada ({best_match['match_score']:.0%})"
    else:
        result["message"] = "No se encontraron coincidencias exactas"

    return result


def get_recent_gacetas(
    days: int = 30,
    tipo: Optional[GacetaType] = None,
    max_results: int = 20,
    use_cache: bool = True
) -> List[GacetaEntry]:
    """
    Get recent Gaceta Oficial publications.

    Args:
        days: How many days back to search
        tipo: Filter by Gaceta type
        max_results: Maximum results
        use_cache: Whether to use cache

    Returns:
        List of recent GacetaEntry
    """
    cache_key = f"recent:{days}:{tipo}"

    if use_cache:
        cached = read_cache(cache_key)
        if cached:
            return [
                GacetaEntry(
                    tipo=GacetaType(g['tipo']),
                    **{k: v for k, v in g.items() if k != 'tipo'}
                )
                for g in cached.get('gacetas', [])
            ]

    # Fetch main Gaceta page
    html_content = fetch_url(GACETA_TSJ_URL, use_cache=use_cache)
    if not html_content:
        return []

    gacetas = parse_tsj_gaceta_page(html_content)

    # Filter by type if specified
    if tipo:
        gacetas = [g for g in gacetas if g.tipo == tipo]

    # Filter by date (within specified days)
    cutoff = datetime.now() - timedelta(days=days)
    filtered_gacetas = []

    for g in gacetas:
        try:
            # Parse fecha (DD-MM-YYYY)
            if g.fecha and '-' in g.fecha:
                parts = g.fecha.split('-')
                if len(parts) == 3:
                    day, month, year = parts
                    gaceta_date = datetime(int(year), int(month), int(day))
                    if gaceta_date >= cutoff:
                        filtered_gacetas.append(g)
        except Exception:
            # Include if date parsing fails
            filtered_gacetas.append(g)

    gacetas = filtered_gacetas[:max_results]

    # Cache results
    if use_cache and gacetas:
        write_cache(cache_key, {
            'gacetas': [{**asdict(g), 'tipo': g.tipo.value} for g in gacetas]
        })

    return gacetas


def get_scraper_status() -> Dict[str, Any]:
    """Get scraper status and statistics."""
    cache_files = list(CACHE_DIR.glob("*.json")) if CACHE_DIR.exists() else []

    total_size = sum(f.stat().st_size for f in cache_files) if cache_files else 0

    return {
        "gaceta_url": GACETA_TSJ_URL,
        "cache_dir": str(CACHE_DIR),
        "cached_items": len(cache_files),
        "cache_size_kb": round(total_size / 1024, 2),
        "cache_expiry_hours": CACHE_EXPIRY_HOURS,
        "rate_limit_seconds": MIN_REQUEST_INTERVAL,
        "norm_types": [t.value for t in NormType],
        "gaceta_types": [t.value for t in GacetaType]
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def print_norm(norm: ScrapedNorm, verbose: bool = False) -> None:
    """Print norm in formatted output."""
    print(f"\n{'─' * 70}")
    print(f"  {norm.nombre}")
    print(f"{'─' * 70}")
    print(f"  Tipo:       {norm.tipo.value}")
    print(f"  Status:     {norm.status.value}")
    print(f"  Gaceta:     N° {norm.gaceta_numero} ({norm.gaceta_tipo.value})")
    print(f"  Fecha:      {norm.gaceta_fecha}")
    if norm.url:
        print(f"  URL:        {norm.url}")

    if verbose and norm.resumen:
        print(f"\n  Resumen:")
        print(f"  {norm.resumen[:400]}...")


def print_gaceta(gaceta: GacetaEntry) -> None:
    """Print Gaceta entry in formatted output."""
    print(f"\n  N° {gaceta.numero} - {gaceta.tipo.value}")
    print(f"  Fecha: {gaceta.fecha}")
    if gaceta.pdf_url:
        print(f"  PDF: {gaceta.pdf_url}")


def main():
    """CLI interface for Gaceta scraper."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Venezuela Super Lawyer - Gaceta Oficial Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 gaceta_scraper.py search "Ley Orgánica del Trabajo"
  python3 gaceta_scraper.py search "hidrocarburos" --tipo LEY_ORGANICA
  python3 gaceta_scraper.py gaceta 6.152
  python3 gaceta_scraper.py verify "CRBV" --numero 5.908
  python3 gaceta_scraper.py recent --days 30
  python3 gaceta_scraper.py status
  python3 gaceta_scraper.py clear-cache
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search Gaceta Oficial")
    search_parser.add_argument("query", help="Search terms")
    search_parser.add_argument("--tipo", choices=[t.name for t in NormType],
                               help="Filter by norm type")
    search_parser.add_argument("--max", type=int, default=10,
                               help="Maximum results (default: 10)")
    search_parser.add_argument("--no-cache", action="store_true",
                               help="Skip cache")
    search_parser.add_argument("-v", "--verbose", action="store_true",
                               help="Show full details")

    # Gaceta lookup command
    gaceta_parser = subparsers.add_parser("gaceta", help="Get Gaceta by number")
    gaceta_parser.add_argument("numero", help="Gaceta number (e.g., 6.152)")
    gaceta_parser.add_argument("--tipo", choices=[t.name for t in GacetaType],
                               help="Gaceta type")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify norm publication")
    verify_parser.add_argument("nombre", help="Norm name")
    verify_parser.add_argument("--numero", help="Expected Gaceta number")
    verify_parser.add_argument("--fecha", help="Expected date (DD-MM-YYYY)")

    # Recent command
    recent_parser = subparsers.add_parser("recent", help="Get recent Gacetas")
    recent_parser.add_argument("--days", type=int, default=30,
                               help="Days back (default: 30)")
    recent_parser.add_argument("--tipo", choices=[t.name for t in GacetaType],
                               help="Filter by type")
    recent_parser.add_argument("--max", type=int, default=20,
                               help="Maximum results")

    # Status command
    subparsers.add_parser("status", help="Show scraper status")

    # Clear cache command
    subparsers.add_parser("clear-cache", help="Clear cached data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "search":
        tipo = NormType[args.tipo] if args.tipo else None
        result = search_gaceta(
            args.query,
            tipo_norm=tipo,
            max_results=args.max,
            use_cache=not args.no_cache
        )

        print(f"\n{'═' * 70}")
        print(f"GACETA OFICIAL SEARCH RESULTS")
        print(f"{'═' * 70}")
        print(f"Query: {result.query}")
        if result.tipo_norm:
            print(f"Type: {result.tipo_norm.value}")
        print(f"Results: {result.total_results}")
        print(f"Time: {result.search_time:.2f}s {'(cached)' if result.cached else ''}")

        if result.norms:
            print(f"\n  NORMAS ENCONTRADAS:")
            for norm in result.norms:
                print_norm(norm, verbose=args.verbose)

        if result.gacetas:
            print(f"\n  GACETAS RELACIONADAS:")
            for gaceta in result.gacetas[:5]:
                print_gaceta(gaceta)

    elif args.command == "gaceta":
        tipo = GacetaType[args.tipo] if args.tipo else None
        gaceta = get_gaceta_by_number(args.numero, tipo)

        if gaceta:
            print(f"\n{'═' * 70}")
            print(f"GACETA OFICIAL")
            print(f"{'═' * 70}")
            print_gaceta(gaceta)
            if gaceta.contenido:
                print(f"\n  Contenido:")
                for item in gaceta.contenido[:10]:
                    print(f"    - {item}")
        else:
            print(f"\n✗ Gaceta N° {args.numero} not found")

    elif args.command == "verify":
        result = verify_norm_publication(
            args.nombre,
            gaceta_numero=args.numero,
            gaceta_fecha=args.fecha
        )

        print(f"\n{'═' * 70}")
        print(f"VERIFICATION RESULT")
        print(f"{'═' * 70}")
        print(f"  Norm: {result['nombre']}")
        print(f"  Verified: {'✓ YES' if result['verified'] else '✗ NO'}")
        print(f"  Confidence: {result['confidence']:.0%}")
        print(f"  Message: {result['message']}")

        if result['found_matches']:
            print(f"\n  MATCHES FOUND:")
            for match in result['found_matches'][:3]:
                print(f"\n    - {match['nombre']}")
                print(f"      Gaceta: N° {match['gaceta_numero']}")
                print(f"      Score: {match['match_score']:.0%}")

    elif args.command == "recent":
        tipo = GacetaType[args.tipo] if args.tipo else None
        gacetas = get_recent_gacetas(days=args.days, tipo=tipo, max_results=args.max)

        print(f"\n{'═' * 70}")
        print(f"RECENT GACETAS ({args.days} days)")
        print(f"{'═' * 70}")
        print(f"Found: {len(gacetas)} gacetas")

        for gaceta in gacetas:
            print_gaceta(gaceta)

    elif args.command == "status":
        status = get_scraper_status()
        print(f"\n{'═' * 70}")
        print("GACETA SCRAPER STATUS")
        print(f"{'═' * 70}")
        for key, value in status.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value[:5]:
                    print(f"    - {item}")
                if len(value) > 5:
                    print(f"    ... and {len(value) - 5} more")
            else:
                print(f"  {key}: {value}")

    elif args.command == "clear-cache":
        count = clear_cache()
        print(f"✓ Cleared {count} cached items")


if __name__ == "__main__":
    main()
