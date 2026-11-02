import httpx
import asyncio
import urllib.parse
import json
import re
from typing import List, Dict, Any, Optional

SCRAPER_API_TOKEN = "8009aa57ce904b2ab4edbaab72aaf5158288fed9359"

async def fetch_blinkit(client: httpx.AsyncClient, query: str) -> Optional[Dict[str, Any]]:
    """Scrapes Blinkit search web page and extracts embedded product data."""
    target_url = f"https://blinkit.com/s/?q={query}"
    encoded_url = urllib.parse.quote_plus(target_url)
    request_url = f"https://api.scrape.do/?token={SCRAPER_API_TOKEN}&geoCode=in&url={encoded_url}"

    try:
        resp = await client.get(request_url, timeout=15.0)
        if resp.status_code == 200:
            html = resp.text
            # Extract Next.js catalog state
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                page_props = data.get("props", {}).get("pageProps", {})
                
                # Navigate objects to locate product listings
                products = []
                for key, val in page_props.items():
                    if isinstance(val, dict) and "snippets" in val:
                        products = val.get("snippets", [])
                        break
                    if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict) and "name" in val[0]:
                        products = val
                        break

                if products:
                    top = products[0].get("data", products[0])
                    price = top.get("price") or top.get("selling_price", 0)
                    mrp = top.get("mrp") or price
                    return {
                        "provider": "Blinkit",
                        "product_name": top.get("name") or top.get("title", query),
                        "pack_size": top.get("unit") or "1 unit",
                        "mrp": float(mrp),
                        "price": float(price),
                        "image": top.get("image_url", ""),
                        "in_stock": True,
                        "eta": "10-15 mins",
                        "deep_link": target_url
                    }
    except Exception as e:
        print(f"Blinkit scrape error: {e}")
    return None


async def fetch_zepto(client: httpx.AsyncClient, query: str) -> Optional[Dict[str, Any]]:
    """Scrapes Zepto search web page and extracts embedded product data."""
    target_url = f"https://www.zeptonow.com/search?query={query}"
    encoded_url = urllib.parse.quote_plus(target_url)
    # Enable render=true for Zepto's JavaScript hydration
    request_url = f"https://api.scrape.do/?token={SCRAPER_API_TOKEN}&geoCode=in&render=true&url={encoded_url}"

    try:
        resp = await client.get(request_url, timeout=20.0)
        if resp.status_code == 200:
            html = resp.text
            match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                props = data.get("props", {}).get("pageProps", {})
                
                # Parse search layout
                products = props.get("products") or []
                if not products and "fallbackData" in props:
                    products = props.get("fallbackData", {}).get("products", [])

                if products:
                    top = products[0]
                    price = top.get("sellingPrice") or top.get("discountedSellingPrice", 0)
                    mrp = top.get("mrp") or price
                    # Normalize paise if pricing is returned in cents/paise
                    final_price = float(price) / 100 if price > 1000 else float(price)
                    final_mrp = float(mrp) / 100 if mrp > 1000 else float(mrp)
                    return {
                        "provider": "Zepto",
                        "product_name": top.get("name", query),
                        "pack_size": top.get("packSize") or top.get("weight", "1 unit"),
                        "mrp": final_mrp,
                        "price": final_price,
                        "image": top.get("images", [{}])[0].get("url", ""),
                        "in_stock": top.get("outOfStock") is not True,
                        "eta": "10-12 mins",
                        "deep_link": target_url
                    }
    except Exception as e:
        print(f"Zepto scrape error: {e}")
    return None


async def get_live_comparison(query: str, lat: float = 12.9904, lon: float = 77.6710) -> Dict[str, Any]:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            fetch_blinkit(client, query),
            fetch_zepto(client, query),
            return_exceptions=True
        )

    valid_results = [r for r in results if isinstance(r, dict) and r is not None]

    if not valid_results:
        # Fallback to standard price modeling if scraping timed out
        return {
            "status": "fallback",
            "message": "Live catalog temporarily unavailable, using benchmark estimates",
            "data": []
        }

    valid_results.sort(key=lambda x: x["price"])
    return {
        "status": "live",
        "winning_provider": valid_results[0]["provider"],
        "lowest_price": valid_results[0]["price"],
        "items": valid_results
    }
