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
# Primary Comparison Route (Called by compareq.netlify.app)
# ---------------------------------------------------------
@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Product query"),
    category: str = Query("grocery", description="Category"),
    lat: float = Query(12.9904, description="Latitude"),
    lon: float = Query(77.6710, description="Longitude")
):
    """
    Main endpoint consumed by the frontend.
    Pulls live catalog data or calibrated fee/item breakdown.
    """
    live_data = await get_live_comparison(query=q, lat=lat, lon=lon)
    
    # Format items to match frontend structure
    formatted_results = []
    for item in live_data.get("items", []):
        formatted_results.append({
            "name": item.get("provider"),
            "product_name": item.get("product_name"),
            "pack_size": item.get("pack_size"),
            "base_price": item.get("price"),
            "fees": 15 if item.get("provider") != "JioMart" else 0,
            "total": item.get("price") + (15 if item.get("provider") != "JioMart" else 0),
            "eta": item.get("eta", "12 mins"),
            "link": item.get("deep_link", "#"),
            "image": item.get("image", "")
        })

    # Sort lowest total price first
    formatted_results.sort(key=lambda x: x["total"])

    return {
        "query": q,
        "category": category,
        "status": live_data.get("status", "success"),
        "cheapest": formatted_results[0]["name"] if formatted_results else "Blinkit",
        "results": formatted_results
    }

# Live Direct Route
@app.get("/api/compare/live")
async def live_search(
    q: str = Query(...),
    lat: float = Query(12.9904),
    lon: float = Query(77.6710)
):
    return await get_live_comparison(query=q, lat=lat, lon=lon)

# Legacy Search Route
@app.get("/api/search")
async def search_alias(
    q: str = Query(...),
    category: str = Query("grocery")
):
    return await compare_items(q=q, category=category)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
