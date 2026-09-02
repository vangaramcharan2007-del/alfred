"""
Public API Capability Registry for Jarvis X.
Contains a curated catalog of public and open APIs categorized by domain:
Weather, Geocoding, Finance & Currency, News & Tech, Science & Reference, Crypto, Government.

Rich Metadata per API:
- Name, Category, Description
- Endpoint URL & HTTP Method
- Auth requirement (None, apiKey, OAuth)
- HTTPS support, CORS status
- Param template & response parser
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class AuthType(str, Enum):
    NO_AUTH = "No"
    API_KEY = "apiKey"
    OAUTH = "OAuth"


@dataclass
class APIEndpointSpec:
    api_id: str
    name: str
    category: str
    description: str
    base_url: str
    auth_type: AuthType
    https: bool = True
    cors: str = "yes"
    rate_limit_rpm: int = 60
    tags: List[str] = field(default_factory=list)
    param_template: Dict[str, Any] = field(default_factory=dict)
    response_path: Optional[str] = None


# Curated high-reliability public API catalog from public-apis directory
CURATED_API_CATALOG: List[APIEndpointSpec] = [
    # 1. Weather
    APIEndpointSpec(
        api_id="open_meteo_weather",
        name="Open-Meteo Weather API",
        category="Weather",
        description="Free open-source weather forecast API for any coordinate on Earth without API key.",
        base_url="https://api.open-meteo.com/v1/forecast",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=10000,
        tags=["weather", "forecast", "temperature", "climate", "rain", "wind", "meteo"],
        param_template={"latitude": 35.6895, "longitude": 139.6917, "current_weather": True},
    ),
    APIEndpointSpec(
        api_id="wttr_in_weather",
        name="Wttr.in Weather Service",
        category="Weather",
        description="Lightweight weather forecast service for terminal and HTTP clients.",
        base_url="https://wttr.in",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=120,
        tags=["weather", "city", "temperature", "forecast"],
        param_template={"format": "j1"},
    ),

    # 2. Finance & Currency Exchange
    APIEndpointSpec(
        api_id="frankfurter_currency",
        name="Frankfurter Currency API",
        category="Finance",
        description="Free open-source foreign exchange rates and currency conversion data published by European Central Bank.",
        base_url="https://api.frankfurter.app/latest",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=300,
        tags=["finance", "currency", "forex", "exchange", "usd", "eur", "inr", "conversion"],
        param_template={"from": "USD", "to": "EUR,INR,GBP,JPY"},
    ),
    APIEndpointSpec(
        api_id="coingecko_crypto",
        name="CoinGecko Crypto Ticker API",
        category="Finance",
        description="Live cryptocurrency prices, market cap, volume, and coin information.",
        base_url="https://api.coingecko.com/api/v3/simple/price",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=50,
        tags=["crypto", "bitcoin", "ethereum", "btc", "eth", "solana", "price", "finance"],
        param_template={"ids": "bitcoin,ethereum,solana", "vs_currencies": "usd,inr"},
    ),

    # 3. Geocoding & IP Location
    APIEndpointSpec(
        api_id="open_geocoding",
        name="Open-Meteo Geocoding API",
        category="Geocoding",
        description="Fast address and city name to latitude/longitude search without credentials.",
        base_url="https://geocoding-api.open-meteo.com/v1/search",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=600,
        tags=["geocoding", "location", "city", "latitude", "longitude", "gps", "coordinates", "maps"],
        param_template={"name": "Tokyo", "count": 1},
    ),
    APIEndpointSpec(
        api_id="ipapi_geolocation",
        name="ipapi IP Geolocation API",
        category="Geocoding",
        description="Find city, country, ISP, and coordinates for any IP address.",
        base_url="https://ipapi.co/json/",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=1000,
        tags=["ip", "location", "network", "isp", "country", "city"],
        param_template={},
    ),

    # 4. News, Tech & Knowledge
    APIEndpointSpec(
        api_id="hackernews_api",
        name="Hacker News Official Firebase API",
        category="News",
        description="Real-time top stories, tech news, and developer discussions.",
        base_url="https://hacker-news.firebaseio.com/v0/topstories.json",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=1000,
        tags=["news", "tech", "hackernews", "articles", "stories", "programming", "software"],
        param_template={},
    ),
    APIEndpointSpec(
        api_id="wikipedia_summary",
        name="Wikipedia REST API Summary",
        category="Reference",
        description="Official encyclopedic summaries and structured extracts from Wikipedia.",
        base_url="https://en.wikipedia.org/api/rest_v1/page/summary",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=1200,
        tags=["wikipedia", "encyclopedia", "knowledge", "reference", "definition", "science", "history"],
        param_template={"title": "Artificial_intelligence"},
    ),

    # 5. Security & Network Utilities
    APIEndpointSpec(
        api_id="dns_google_doh",
        name="Google Public DNS over HTTPS (DoH)",
        category="Security",
        description="Perform cryptographic DNS lookups over secure HTTPS.",
        base_url="https://dns.google/resolve",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=1500,
        tags=["dns", "network", "domain", "security", "ip", "resolve"],
        param_template={"name": "google.com", "type": "A"},
    ),
    APIEndpointSpec(
        api_id="useless_facts",
        name="Random Knowledge Facts API",
        category="Entertainment",
        description="Curated educational and trivia facts for conversational intelligence.",
        base_url="https://uselessfacts.jsph.pl/api/v2/facts/random",
        auth_type=AuthType.NO_AUTH,
        https=True,
        cors="yes",
        rate_limit_rpm=200,
        tags=["trivia", "facts", "knowledge", "random", "entertainment"],
        param_template={},
    ),
]


class PublicAPICapabilityRegistry:
    """In-memory and persistent catalog of discovered public APIs."""

    def __init__(self, catalog: Optional[List[APIEndpointSpec]] = None):
        self._endpoints: Dict[str, APIEndpointSpec] = {
            spec.api_id: spec for spec in (catalog or CURATED_API_CATALOG)
        }

    def list_all_apis(self) -> List[APIEndpointSpec]:
        return list(self._endpoints.values())

    def get_api(self, api_id: str) -> Optional[APIEndpointSpec]:
        return self._endpoints.get(api_id)

    def get_categories(self) -> List[str]:
        return sorted(list(set(spec.category for spec in self._endpoints.values())))

    def register_api(self, spec: APIEndpointSpec) -> None:
        self._endpoints[spec.api_id] = spec
