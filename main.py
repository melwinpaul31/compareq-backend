from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import uvicorn

from live_scraper import get_live_comparison

app = FastAPI(
    title="CompareQ Backend API",
    description="Real-time multi-category price aggregator & fee modeling engine",
    version="2.0.0"
)

# Enable CORS for Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "app": "CompareQ Backend",
        "status": "operational",
        "version": "2.0.0"
    }

# ---------------------------------------------------------
# Primary Comparison Route (Populates all frontend aliases)
# ---------------------------------------------------------
@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Product query"),
    category: str = Query("grocery", description="Category"),
    lat: float = Query(12.9904, description="Latitude"),
    lon: float = Query(77.6710, description="Longitude")
):
    live_data = await get_live_comparison(query=q, lat=lat, lon=lon)
    
    formatted_results = []
    for item in live_data.get("items", []):
        provider_name = item.get("provider", "Store")
        prod_title = item.get("product_name") or f"{q.title()} (Standard)"
        base_price = float(item.get("price", 90.0))
        fees = 15.0 if provider_name != "JioMart" else 0.0
        total_price = base_price + fees
        pack = item.get("pack_size", "1 unit")
        eta_str = item.get("eta", "10-15 mins")
        link_url = item.get("deep_link", "#")

        # Provide all aliases to satisfy any frontend field accessor
        formatted_results.append({
            # Store names
            "name": provider_name,
            "store": provider_name,
            "provider": provider_name,
            "store_name": provider_name,

            # Product titles & details
            "product_name": prod_title,
            "product": prod_title,
            "item_name": prod_title,
            "title": prod_title,
            "item": prod_title,
            "pack_size": pack,
            "unit": pack,
            "weight": pack,

            # Pricing & fees
            "base_price": base_price,
            "price": base_price,
            "mrp": float(item.get("mrp", base_price + 20)),
            "fees": fees,
            "fee": fees,
            "platform_fee": fees,
            "delivery_fee": fees,
            "total": total_price,
            "landed_price": total_price,
            "final_price": total_price,
            "total_price": total_price,

            # Metadata
            "eta": eta_str,
            "delivery_time": eta_str,
            "in_stock": item.get("in_stock", True),
            "link": link_url,
            "deep_link": link_url,
            "url": link_url,
            "image": item.get("image", "")
        })

    # Sort so cheapest landed price is first
    formatted_results.sort(key=lambda x: x["landed_price"])
    winner = formatted_results[0] if formatted_results else {}

    return {
        "query": q,
        "category": category,
        "status": "success",
        
        # Winner aliases for the bottom banner
        "cheapest": winner.get("store", "Instamart"),
        "cheapest_store": winner.get("store", "Instamart"),
        "winning_provider": winner.get("store", "Instamart"),
        "winner": winner.get("store", "Instamart"),
        "store": winner.get("store", "Instamart"),
        "lowest_price": winner.get("landed_price", 0),
        "lowest_landed": winner.get("landed_price", 0),
        "winning_price": winner.get("landed_price", 0),

        # Array aliases
        "results": formatted_results,
        "items": formatted_results,
        "data": formatted_results
    }

# Live Direct Route
@app.get("/api/compare/live")
async def live_search(
    q: str = Query(...),
    lat: float = Query(12.9904),
    lon: float = Query(77.6710)
):
    return await compare_items(q=q, lat=lat, lon=lon)

# Legacy Search Route
@app.get("/api/search")
async def search_alias(
    q: str = Query(...),
    category: str = Query("grocery")
):
    return await compare_items(q=q, category=category)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
