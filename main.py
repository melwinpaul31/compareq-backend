from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import uvicorn

# Import the new live scraper engine
from live_scraper import get_live_comparison

app = FastAPI(
    title="CompareQ Backend API",
    description="Real-time multi-category price aggregator & fee modeling engine",
    version="2.0.0"
)

# ---------------------------------------------------------
# CORS Middleware: Allows Netlify frontend and local testing
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------
@app.get("/")
def read_root():
    return {
        "app": "CompareQ Backend",
        "status": "operational",
        "version": "2.0.0"
    }

# ---------------------------------------------------------
# NEW: Live Real-Time Provider Comparison Route
# ---------------------------------------------------------
@app.get("/api/compare/live")
async def live_search(
    q: str = Query(..., description="Product query (e.g., tennis ball, milk, bread)"),
    lat: float = Query(12.9904, description="User latitude (defaults to Bengaluru)"),
    lon: float = Query(77.6710, description="User longitude (defaults to Bengaluru)")
):
    """
    Queries live catalog endpoints (Blinkit, Zepto, etc.) in parallel
    using geographic dark-store coordinates.
    """
    result = await get_live_comparison(query=q, lat=lat, lon=lon)
    return result

# ---------------------------------------------------------
# Existing Heuristic/Fallback Search Route
# ---------------------------------------------------------
@app.get("/api/search")
def search_items(
    q: str = Query(..., description="Search query"),
    category: str = Query("grocery", description="Search category")
):
    """
    Standard benchmark comparison endpoint used as fallback.
    """
    providers = [
        {"name": "JioMart", "base_price": 60, "fees": 0, "eta": "30 mins"},
        {"name": "Flipkart Minutes", "base_price": 62, "fees": 20, "eta": "15 mins"},
        {"name": "BB Now", "base_price": 64, "fees": 18, "eta": "18 mins"},
        {"name": "Blinkit", "base_price": 65, "fees": 19, "eta": "11 mins"},
        {"name": "Amazon Fresh", "base_price": 61, "fees": 29, "eta": "60 mins"},
        {"name": "Zepto", "base_price": 68, "fees": 24, "eta": "10 mins"},
        {"name": "Instamart", "base_price": 66, "fees": 26, "eta": "14 mins"},
    ]

    for p in providers:
        p["total"] = p["base_price"] + p["fees"]

    providers.sort(key=lambda x: x["total"])

    return {
        "query": q,
        "category": category,
        "cheapest": providers[0]["name"],
        "results": providers
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
