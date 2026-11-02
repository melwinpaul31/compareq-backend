import httpx
import asyncio
from typing import List, Dict, Any, Optional

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
}

async def fetch_blinkit(client: httpx.AsyncClient, query: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Fetches real-time matching product from Blinkit's mobile catalog endpoint."""
    url = "https://blinkit.com/v1/search/products"
    headers = {
        **COMMON_HEADERS,
        "lat": str(lat),
        "lon": str(lon),
        "app_client": "consumer_android",
    }
    params = {"q": query, "start": "0", "size": "1"}
    
    try:
        resp = await client.get(url, headers=headers, params=params, timeout=4.5)
        if resp.status_code == 200:
            data = resp.json()
            products = data.get("products") or data.get("items", [])
            if products:
                top = products[0]
                return {
                    "provider": "Blinkit",
                    "product_name": top.get("name") or top.get("title", query),
                    "pack_size": top.get("unit") or top.get("weight", "1 pc"),
                    "mrp": float(top.get("mrp", 0)),
                    "price": float(top.get("price", 0)),
                    "image": top.get("image_url", ""),
                    "in_stock": top.get("inventory", 1) > 0,
                    "eta": top.get("eta", "10-15 mins"),
                    "deep_link": f"https://blinkit.com/s/?q={query}"
                }
    except Exception as e:
        print(f"Blinkit fetch error: {e}")
    return None

async def fetch_zepto(client: httpx.AsyncClient, query: str, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """Fetches real-time matching product from Zepto's mobile search endpoint."""
    url = "https://api.zeptonow.com/api/v1/search"
    headers = {
        **COMMON_HEADERS,
        "x-user-latitude": str(lat),
        "x-user-longitude": str(lon),
        "platform": "ANDROID",
    }
    params = {"query": query, "page": "1", "mode": "SEARCH"}
    
    try:
        resp = await client.get(url, headers=headers, params=params, timeout=4.5)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("layout", []) or data.get("products", [])
            for entry in items:
                product = entry.get("product") or entry
                if "sellingPrice" in product or "price" in product:
                    price = product.get("sellingPrice") or product.get("price", 0)
                    mrp = product.get("mrp") or price
                    return {
                        "provider": "Zepto",
                        "product_name": product.get("name", query),
                        "pack_size": product.get("packSize") or product.get("weight", "1 pc"),
                        "mrp": float(mrp) / 100 if mrp > 1000 else float(mrp),
                        "price": float(price) / 100 if price > 1000 else float(price),
                        "image": product.get("images", [{}])[0].get("url", ""),
                        "in_stock": product.get("outOfStock") is not True,
                        "eta": "10-12 mins",
                        "deep_link": f"https://www.zeptonow.com/search?query={query}"
                    }
    except Exception as e:
        print(f"Zepto fetch error: {e}")
    return None

async def get_live_comparison(query: str, lat: float = 12.9904, lon: float = 77.6710) -> Dict[str, Any]:
    """Runs parallel searches across active quick commerce providers."""
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_blinkit(client, query, lat, lon),
            fetch_zepto(client, query, lat, lon),
            return_exceptions=True
        )
    
    valid_results = [r for r in results if isinstance(r, dict) and r is not None]
    
    if not valid_results:
        return {"status": "fallback", "data": []}
        
    valid_results.sort(key=lambda x: x["price"])
    return {
        "status": "live",
        "winning_provider": valid_results[0]["provider"],
        "lowest_price": valid_results[0]["price"],
        "items": valid_results
    }
