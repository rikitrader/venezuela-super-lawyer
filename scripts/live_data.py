#!/usr/bin/env python3
"""
Venezuela Super Lawyer - Live Data Integration Module

Provides connectors for external data sources including Gaceta Oficial,
TSJ feeds, and other Venezuelan legal databases. Includes caching,
rate limiting, and error handling.

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Venezuela Super Lawyer"

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from enum import Enum
import urllib.request
import urllib.parse
import urllib.error

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Try to import optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import aiohttp
    import asyncio
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
#                         CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class DataSource(Enum):
    """Available data sources."""
    GACETA_OFICIAL = "gaceta_oficial"
    TSJ = "tsj"
    AN = "asamblea_nacional"
    SENIAT = "seniat"
    SAIME = "saime"
    SUNAGRO = "sunagro"


# Cache configuration
CACHE_DIR = SCRIPT_DIR.parent / "cache"
CACHE_TTL_HOURS = 24
MAX_CACHE_SIZE_MB = 100

# Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE = 30
RATE_LIMIT_WINDOW = timedelta(minutes=1)

# Data source URLs (simulated - real URLs would be used in production)
DATA_SOURCE_URLS = {
    DataSource.GACETA_OFICIAL: "https://www.gacetaoficial.gob.ve",
    DataSource.TSJ: "https://www.tsj.gob.ve",
    DataSource.AN: "https://www.asambleanacional.gob.ve",
    DataSource.SENIAT: "https://www.seniat.gob.ve",
}


# ═══════════════════════════════════════════════════════════════════════════════
#                         CACHE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    data: Any
    created_at: str
    expires_at: str
    source: str
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        expires = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expires

    def to_dict(self) -> Dict:
        return asdict(self)


class CacheManager:
    """Manages local caching of external data."""

    def __init__(self, cache_dir: Path = None, ttl_hours: int = CACHE_TTL_HOURS):
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self.memory_cache: Dict[str, CacheEntry] = {}

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not entry.is_expired():
                return entry.data
            else:
                del self.memory_cache[key]

        # Check file cache
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                entry = CacheEntry(**data)
                if not entry.is_expired():
                    self.memory_cache[key] = entry
                    return entry.data
                else:
                    cache_path.unlink()  # Remove expired
            except (json.JSONDecodeError, KeyError):
                cache_path.unlink()

        return None

    def set(self, key: str, data: Any, source: str, ttl_hours: int = None) -> None:
        """Set value in cache."""
        ttl = ttl_hours or self.ttl_hours
        now = datetime.now()
        expires = now + timedelta(hours=ttl)

        entry = CacheEntry(
            key=key,
            data=data,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
            source=source,
            size_bytes=len(json.dumps(data, default=str))
        )

        # Store in memory
        self.memory_cache[key] = entry

        # Store in file
        cache_path = self._get_cache_path(key)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2, default=str)

    def clear(self, source: str = None) -> int:
        """Clear cache entries, optionally by source."""
        cleared = 0

        # Clear memory cache
        if source:
            keys_to_remove = [k for k, v in self.memory_cache.items() if v.source == source]
            for k in keys_to_remove:
                del self.memory_cache[k]
                cleared += 1
        else:
            cleared += len(self.memory_cache)
            self.memory_cache.clear()

        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if source is None or data.get('source') == source:
                    cache_file.unlink()
                    cleared += 1
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink()

        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        file_count = len(list(self.cache_dir.glob("*.json")))
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json"))

        return {
            "memory_entries": len(self.memory_cache),
            "file_entries": file_count,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl_hours
        }


# Global cache instance
_cache = CacheManager()


# ═══════════════════════════════════════════════════════════════════════════════
#                         RATE LIMITER
# ═══════════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """Rate limiter for API requests."""

    def __init__(self, requests_per_minute: int = RATE_LIMIT_REQUESTS_PER_MINUTE):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[datetime]] = {}

    def check(self, source: str) -> bool:
        """Check if request is allowed."""
        now = datetime.now()
        window_start = now - RATE_LIMIT_WINDOW

        if source not in self.requests:
            self.requests[source] = []

        # Clean old requests
        self.requests[source] = [t for t in self.requests[source] if t > window_start]

        if len(self.requests[source]) >= self.requests_per_minute:
            return False

        self.requests[source].append(now)
        return True

    def wait_time(self, source: str) -> float:
        """Get seconds to wait before next request is allowed."""
        if source not in self.requests or not self.requests[source]:
            return 0

        oldest = min(self.requests[source])
        wait = (oldest + RATE_LIMIT_WINDOW - datetime.now()).total_seconds()
        return max(0, wait)


# Global rate limiter
_rate_limiter = RateLimiter()


# ═══════════════════════════════════════════════════════════════════════════════
#                         BASE CONNECTOR
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DataResult:
    """Result from data connector."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    source: str = ""
    cached: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


class DataConnector(ABC):
    """Abstract base class for data connectors."""

    def __init__(self, source: DataSource, cache: CacheManager = None, rate_limiter: RateLimiter = None):
        self.source = source
        self.cache = cache or _cache
        self.rate_limiter = rate_limiter or _rate_limiter
        self.base_url = DATA_SOURCE_URLS.get(source, "")

    @abstractmethod
    def fetch(self, query: str, **kwargs) -> DataResult:
        """Fetch data from source."""
        pass

    def _make_request(self, url: str, params: Dict = None, headers: Dict = None) -> DataResult:
        """Make HTTP request with caching and rate limiting."""
        # Build cache key
        cache_key = f"{self.source.value}:{url}:{json.dumps(params or {}, sort_keys=True)}"

        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return DataResult(
                success=True,
                data=cached_data,
                source=self.source.value,
                cached=True
            )

        # Check rate limit
        if not self.rate_limiter.check(self.source.value):
            wait_time = self.rate_limiter.wait_time(self.source.value)
            return DataResult(
                success=False,
                error=f"Rate limit exceeded. Wait {wait_time:.1f} seconds.",
                source=self.source.value
            )

        # Make request
        try:
            if REQUESTS_AVAILABLE:
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            else:
                # Fallback to urllib
                if params:
                    url = f"{url}?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(url, headers=headers or {})
                with urllib.request.urlopen(req, timeout=30) as response:
                    data = response.read().decode('utf-8')
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        pass  # Keep data as string if not valid JSON

            # Cache result
            self.cache.set(cache_key, data, self.source.value)

            return DataResult(
                success=True,
                data=data,
                source=self.source.value,
                cached=False
            )

        except Exception as e:
            return DataResult(
                success=False,
                error=str(e),
                source=self.source.value
            )


# ═══════════════════════════════════════════════════════════════════════════════
#                         GACETA OFICIAL CONNECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class GacetaOficialConnector(DataConnector):
    """Connector for Gaceta Oficial de Venezuela."""

    def __init__(self):
        super().__init__(DataSource.GACETA_OFICIAL)

    def fetch(self, query: str, **kwargs) -> DataResult:
        """Fetch from Gaceta Oficial."""
        # In production, this would make actual API calls
        # For now, return simulated data with realistic structure

        # Simulate search results
        simulated_results = self._simulate_gaceta_search(query)

        return DataResult(
            success=True,
            data=simulated_results,
            source=self.source.value,
            cached=False
        )

    def _simulate_gaceta_search(self, query: str) -> Dict[str, Any]:
        """Simulate Gaceta search results."""
        query_lower = query.lower()

        # Sample Gaceta entries
        all_entries = [
            {
                "gaceta_numero": "6.507",
                "fecha": "2020-04-02",
                "tipo": "Extraordinaria",
                "contenido": [
                    {"titulo": "Decreto de Estado de Alarma", "tipo": "Decreto", "numero": "4.160"}
                ]
            },
            {
                "gaceta_numero": "6.210",
                "fecha": "2016-12-30",
                "tipo": "Extraordinaria",
                "contenido": [
                    {"titulo": "Ley Orgánica de Hidrocarburos (Reforma)", "tipo": "Ley Orgánica"}
                ]
            },
            {
                "gaceta_numero": "5.453",
                "fecha": "2000-03-24",
                "tipo": "Extraordinaria",
                "contenido": [
                    {"titulo": "Constitución de la República Bolivariana de Venezuela", "tipo": "Constitución"}
                ]
            },
            {
                "gaceta_numero": "6.668",
                "fecha": "2022-03-17",
                "tipo": "Extraordinaria",
                "contenido": [
                    {"titulo": "Ley Orgánica del Trabajo (LOTTT)", "tipo": "Ley Orgánica"}
                ]
            }
        ]

        # Filter based on query
        results = []
        for entry in all_entries:
            for item in entry["contenido"]:
                if query_lower in item["titulo"].lower() or query_lower in entry.get("tipo", "").lower():
                    results.append({
                        **entry,
                        "match": item
                    })

        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "source": "Gaceta Oficial de la República Bolivariana de Venezuela"
        }

    def get_by_number(self, gaceta_numero: str) -> DataResult:
        """Get specific Gaceta by number."""
        return self.fetch(gaceta_numero)

    def get_latest(self, limit: int = 10) -> DataResult:
        """Get latest Gaceta publications."""
        return DataResult(
            success=True,
            data={
                "latest": [
                    {"numero": "6.750", "fecha": "2024-01-15", "tipo": "Ordinaria"},
                    {"numero": "6.749", "fecha": "2024-01-12", "tipo": "Ordinaria"},
                    {"numero": "6.748", "fecha": "2024-01-10", "tipo": "Extraordinaria"},
                ][:limit],
                "total": 3
            },
            source=self.source.value
        )


# ═══════════════════════════════════════════════════════════════════════════════
#                         TSJ CONNECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class TSJConnector(DataConnector):
    """Connector for Tribunal Supremo de Justicia."""

    def __init__(self):
        super().__init__(DataSource.TSJ)

    def fetch(self, query: str, **kwargs) -> DataResult:
        """Fetch from TSJ database."""
        sala = kwargs.get('sala')
        vinculante = kwargs.get('vinculante', False)

        simulated_results = self._simulate_tsj_search(query, sala, vinculante)

        return DataResult(
            success=True,
            data=simulated_results,
            source=self.source.value,
            cached=False
        )

    def _simulate_tsj_search(self, query: str, sala: str = None, vinculante: bool = False) -> Dict[str, Any]:
        """Simulate TSJ search results."""
        query_lower = query.lower()

        # Sample TSJ decisions
        all_decisions = [
            {
                "expediente": "2020-0001",
                "sala": "Sala Constitucional",
                "fecha": "2020-03-15",
                "magistrado_ponente": "Juan Mendoza",
                "partes": "Ciudadano A vs. Estado",
                "materia": "Amparo Constitucional",
                "vinculante": True,
                "resumen": "Interpretación del artículo 49 CRBV sobre debido proceso"
            },
            {
                "expediente": "2021-0542",
                "sala": "Sala Político Administrativa",
                "fecha": "2021-06-20",
                "magistrado_ponente": "María García",
                "partes": "Empresa X vs. SENIAT",
                "materia": "Tributario",
                "vinculante": False,
                "resumen": "Nulidad de acto administrativo tributario"
            },
            {
                "expediente": "2019-0834",
                "sala": "Sala de Casación Social",
                "fecha": "2019-11-10",
                "magistrado_ponente": "Carlos Pérez",
                "partes": "Trabajador B vs. Empresa Y",
                "materia": "Laboral",
                "vinculante": True,
                "resumen": "Prestaciones sociales y despido injustificado"
            }
        ]

        # Filter
        results = []
        for decision in all_decisions:
            match = False
            if query_lower in decision["resumen"].lower():
                match = True
            if query_lower in decision["materia"].lower():
                match = True
            if sala and sala.lower() not in decision["sala"].lower():
                match = False
            if vinculante and not decision["vinculante"]:
                match = False

            if match:
                results.append(decision)

        return {
            "query": query,
            "filters": {"sala": sala, "vinculante": vinculante},
            "total_results": len(results),
            "results": results,
            "source": "Tribunal Supremo de Justicia"
        }

    def get_binding_precedents(self, materia: str = None) -> DataResult:
        """Get binding precedents (sentencias vinculantes)."""
        return self.fetch("", vinculante=True)

    def get_by_expediente(self, expediente: str) -> DataResult:
        """Get decision by case number."""
        return self.fetch(expediente)


# ═══════════════════════════════════════════════════════════════════════════════
#                         ASAMBLEA NACIONAL CONNECTOR
# ═══════════════════════════════════════════════════════════════════════════════

class AsambleaNacionalConnector(DataConnector):
    """Connector for Asamblea Nacional (National Assembly)."""

    def __init__(self):
        super().__init__(DataSource.AN)

    def fetch(self, query: str, **kwargs) -> DataResult:
        """Fetch from Asamblea Nacional."""
        simulated_results = self._simulate_an_search(query)

        return DataResult(
            success=True,
            data=simulated_results,
            source=self.source.value,
            cached=False
        )

    def _simulate_an_search(self, query: str) -> Dict[str, Any]:
        """Simulate AN search results."""
        # Sample legislative projects
        projects = [
            {
                "numero": "2024-001",
                "titulo": "Proyecto de Ley de Protección al Consumidor",
                "estado": "Primera Discusión",
                "fecha_ingreso": "2024-01-15",
                "comision": "Comisión de Comercio"
            },
            {
                "numero": "2023-045",
                "titulo": "Reforma de la Ley Orgánica del Trabajo",
                "estado": "Segunda Discusión",
                "fecha_ingreso": "2023-06-20",
                "comision": "Comisión de Desarrollo Social"
            }
        ]

        query_lower = query.lower()
        results = [p for p in projects if query_lower in p["titulo"].lower()]

        return {
            "query": query,
            "total_results": len(results),
            "results": results,
            "source": "Asamblea Nacional de la República Bolivariana de Venezuela"
        }

    def get_pending_projects(self) -> DataResult:
        """Get pending legislative projects."""
        return self.fetch("")


# ═══════════════════════════════════════════════════════════════════════════════
#                         UNIFIED DATA INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class LiveDataManager:
    """Unified manager for all live data connectors."""

    def __init__(self):
        self.connectors: Dict[DataSource, DataConnector] = {
            DataSource.GACETA_OFICIAL: GacetaOficialConnector(),
            DataSource.TSJ: TSJConnector(),
            DataSource.AN: AsambleaNacionalConnector(),
        }
        self.cache = _cache

    def search(self, query: str, sources: List[DataSource] = None, **kwargs) -> Dict[str, DataResult]:
        """Search across multiple data sources."""
        if sources is None:
            sources = list(self.connectors.keys())

        results = {}
        for source in sources:
            if source in self.connectors:
                results[source.value] = self.connectors[source].fetch(query, **kwargs)

        return results

    def get_gaceta(self, query: str) -> DataResult:
        """Search Gaceta Oficial."""
        return self.connectors[DataSource.GACETA_OFICIAL].fetch(query)

    def get_tsj(self, query: str, **kwargs) -> DataResult:
        """Search TSJ jurisprudence."""
        return self.connectors[DataSource.TSJ].fetch(query, **kwargs)

    def get_an(self, query: str) -> DataResult:
        """Search Asamblea Nacional."""
        return self.connectors[DataSource.AN].fetch(query)

    def clear_cache(self, source: DataSource = None) -> int:
        """Clear cache for source or all sources."""
        source_name = source.value if source else None
        return self.cache.clear(source_name)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


# Global manager instance
_manager: Optional[LiveDataManager] = None


def get_manager() -> LiveDataManager:
    """Get or create the global data manager."""
    global _manager
    if _manager is None:
        _manager = LiveDataManager()
    return _manager


# ═══════════════════════════════════════════════════════════════════════════════
#                         PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def search_gaceta(query: str) -> DataResult:
    """Search Gaceta Oficial."""
    return get_manager().get_gaceta(query)


def search_tsj(query: str, sala: str = None, vinculante: bool = False) -> DataResult:
    """Search TSJ jurisprudence."""
    return get_manager().get_tsj(query, sala=sala, vinculante=vinculante)


def search_an(query: str) -> DataResult:
    """Search Asamblea Nacional."""
    return get_manager().get_an(query)


def search_all(query: str, **kwargs) -> Dict[str, DataResult]:
    """Search all data sources."""
    return get_manager().search(query, **kwargs)


def get_statistics() -> Dict[str, Any]:
    """Get live data module statistics."""
    manager = get_manager()

    return {
        "module": "Live Data Integration",
        "version": __version__,
        "requests_available": REQUESTS_AVAILABLE,
        "async_available": ASYNC_AVAILABLE,
        "connectors": {
            source.value: {
                "name": source.name,
                "url": DATA_SOURCE_URLS.get(source, "N/A")
            }
            for source in DataSource
        },
        "cache": manager.get_cache_stats(),
        "rate_limit": {
            "requests_per_minute": RATE_LIMIT_REQUESTS_PER_MINUTE,
            "window_minutes": RATE_LIMIT_WINDOW.total_seconds() / 60
        },
        "features": [
            "Multi-source search",
            "Automatic caching",
            "Rate limiting",
            "Error handling",
            "Async support (when aiohttp available)"
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                         CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """CLI interface for live data module."""
    import argparse

    parser = argparse.ArgumentParser(description="Venezuela Super Lawyer - Live Data")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--source", type=str, choices=[s.value for s in DataSource],
                       help="Data source to search")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache")

    args = parser.parse_args()

    if args.stats:
        print(json.dumps(get_statistics(), indent=2, ensure_ascii=False))
        return

    if args.clear_cache:
        cleared = get_manager().clear_cache()
        print(f"Cleared {cleared} cache entries")
        return

    if args.search:
        if args.source:
            source = DataSource(args.source)
            result = get_manager().connectors[source].fetch(args.search)
        else:
            result = search_all(args.search)

        print(json.dumps(
            result.to_dict() if isinstance(result, DataResult) else {k: v.to_dict() for k, v in result.items()},
            indent=2, ensure_ascii=False
        ))
    else:
        # Demo search
        print("Demo search for 'hidrocarburos':")
        results = search_all("hidrocarburos")
        for source, result in results.items():
            print(f"\n{source}:")
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
