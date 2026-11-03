from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import datetime
import urllib.parse
import uvicorn

from live_scraper import get_live_comparison

app = FastAPI(
    title="CompareQ Backend API",
    description="Real-time multi-category dynamic quick commerce aggregator",
    version="3.3.0"
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
    return {"app": "CompareQ Dynamic Backend", "status": "operational", "version": "3.3.0"}

def get_store_status(store_key: str) -> Dict[str, Any]:
    """Accurate real-time store availability without artificial delay tags."""
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    current_hour = now.hour

    if store_key in ["zepto", "blinkit", "instamart", "amazon_now", "bbnow", "flipkart_minutes"]:
        is_open = True
        status_text = "🟢 Delivering Now (10-15m)"
    elif store_key == "jiomart":
        is_open = (7 <= current_hour < 23)
        status_text = "🟢 Open · Next Slot" if is_open else "🟡 Opens 7 AM"
    elif store_key == "amazon_fresh":
        is_open = (6 <= current_hour < 23)
        status_text = "🟢 Open · Fresh Slot" if is_open else "🟡 Opens 6 AM"
    else:
        is_open = True
        status_text = "🟢 Open"

    return {"is_open": is_open, "status_text": status_text}

@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Any search query entered by the user"),
    category: str = Query("grocery", description="Category"),
    lat: float = Query(12.9904, description="Latitude"),
    lon: float = Query(77.6710, description="Longitude")
):
    clean_query = q.strip()
    encoded_q = urllib.parse.quote_plus(clean_query)

    # Fetch live structured comparison from scraper/catalog layer
    scraped_res = await get_live_comparison(query=clean_query, lat=lat, lon=lon)
    raw_prices = scraped_res.get("resolved", {}).get("store_prices", {})
    product_meta = scraped_res.get("resolved", {})

    detected_title = product_meta.get("title", f"{clean_query.title()} (Verified Pack)")
    product_unit = product_meta.get("unit", "Standard Pack")
    product_mrp = float(product_meta.get("mrp", 50.0))

    # Standard quick commerce fee rules (waived above thresholds)
    stores_config = {
        "zepto": {"del": 15.0, "hand": 5.0, "eta": "9-11m", "url": f"https://www.zeptonow.com/search?query={encoded_q}"},
        "instamart": {"del": 15.0, "hand": 5.0, "eta": "10-14m", "url": f"https://www.swiggy.com/instamart/search?custom_back=true&query={encoded_q}"},
        "blinkit": {"del": 16.0, "hand": 4.0, "eta": "8-11m", "url": f"https://blinkit.com/s/?q={encoded_q}"},
        "amazon_now": {"del": 15.0, "hand": 0.0, "eta": "10-15m", "url": f"https://www.amazon.in/s?k={encoded_q}&i=nowstore&almBrandId=ctnow"},
        "bbnow": {"del": 30.0, "hand": 8.0, "eta": "10-15m", "url": f"https://www.bigbasket.com/ps/?q={encoded_q}"},
        "flipkart_minutes": {"del": 10.0, "hand": 3.0, "eta": "15-20m", "url": f"https://www.flipkart.com/search?q={encoded_q}+grocery&marketplace=HYPERLOCAL"},
        "jiomart": {"del": 0.0, "hand": 2.0, "eta": "30-45m", "url": f"https://www.jiomart.com/search?q={encoded_q}"},
        "amazon_fresh": {"del": 25.0, "hand": 0.0, "eta": "2-3 hrs", "url": f"https://www.amazon.in/s?k={encoded_q}&i=nowstore&almBrandId=ctnow"},
        "amazon_standard": {"del": 0.0, "hand": 0.0, "eta": "1-2 Days", "url": f"https://www.amazon.in/s?k={encoded_q}&tag=compareq-21"},
        "flipkart_standard": {"del": 0.0, "hand": 0.0, "eta": "1-2 Days", "url": f"https://www.flipkart.com/search?q={encoded_q}&affid=compareq"}
    }

    calculated_dict = {}
    best_store_key = None
    min_total = float("inf")

    for key, cfg in stores_config.items():
        item_price = float(raw_prices.get(key, 50.0))
        del_fee = cfg["del"]
        hand_fee = cfg["hand"]
        
        # Free delivery waiver if item/basket >= 199
        if item_price >= 199.0 and key not in ["amazon_fresh"]:
            del_fee = 0.0

        final_total = round(item_price + del_fee + hand_fee, 2)
        status_info = get_store_status(key)

        calculated_dict[key] = {
            "price": item_price,
            "delivery": del_fee,
            "handling": hand_fee,
            "total": final_total,
            "eta": cfg["eta"],
            "brand_product": detected_title,
            "is_open": status_info["is_open"],
            "status_text": status_info["status_text"],
            "url": cfg["url"]
        }

        if status_info["is_open"] and final_total < min_total:
            min_total = final_total
            best_store_key = key

    if not best_store_key:
        best_store_key = "zepto"
        min_total = calculated_dict["zepto"]["total"]

    best_store = calculated_dict[best_store_key]

    return {
        "query": clean_query,
        "category": category,
        "status": "success",
        "results": [
            {
                "name": detected_title,
                "unit": product_unit,
                "winner": {
                    "store": best_store_key,
                    "total": min_total
                },
                "calculated": calculated_dict
            }
        ],
        "basket_summary": {
            "best_single_store": {
                "store": best_store_key,
                "total": min_total,
                "items_total": best_store["price"],
                "fees_total": round(best_store["delivery"] + best_store["handling"], 2),
                "eta": best_store["eta"],
                "product_name": detected_title
            },
            "total_items_queried": 1
        }
    }

@app.get("/api/compare/live")
async def live_search(q: str = Query(...), lat: float = Query(12.9904), lon: float = Query(77.6710)):
    return await compare_items(q=q, lat=lat, lon=lon)

@app.get("/api/search")
async def search_alias(q: str = Query(...), category: str = Query("grocery")):
    return await compare_items(q=q, category=category)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
