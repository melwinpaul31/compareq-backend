import httpx
import asyncio
import urllib.parse
from typing import Dict, Any

SCRAPER_API_TOKEN = "8009aa57ce904b2ab4edbaab72aaf5158288fed9359"

async def inspect_endpoint(client: httpx.AsyncClient, name: str, target_url: str) -> Dict[str, Any]:
    encoded_target = urllib.parse.quote_plus(target_url)
    request_url = f"https://api.scrape.do/?token={SCRAPER_API_TOKEN}&geoCode=in&url={encoded_target}"
    
    try:
        resp = await client.get(request_url, timeout=15.0)
        return {
            "provider": name,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("content-type", "unknown"),
            "raw_preview": resp.text[:400]
        }
    except Exception as e:
        return {"provider": name, "error": str(e)}

async def get_live_comparison(query: str, lat: float = 12.9904, lon: float = 77.6710) -> Dict[str, Any]:
    # Testing both public search web URLs and internal API paths
    blinkit_url = f"https://blinkit.com/v1/search/products?q={query}&start=0&size=2"
    zepto_url = f"https://www.zeptonow.com/search?query={query}"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            inspect_endpoint(client, "Blinkit", blinkit_url),
            inspect_endpoint(client, "Zepto", zepto_url),
            return_exceptions=False
        )

    return {
        "status": "proxy_diagnostic",
        "proxy_key_active": True,
        "diagnostics": results
    }
