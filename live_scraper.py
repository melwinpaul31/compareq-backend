import httpx
import asyncio
from typing import List, Dict, Any, Optional

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Origin": "https://blinkit.com",
    "Referer": "https://blinkit.com/"
}

async def fetch_blinkit(client: httpx.AsyncClient, query: str, lat: float, lon: float) -> Dict[str, Any]:
    url = "https://blinkit.com/v1/search/products"
    headers = {
        **COMMON_HEADERS,
        "lat": str(lat),
        "lon": str(lon),
        "app_client": "consumer_android",
    }
    params = {"q": query, "start": "0", "size": "3"}
    
    try:
        resp = await client.get(url, headers=headers, params=params, timeout=5.0)
        return {
            "provider": "Blinkit",
            "http_status": resp.status_code,
            "response_preview": resp.text[:200]
        }
    except Exception as e:
        return {"provider": "Blinkit", "error": str(e)}

async def fetch_zepto(client: httpx.AsyncClient, query: str, lat: float, lon: float) -> Dict[str, Any]:
    url = "https://api.zeptonow.com/api/v1/search"
    headers = {
        **COMMON_HEADERS,
        "x-user-latitude": str(lat),
        "x-user-longitude": str(lon),
        "platform": "ANDROID",
    }
    params = {"query": query, "page": "1", "mode": "SEARCH"}
    
    try:
        resp = await client.get(url, headers=headers, params=params, timeout=5.0)
        return {
            "provider": "Zepto",
            "http_status": resp.status_code,
            "response_preview": resp.text[:200]
        }
    except Exception as e:
        return {"provider": "Zepto", "error": str(e)}

async def get_live_comparison(query: str, lat: float = 12.9904, lon: float = 77.6710) -> Dict[str, Any]:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            fetch_blinkit(client, query, lat, lon),
            fetch_zepto(client, query, lat, lon),
            return_exceptions=False
        )
    return {
        "status": "debug_run",
        "query": query,
        "server_region": "Render Oregon",
        "debug_results": results
    }
