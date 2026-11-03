from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import urllib.parse
import uvicorn

from live_scraper import get_live_comparison

app = FastAPI(
    title="CompareQ Backend API",
    description="Real-time multi-category dynamic quick commerce aggregator",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"app": "CompareQ Dynamic Backend", "status": "operational", "version": "4.0.0"}

@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Any search query entered by the user"),
    category: str = Query("grocery", description="Category"),
    lat: float = Query(12.9904, description="Latitude"),
    lon: float = Query(77.6710, description="Longitude")
):
    clean_query = q.strip()
    
    # Fetch live results from scraper
    scraped_res = await get_live_comparison(query=clean_query, lat=lat, lon=lon)
    items = scraped_res.get("items", [])
    
    if not items:
        return {
            "query": clean_query,
            "status": "no_results",
            "results": [],
            "message": "No live listings found for this search term on quick commerce apps."
        }

    # Format results for the frontend
    calculated_dict = {}
    min_price = float("inf")
    best_store = None

    for item in items:
        store_key = item["provider"]
        price = item["price"]
        
        calculated_dict[store_key] = {
            "price": price,
            "total": price,  # Raw item price as requested
            "eta": "10-15m",
            "brand_product": item["product_name"],
            "is_open": True,
            "status_text": "🟢 Available",
            "url": item["url"]
        }

        if price < min_price:
            min_price = price
            best_store = store_key

    return {
        "query": clean_query,
        "category": category,
        "status": "success",
        "results": [
            {
                "name": clean_query.title(),
                "unit": "Live Search Result",
                "winner": {
                    "store": best_store,
                    "total": min_price
                },
                "calculated": calculated_dict
            }
        ]
    }

@app.get("/api/search")
async def search_alias(q: str = Query(...), category: str = Query("grocery")):
    return await compare_items(q=q, category=category)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
