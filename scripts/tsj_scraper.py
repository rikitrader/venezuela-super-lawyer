#!/usr/bin/env python3
"""
Venezuela Super Lawyer - TSJ Web Scraper Module
Scrapes the Tribunal Supremo de Justicia website for live jurisprudence.

TSJ Website: http://historico.tsj.gob.ve/decisiones/

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
import time
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum
from urllib.parse import urljoin, quote_plus
import html

# ═══════════════════════════════════════════════════════════════════════════════
#                         CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Base URLs for TSJ
TSJ_BASE_URL = "http://historico.tsj.gob.ve"
TSJ_SEARCH_URL = f"{TSJ_BASE_URL}/decisiones/scon/busconam.asp"
TSJ_DECISION_BASE = f"{TSJ_BASE_URL}/decisiones"

# Sala codes used in TSJ URLs
SALA_CODES = {
    "CONSTITUCIONAL": "scon",
    "POLITICO_ADMINISTRATIVA": "spa",
    "CASACION_CIVIL": "scc",
    "CASACION_PENAL": "scp",
    "CASACION_SOCIAL": "scs",
    "ELECTORAL": "selec",
    "PLENA": "sp"
}

# Rate limiting
MIN_REQUEST_INTERVAL = 2.0  # Minimum seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # Seconds to wait before retry

# Cache configuration
CACHE_DIR = Path(__file__).parent.parent / "cache" / "tsj"
CACHE_EXPIRY_HOURS = 24

# ═══════════════════════════════════════════════════════════════════════════════
#                         DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class SalaTSJ(Enum):
    """TSJ Chamber enumeration."""
    CONSTITUCIONAL = "Sala Constitucional"
    POLITICO_ADMINISTRATIVA = "Sala Político-Administrativa"
    CASACION_CIVIL = "Sala de Casación Civil"
    CASACION_PENAL = "Sala de Casación Penal"
    CASACION_SOCIAL = "Sala de Casación Social"
    ELECTORAL = "Sala Electoral"
    PLENA = "Sala Plena"


@dataclass
class ScrapedDecision:
    """Represents a decision scraped from TSJ website."""
    numero: str
    fecha: str
    sala: SalaTSJ
    expediente: str
    ponente: str
    partes: str
    materia: str
    resumen: str
    url: str
    texto_completo: Optional[str] = None
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()


@dataclass
class SearchResult:
    """Search results container."""
    query: str
    sala: Optional[SalaTSJ]
    fecha_desde: Optional[str]
    fecha_hasta: Optional[str]
    total_results: int
    decisions: List[ScrapedDecision]
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
        except (OSError, json.JSONDecodeError):
            pass  # Cache miss or corrupted, will fetch fresh
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
            except OSError:
                pass  # File in use or permission denied, skip
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

def fetch_url(url: str, use_cache: bool = True) -> Optional[str]:
    """
    Fetch URL content with rate limiting, caching, and retry logic.

    Args:
        url: URL to fetch
        use_cache: Whether to use cached response if available

    Returns:
        Response text or None if failed
    """
    # Check cache first
    if use_cache:
        cached = read_cache(url)
        if cached:
            return cached.get('content')

    # Import here to handle missing dependency gracefully
    try:
        import urllib.request
        import urllib.error
    except ImportError:
        print("ERROR: urllib not available", file=sys.stderr)
        return None

    for attempt in range(MAX_RETRIES):
        try:
            _rate_limiter.wait()

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

            with urllib.request.urlopen(request, timeout=30) as response:
                # Try different encodings
                content = response.read()
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
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


def extract_text_between(content: str, start: str, end: str) -> Optional[str]:
    """Extract text between two markers."""
    try:
        start_idx = content.find(start)
        if start_idx == -1:
            return None
        start_idx += len(start)
        end_idx = content.find(end, start_idx)
        if end_idx == -1:
            return None
        return content[start_idx:end_idx]
    except Exception:
        return None


def parse_search_results(html_content: str, sala: SalaTSJ) -> List[ScrapedDecision]:
    """
    Parse TSJ search results page.

    Note: This is a basic parser. TSJ's HTML structure may vary.
    """
    decisions = []

    # Pattern to find decision links
    # TSJ URLs typically look like: /decisiones/scon/marzo/123-010312-12-0001.HTML
    link_pattern = re.compile(
        r'href=["\']([^"\']*?/decisiones/[^"\']+\.html?)["\']',
        re.IGNORECASE
    )

    # Find all decision links
    links = link_pattern.findall(html_content)

    for link in links:
        # Build full URL
        if link.startswith('/'):
            full_url = urljoin(TSJ_BASE_URL, link)
        else:
            full_url = link

        # Extract decision number from URL
        # Example: 123-010312-12-0001.HTML
        filename = link.split('/')[-1]
        numero_match = re.match(r'(\d+)', filename)
        numero = numero_match.group(1) if numero_match else filename

        # Extract date from path if possible
        # Example: /decisiones/scon/marzo/...
        fecha = ""
        month_match = re.search(r'/(\w+)/[^/]+\.html?$', link, re.IGNORECASE)
        if month_match:
            month_name = month_match.group(1).lower()
            # Spanish months
            months = {
                'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
            }
            if month_name in months:
                fecha = f"??-{months[month_name]}-????"

        decision = ScrapedDecision(
            numero=numero,
            fecha=fecha,
            sala=sala,
            expediente="",
            ponente="",
            partes="",
            materia="",
            resumen="",
            url=full_url
        )
        decisions.append(decision)

    return decisions


def parse_decision_page(html_content: str, decision: ScrapedDecision) -> ScrapedDecision:
    """
    Parse a single decision page to extract full details.

    Updates the decision object with extracted information.
    """
    # Extract expediente
    exp_match = re.search(r'Expediente[:\s]+([^\s<]+)', html_content, re.IGNORECASE)
    if exp_match:
        decision.expediente = clean_html_text(exp_match.group(1))

    # Extract ponente
    ponente_match = re.search(
        r'Ponente[:\s]+([^<]+?)(?:<|$)',
        html_content,
        re.IGNORECASE
    )
    if ponente_match:
        decision.ponente = clean_html_text(ponente_match.group(1))

    # Extract fecha if not already set
    if not decision.fecha or '?' in decision.fecha:
        fecha_match = re.search(
            r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
            html_content,
            re.IGNORECASE
        )
        if fecha_match:
            day, month_name, year = fecha_match.groups()
            months = {
                'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
            }
            month = months.get(month_name.lower(), '00')
            decision.fecha = f"{day.zfill(2)}-{month}-{year}"

    # Extract partes (parties involved)
    partes_match = re.search(
        r'(?:Partes|Recurrente|Demandante)[:\s]+([^<]+)',
        html_content,
        re.IGNORECASE
    )
    if partes_match:
        decision.partes = clean_html_text(partes_match.group(1))[:500]

    # Extract materia (subject matter)
    materia_match = re.search(
        r'(?:Materia|Asunto)[:\s]+([^<]+)',
        html_content,
        re.IGNORECASE
    )
    if materia_match:
        decision.materia = clean_html_text(materia_match.group(1))[:200]

    # Extract full text (main content)
    # Look for common content containers
    for pattern in [
        r'<div[^>]*class=["\']?texto["\']?[^>]*>(.*?)</div>',
        r'<td[^>]*class=["\']?contenido["\']?[^>]*>(.*?)</td>',
        r'<body[^>]*>(.*?)</body>'
    ]:
        content_match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if content_match:
            full_text = clean_html_text(content_match.group(1))
            if len(full_text) > 100:
                decision.texto_completo = full_text
                # Create summary from first 500 chars
                decision.resumen = full_text[:500] + "..." if len(full_text) > 500 else full_text
                break

    return decision


# ═══════════════════════════════════════════════════════════════════════════════
#                         PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def search_tsj(
    query: str,
    sala: Optional[SalaTSJ] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    max_results: int = 20,
    use_cache: bool = True
) -> SearchResult:
    """
    Search TSJ jurisprudence.

    Args:
        query: Search terms
        sala: Specific chamber to search (None for all)
        fecha_desde: Start date (DD-MM-YYYY)
        fecha_hasta: End date (DD-MM-YYYY)
        max_results: Maximum results to return
        use_cache: Whether to use cached results

    Returns:
        SearchResult object with decisions
    """
    start_time = time.time()

    # Build cache key
    cache_key = f"search:{query}:{sala}:{fecha_desde}:{fecha_hasta}"

    # Check cache
    if use_cache:
        cached = read_cache(cache_key)
        if cached:
            decisions = [
                ScrapedDecision(
                    sala=SalaTSJ(d['sala']),
                    **{k: v for k, v in d.items() if k != 'sala'}
                )
                for d in cached.get('decisions', [])
            ]
            return SearchResult(
                query=query,
                sala=sala,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                total_results=len(decisions),
                decisions=decisions[:max_results],
                search_time=0.0,
                cached=True
            )

    all_decisions = []

    # Determine which salas to search
    salas_to_search = [sala] if sala else list(SalaTSJ)

    for s in salas_to_search:
        sala_code = SALA_CODES.get(s.name, "scon")

        # Build search URL
        # TSJ uses ASP-based search forms
        search_params = quote_plus(query)
        search_url = f"{TSJ_BASE_URL}/decisiones/{sala_code}/busconft.asp?palabra={search_params}"

        # Fetch search results
        html_content = fetch_url(search_url, use_cache=use_cache)
        if html_content:
            decisions = parse_search_results(html_content, s)
            all_decisions.extend(decisions)

        if len(all_decisions) >= max_results:
            break

    # Limit results
    all_decisions = all_decisions[:max_results]

    # Cache results
    if use_cache and all_decisions:
        write_cache(cache_key, {
            'decisions': [
                {**asdict(d), 'sala': d.sala.value}
                for d in all_decisions
            ]
        })

    elapsed = time.time() - start_time

    return SearchResult(
        query=query,
        sala=sala,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total_results=len(all_decisions),
        decisions=all_decisions,
        search_time=elapsed,
        cached=False
    )


def get_decision_details(decision: ScrapedDecision, use_cache: bool = True) -> ScrapedDecision:
    """
    Fetch and parse full decision details.

    Args:
        decision: Decision with URL to fetch
        use_cache: Whether to use cached content

    Returns:
        Updated decision with full details
    """
    if not decision.url:
        return decision

    html_content = fetch_url(decision.url, use_cache=use_cache)
    if html_content:
        return parse_decision_page(html_content, decision)

    return decision


def get_recent_decisions(
    sala: SalaTSJ,
    days: int = 30,
    max_results: int = 10,
    use_cache: bool = True
) -> List[ScrapedDecision]:
    """
    Get recent decisions from a specific chamber.

    Args:
        sala: TSJ chamber
        days: How many days back to search
        max_results: Maximum results
        use_cache: Whether to use cache

    Returns:
        List of recent decisions
    """
    sala_code = SALA_CODES.get(sala.name, "scon")

    # TSJ organizes decisions by year and month
    now = datetime.now()
    months_spanish = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]

    decisions = []

    # Check current and previous month
    for offset in range(2):
        check_date = now - timedelta(days=offset * 30)
        month_name = months_spanish[check_date.month - 1]
        year = check_date.year

        # Build URL for month listing
        listing_url = f"{TSJ_BASE_URL}/decisiones/{sala_code}/{month_name}/"

        html_content = fetch_url(listing_url, use_cache=use_cache)
        if html_content:
            month_decisions = parse_search_results(html_content, sala)
            decisions.extend(month_decisions)

        if len(decisions) >= max_results:
            break

    return decisions[:max_results]


def verify_decision_exists(
    numero: str,
    sala: SalaTSJ,
    year: Optional[int] = None
) -> Optional[ScrapedDecision]:
    """
    Verify if a specific decision exists in TSJ.

    Args:
        numero: Decision number
        sala: TSJ chamber
        year: Year of decision (optional, improves search)

    Returns:
        Decision if found, None otherwise
    """
    query = f"sentencia {numero}"
    if year:
        query += f" {year}"

    result = search_tsj(query, sala=sala, max_results=5)

    for decision in result.decisions:
        if numero in decision.numero:
            return get_decision_details(decision)

    return None


def get_scraper_status() -> Dict[str, Any]:
    """Get scraper status and statistics."""
    cache_files = list(CACHE_DIR.glob("*.json")) if CACHE_DIR.exists() else []

    total_size = sum(f.stat().st_size for f in cache_files) if cache_files else 0

    return {
        "tsj_base_url": TSJ_BASE_URL,
        "cache_dir": str(CACHE_DIR),
        "cached_items": len(cache_files),
        "cache_size_kb": round(total_size / 1024, 2),
        "cache_expiry_hours": CACHE_EXPIRY_HOURS,
        "rate_limit_seconds": MIN_REQUEST_INTERVAL,
        "available_salas": [s.value for s in SalaTSJ],
        "sala_codes": SALA_CODES
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def print_decision(decision: ScrapedDecision, verbose: bool = False) -> None:
    """Print decision in formatted output."""
    print(f"\n{'═' * 70}")
    print(f"Decisión No. {decision.numero}")
    print(f"{'═' * 70}")
    print(f"  Sala:       {decision.sala.value}")
    print(f"  Fecha:      {decision.fecha}")
    print(f"  Expediente: {decision.expediente or 'N/A'}")
    print(f"  Ponente:    {decision.ponente or 'N/A'}")
    print(f"  Materia:    {decision.materia or 'N/A'}")
    print(f"  URL:        {decision.url}")

    if decision.partes:
        print(f"  Partes:     {decision.partes[:100]}...")

    if verbose and decision.resumen:
        print(f"\n  Resumen:")
        print(f"  {decision.resumen[:500]}...")


def main():
    """CLI interface for TSJ scraper."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Venezuela Super Lawyer - TSJ Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tsj_scraper.py search "control constitucional"
  python3 tsj_scraper.py search "amparo" --sala CONSTITUCIONAL
  python3 tsj_scraper.py recent CONSTITUCIONAL
  python3 tsj_scraper.py verify 123 CONSTITUCIONAL --year 2023
  python3 tsj_scraper.py status
  python3 tsj_scraper.py clear-cache
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search TSJ jurisprudence")
    search_parser.add_argument("query", help="Search terms")
    search_parser.add_argument("--sala", choices=[s.name for s in SalaTSJ],
                               help="Filter by chamber")
    search_parser.add_argument("--max", type=int, default=10,
                               help="Maximum results (default: 10)")
    search_parser.add_argument("--no-cache", action="store_true",
                               help="Skip cache")
    search_parser.add_argument("-v", "--verbose", action="store_true",
                               help="Show full details")

    # Recent command
    recent_parser = subparsers.add_parser("recent", help="Get recent decisions")
    recent_parser.add_argument("sala", choices=[s.name for s in SalaTSJ],
                               help="Chamber to search")
    recent_parser.add_argument("--days", type=int, default=30,
                               help="Days back (default: 30)")
    recent_parser.add_argument("--max", type=int, default=10,
                               help="Maximum results")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify decision exists")
    verify_parser.add_argument("numero", help="Decision number")
    verify_parser.add_argument("sala", choices=[s.name for s in SalaTSJ],
                               help="Chamber")
    verify_parser.add_argument("--year", type=int, help="Year of decision")

    # Status command
    subparsers.add_parser("status", help="Show scraper status")

    # Clear cache command
    subparsers.add_parser("clear-cache", help="Clear cached data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "search":
        sala = SalaTSJ[args.sala] if args.sala else None
        result = search_tsj(
            args.query,
            sala=sala,
            max_results=args.max,
            use_cache=not args.no_cache
        )

        print(f"\n{'═' * 70}")
        print(f"TSJ SEARCH RESULTS")
        print(f"{'═' * 70}")
        print(f"Query: {result.query}")
        if result.sala:
            print(f"Sala: {result.sala.value}")
        print(f"Results: {result.total_results}")
        print(f"Time: {result.search_time:.2f}s {'(cached)' if result.cached else ''}")

        for decision in result.decisions:
            if args.verbose:
                decision = get_decision_details(decision)
            print_decision(decision, verbose=args.verbose)

    elif args.command == "recent":
        sala = SalaTSJ[args.sala]
        decisions = get_recent_decisions(sala, days=args.days, max_results=args.max)

        print(f"\n{'═' * 70}")
        print(f"RECENT DECISIONS - {sala.value}")
        print(f"{'═' * 70}")
        print(f"Found: {len(decisions)} decisions")

        for decision in decisions:
            print_decision(decision)

    elif args.command == "verify":
        sala = SalaTSJ[args.sala]
        decision = verify_decision_exists(args.numero, sala, args.year)

        if decision:
            print(f"\n✓ Decision found:")
            print_decision(decision, verbose=True)
        else:
            print(f"\n✗ Decision {args.numero} not found in {sala.value}")

    elif args.command == "status":
        status = get_scraper_status()
        print(f"\n{'═' * 70}")
        print("TSJ SCRAPER STATUS")
        print(f"{'═' * 70}")
        for key, value in status.items():
            if isinstance(value, list):
                print(f"  {key}:")
                for item in value:
                    print(f"    - {item}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")

    elif args.command == "clear-cache":
        count = clear_cache()
        print(f"✓ Cleared {count} cached items")


if __name__ == "__main__":
    main()
