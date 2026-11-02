import httpx
import asyncio
import urllib.parse
from typing import Dict, Any, Optional

SCRAPER_API_TOKEN = "8009aa57ce904b2ab4edbaab72aaf5158288fed9359"

# Base coordinates for Bengaluru
DEFAULT_LAT = 12.9904
DEFAULT_LON = 77.6710

async def fetch_blinkit(client: httpx.AsyncClient, query: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Calls Blinkit's layout search endpoint through Scrape.do
    with geographic coordinate headers.
    """
    target_api = f"https://blinkit.com/v1/search/products?q={query}&start=0&size=6"
    encoded_target = urllib.parse.quote_plus(target_api)
    request_url = (
        f"https://api.scrape.do/?token={SCRAPER_API_TOKEN}&geoCode=in"
        f"&customHeaders=true&url={encoded_target}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Blinkit/14.0",
        "Accept": "application/json, text/plain, */*",
        "lat": str(lat),
        "lon": str(lon),
        "app_client": "consumer_ios",
        "device_id": "c71a39f0-281b-4d7a-8f56-0291a1348821"
    }

    try:
        resp = await client.get(request_url, headers=headers, timeout=14.0)
        if resp.status_code == 200:
            data = resp.json()
            # Parse products from layout snippets or direct array
            items = []
            if "products" in data:
                items = data["products"]
            elif "snippet" in data:
                items = data.get("snippet", {}).get("items", [])
            elif "data" in data and isinstance(data["data"], dict):
                items = data["data"].get("products", [])

            if items:
                top = items[0]
                price = float(top.get("price", 0))
                mrp = float(top.get("mrp", price))
                return {
                    "provider": "Blinkit",
                    "product_name": top.get("name") or top.get("title", query),
                    "pack_size": top.get("unit") or top.get("weight", "1 pc"),
                    "mrp": mrp,
                    "price": price,
                    "image": top.get("image_url", ""),
                    "in_stock": top.get("inventory", 1) > 0,
                    "eta": "10-15 mins",
                    "deep_link": f"https://blinkit.com/s/?q={query}"
                }
    except Exception as e:
        print(f"Blinkit fetch exception: {e}")
    return None


async def fetch_zepto(client: httpx.AsyncClient, query: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Calls Zepto's search endpoint through Scrape.do
    with dark-store coordinates.
    """
    target_api = f"https://www.zeptonow.com/api/v3/search?query={query}&pageNumber=1&mode=SEARCH"
    encoded_target = urllib.parse.quote_plus(target_api)
    request_url = (
        f"https://api.scrape.do/?token={SCRAPER_API_TOKEN}&geoCode=in"
        f"&customHeaders=true&url={encoded_target}"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "x-user-latitude": str(lat),
        "x-user-longitude": str(lon),
        "compatible_components": "CONVENIENCE_FEE"
    }

    try:
        resp = await client.get(request_url, headers=headers, timeout=14.0)
        if resp.status_code == 200:
            data = resp.json()
            layouts = data.get("layout", []) or data.get("products", [])
            for item in layouts:
                prod = item.get("product") or item.get("data") or item
                if "sellingPrice" in prod or "price" in prod:
                    price = prod.get("sellingPrice") or prod.get("price", 0)
                    mrp = prod.get("mrp") or price
                    final_price = float(price) / 100 if price > 1000 else float(price)
                    final_mrp = float(mrp) / 100 if mrp > 1000 else float(mrp)
                    return {
                        "provider": "Zepto",
                        "product_name": prod.get("name", query),
                        "pack_size": prod.get("packSize") or prod.get("weight", "1 pc"),
                        "mrp": final_mrp,
                        "price": final_price,
                        "image": prod.get("images", [{}])[0].get("url", ""),
                        "in_stock": prod.get("outOfStock") is not True,
                        "eta": "10-12 mins",
                        "deep_link": f"https://www.zeptonow.com/search?query={query}"
                    }
    except Exception as e:
        print(f"Zepto fetch exception: {e}")
    return None


async def get_live_comparison(query: str, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> Dict[str, Any]:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            fetch_blinkit(client, query, lat, lon),
            fetch_zepto(client, query, lat, lon),
            return_exceptions=True
        )

    valid_results = [r for r in results if isinstance(r, dict) and r is not None]

    if not valid_results:
        # Structured benchmark fallback so the frontend never gets blank screens
        fallback_items = [
            {"provider": "Blinkit", "product_name": f"{query.title()} (Standard)", "pack_size": "1 unit", "mrp": 120.0, "price": 95.0, "image": "", "in_stock": True, "eta": "11 mins", "deep_link": f"https://blinkit.com/s/?q={query}"},
            {"provider": "Zepto", "product_name": f"{query.title()} (Standard)", "pack_size": "1 unit", "mrp": 120.0, "price": 99.0, "image": "", "in_stock": True, "eta": "10 mins", "deep_link": f"https://www.zeptonow.com/search?query={query}"},
            {"provider": "Instamart", "product_name": f"{query.title()} (Standard)", "pack_size": "1 unit", "mrp": 120.0, "price": 92.0, "image": "", "in_stock": True, "eta": "14 mins", "deep_link": f"https://www.swiggy.com/instamart/search?custom_back=true&query={query}"}
        ]
        fallback_items.sort(key=lambda x: x["price"])
        return {
            "status": "fallback_model",
            "winning_provider": fallback_items[0]["provider"],
            "lowest_price": fallback_items[0]["price"],
            "items": fallback_items
        }

    valid_results.sort(key=lambda x: x["price"])
    return {
        "status": "live",
        "winning_provider": valid_results[0]["provider"],
        "lowest_price": valid_results[0]["price"],
        "items": valid_results
    }
