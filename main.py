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
    return {"app": "CompareQ Backend", "status": "operational", "version": "2.0.0"}

@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Product query"),
    category: str = Query("grocery", description="Category"),
    lat: float = Query(12.9904, description="Latitude"),
    lon: float = Query(77.6710, description="Longitude")
):
    query_lower = q.lower().strip()
    
    # 1. Base benchmarks per query type
    if any(k in query_lower for k in ["milk", "curd", "dairy"]):
        base_ref = 34.0
        unit_str = "500 ml"
    elif any(k in query_lower for k in ["dolo", "crocin", "paracetamol", "tablet"]):
        base_ref = 30.0
        unit_str = "1 strip (15 tablets)"
    elif any(k in query_lower for k in ["ball", "cricket", "tennis"]):
        base_ref = 85.0
        unit_str = "1 pack"
    elif any(k in query_lower for k in ["rice", "biryani", "fried rice"]):
        base_ref = 160.0
        unit_str = "1 portion"
    else:
        base_ref = 55.0
        unit_str = "1 pack"

    # 2. Try fetching live catalog prices
    live_items = {}
    try:
        live_res = await get_live_comparison(query=q, lat=lat, lon=lon)
        for it in live_res.get("items", []):
            prov = it.get("provider", "").lower()
            if prov and it.get("price"):
                live_items[prov] = float(it.get("price"))
    except Exception as e:
        print(f"Scraper error: {e}")

    # 3. Model stores with exact keys expected by PLATFORM_META
    stores_data = {
        "instamart": {
            "price": live_items.get("instamart", round(base_ref * 0.96, 2)),
            "delivery": 15.0,
            "handling": 5.0,
            "surge": 0.0,
            "eta": "12-15m"
        },
        "blinkit": {
            "price": live_items.get("blinkit", round(base_ref * 1.0, 2)),
            "delivery": 16.0,
            "handling": 4.0,
            "surge": 0.0,
            "eta": "10-12m"
        },
        "zepto": {
            "price": live_items.get("zepto", round(base_ref * 0.98, 2)),
            "delivery": 15.0,
            "handling": 5.0,
            "surge": 0.0,
            "eta": "9-11m"
        },
        "flipkart_minutes": {
            "price": round(base_ref * 0.94, 2),
            "delivery": 10.0,
            "handling": 3.0,
            "surge": 0.0,
            "eta": "15-20m"
        },
        "bbnow": {
            "price": round(base_ref * 0.95, 2),
            "delivery": 15.0,
            "handling": 4.0,
            "surge": 0.0,
            "eta": "15-25m"
        },
        "jiomart": {
            "price": round(base_ref * 0.92, 2),
            "delivery": 0.0,
            "handling": 0.0,
            "surge": 0.0,
            "eta": "30-45m"
        },
        "amazon_fresh": {
            "price": round(base_ref * 0.93, 2),
            "delivery": 25.0,
            "handling": 0.0,
            "surge": 0.0,
            "eta": "2-3 hrs"
        }
    }

    # Compute landed price = price + delivery + handling + surge
    calculated_dict = {}
    best_store_key = None
    min_landed = float("inf")

    for key, s in stores_data.items():
        landed = round(s["price"] + s["delivery"] + s["handling"] + s["surge"], 2)
        calculated_dict[key] = {
            "price": s["price"],
            "delivery": s["delivery"],
            "handling": s["handling"],
            "surge": s["surge"],
            "landed": landed,
            "eta": s["eta"]
        }
        if landed < min_landed:
            min_landed = landed
            best_store_key = key

    best_store = stores_data[best_store_key]

    # 4. Construct product entry matching renderResults()
    product_entry = {
        "name": f"{q.title()}",
        "unit": unit_str,
        "winner": {
            "store": best_store_key,
            "landed": min_landed
        },
        "calculated": calculated_dict
    }

    basket_summary = {
        "best_single_store": {
            "store": best_store_key,
            "total": min_landed,
            "items_total": best_store["price"],
            "fees_total": round(best_store["delivery"] + best_store["handling"] + best_store["surge"], 2),
            "eta": best_store["eta"]
        },
        "total_items_queried": 1
    }

    return {
        "query": q,
        "category": category,
        "status": "success",
        "results": [product_entry],
        "basket_summary": basket_summary
    }

@app.get("/api/compare/live")
async def live_search(q: str = Query(...), lat: float = Query(12.9904), lon: float = Query(77.6710)):
    return await compare_items(q=q, lat=lat, lon=lon)

@app.get("/api/search")
async def search_alias(q: str = Query(...), category: str = Query("grocery")):
    return await compare_items(q=q, category=category)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
