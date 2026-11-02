import httpx
import asyncio
import urllib.parse
import json
import re
from typing import Dict, Any

SCRAPER_API_TOKEN = "8009aa57ce904b2ab4edbaab72aaf5158288fed9359"

async def inspect_blinkit(client: httpx.AsyncClient, query: str) -> Dict[str, Any]:
    target_url = f"https://blinkit.com/s/?q={query}"
    encoded_url = urllib.parse.quote_plus(target_url)
    request_url = f"https://api.scrape.do/?token={SCRAPER_API_TOKEN}&geoCode=in&url={encoded_url}"

    try:
        resp = await client.get(request_url, timeout=18.0)
        html = resp.text
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if match:
            raw_json = json.loads(match.group(1))
            props = raw_json.get("props", {})
            page_props = props.get("pageProps", {})
            return {
                "found_next_data": True,
                "top_keys": list(raw_json.keys()),
                "page_prop_keys": list(page_props.keys()) if isinstance(page_props, dict) else str(type(page_props)),
                "raw_snippet": str(page_props)[:400]
            }
        return {"found_next_data": False, "html_preview": html[:300]}
    except Exception as e:
        return {"error": str(e)}

async def inspect_zepto(client: httpx.AsyncClient, query: str) -> Dict[str, Any]:
    target_url = f"https://www.zeptonow.com/search?query={query}"
    encoded_url = urllib.parse.quote_plus(target_url)
    request_url = f"https://api.scrape.do/?token={SCRAPER_API_TOKEN}&geoCode=in&render=true&url={encoded_url}"

    try:
        resp = await client.get(request_url, timeout=22.0)
        html = resp.text
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if match:
            raw_json = json.loads(match.group(1))
            props = raw_json.get("props", {})
            page_props = props.get("pageProps", {})
            return {
                "found_next_data": True,
                "top_keys": list(raw_json.keys()),
                "page_prop_keys": list(page_props.keys()) if isinstance(page_props, dict) else str(type(page_props)),
                "raw_snippet": str(page_props)[:400]
            }
        return {"found_next_data": False, "html_preview": html[:300]}
    except Exception as e:
        return {"error": str(e)}

async def get_live_comparison(query: str, lat: float = 12.9904, lon: float = 77.6710) -> Dict[str, Any]:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        b_res, z_res = await asyncio.gather(
            inspect_blinkit(client, query),
            inspect_zepto(client, query),
            return_exceptions=False
        )

    return {
        "status": "schema_discovery",
        "blinkit": b_res,
        "zepto": z_res
    }
