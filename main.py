from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import asyncio
import datetime
import urllib.parse
import httpx
import uvicorn

from live_scraper import resolve_product_across_stores

app = FastAPI(
    title="CompareQ Backend API",
    description="Real-time multi-item basket optimizer, provision list scanner & live price engine",
    version="4.2.0"
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
    return {
        "app": "CompareQ Backend",
        "status": "operational",
        "version": "4.2.0",
        "features": ["universal_search", "multi_item_basket", "provision_list_scanner", "wait_and_save", "live_store_status"]
    }

async def check_live_store_operational_status(store_key: str) -> Dict[str, Any]:
    """
    Pings the platform's live search or storefront endpoint in the background
    to verify whether dark stores / quick-commerce fulfillment centers are actively accepting orders.
    """
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=5, minutes=30)
    current_hour = now.hour

    # Instant quick commerce apps run 24x7 or until 2 AM in active pin codes
    if store_key in ["zepto", "blinkit", "amazon_now"]:
        is_open = True
        status_text = "🟢 Open · Instant 10m"
    elif store_key in ["instamart", "bbnow", "flipkart_minutes"]:
        is_open = (current_hour >= 6 or current_hour < 2)
        status_text = "🟢 Delivering Now" if is_open else "🔴 Closed · Opens 6 AM"
    elif store_key == "jiomart":
        is_open = (7 <= current_hour < 23)
        status_text = "🟢 Open · Slotted" if is_open else "🟡 Opens 7 AM"
    elif store_key in ["amazon_standard", "flipkart_standard"]:
        is_open = True
        status_text = "⏳ Wait & Save · 1-2 Days"
    else:
        is_open = True
        status_text = "🟢 Open"

    # Live background network check for availability
    try:
        test_urls = {
            "zepto": "https://www.zeptonow.com",
            "blinkit": "https://blinkit.com",
            "amazon_now": "https://www.amazon.in/alm/storefront?almBrandId=ctnow",
            "instamart": "https://www.swiggy.com/instamart"
        }
        if store_key in test_urls:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.head(test_urls[store_key], follow_redirects=True)
                if resp.status_code >= 500:
                    is_open = False
                    status_text = "🟡 High Traffic · Delayed"
    except Exception:
        pass  # Fall back to time-based rules if network check times out

    return {"is_open": is_open, "status_text": status_text}

STORE_RULES = {
    "zepto": {"name": "Zepto", "del": 25.0, "free_above": 199.0, "hand": 5.0, "surge": 0.0, "small_cart": 15.0, "small_cart_below": 99.0, "eta": "9-11m", "type": "instant"},
    "instamart": {"name": "Instamart", "del": 25.0, "free_above": 199.0, "hand": 5.0, "surge": 0.0, "small_cart": 15.0, "small_cart_below": 99.0, "eta": "10-14m", "type": "instant"},
    "blinkit": {"name": "Blinkit", "del": 25.0, "free_above": 199.0, "hand": 5.0, "surge": 0.0, "small_cart": 15.0, "small_cart_below": 99.0, "eta": "8-11m", "type": "instant"},
    "amazon_now": {"name": "Amazon Now", "del": 0.0, "free_above": 99.0, "hand": 2.0, "surge": 0.0, "small_cart": 0.0, "small_cart_below": 0.0, "eta": "10-15m", "type": "instant"},
    "flipkart_minutes": {"name": "Flipkart Minutes", "del": 15.0, "free_above": 99.0, "hand": 3.0, "surge": 0.0, "small_cart": 0.0, "small_cart_below": 0.0, "eta": "12-18m", "type": "instant"},
    "bbnow": {"name": "BB Now", "del": 30.0, "free_above": 199.0, "hand": 8.0, "surge": 15.0, "small_cart": 15.0, "small_cart_below": 99.0, "eta": "10-15m", "type": "instant"},
    "jiomart": {"name": "JioMart", "del": 0.0, "free_above": 0.0, "hand": 2.0, "surge": 0.0, "small_cart": 0.0, "small_cart_below": 0.0, "eta": "30-45m", "type": "slotted"},
    "amazon_standard": {"name": "Amazon Standard", "del": 0.0, "free_above": 0.0, "hand": 0.0, "surge": 0.0, "small_cart": 0.0, "small_cart_below": 0.0, "eta": "1-2 Days", "type": "wait_and_save"},
    "flipkart_standard": {"name": "Flipkart Standard", "del": 0.0, "free_above": 0.0, "hand": 0.0, "surge": 0.0, "small_cart": 0.0, "small_cart_below": 0.0, "eta": "1-2 Days", "type": "wait_and_save"}
}

def make_store_urls(query_str: str) -> Dict[str, str]:
    clean = query_str.strip()
    enc = urllib.parse.quote_plus(clean)
    return {
        "zepto": f"https://www.zeptonow.com/search?query={enc}",
        "instamart": f"https://www.swiggy.com/instamart/search?custom_back=true&query={enc}",
        "blinkit": f"https://blinkit.com/s/?q={enc}",
        "amazon_now": f"https://www.amazon.in/s?k={enc}&i=nowstore&almBrandId=ctnow&tag=compareq-21",
        "bbnow": f"https://www.bigbasket.com/ps/?q={enc}",
        "flipkart_minutes": f"https://www.flipkart.com/search?q={enc}&marketplace=HYPERLOCAL&affid=compareq",
        "jiomart": f"https://www.jiomart.com/search?q={enc}",
        "amazon_standard": f"https://www.amazon.in/s?k={enc}&tag=compareq-21",
        "flipkart_standard": f"https://www.flipkart.com/search?q={enc}&affid=compareq"
    }

@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Single product or comma-separated provision list"),
    category: str = Query("grocery", description="Category"),
    wait_and_save: bool = Query(False, description="Include Amazon Standard & Flipkart Standard (1-2 day delivery) for extra savings"),
    lat: float = Query(12.9904, description="Latitude"),
    lon: float = Query(77.6710, description="Longitude")
):
    raw_items = [item.strip() for item in q.replace("\n", ",").split(",") if item.strip()]
    if not raw_items:
        raw_items = [q.strip()]

    resolved_list, store_statuses_list = await asyncio.gather(
        asyncio.gather(*[resolve_product_across_stores(item, lat=lat, lon=lon) for item in raw_items]),
        asyncio.gather(*[check_live_store_operational_status(k) for k in STORE_RULES.keys()])
    )

    store_status_map = {list(STORE_RULES.keys())[i]: store_statuses_list[i] for i in range(len(STORE_RULES))}

    active_store_keys = [
        k for k, rule in STORE_RULES.items()
        if wait_and_save or rule["type"] != "wait_and_save"
    ]

    results_payload = []
    basket_store_subtotals = {k: 0.0 for k in active_store_keys}

    for idx, item_query in enumerate(raw_items):
        res = resolved_list[idx]
        title = res["title"]
        unit = res["unit"]
        store_prices = res["store_prices"]
        urls = make_store_urls(item_query)

        calculated_dict = {}
        best_store_key = None
        min_landed = float("inf")

        for store_key in active_store_keys:
            rule = STORE_RULES[store_key]
            shelf_price = float(store_prices.get(store_key, 50.0))
            basket_store_subtotals[store_key] = round(basket_store_subtotals[store_key] + shelf_price, 2)

            del_fee = 0.0 if shelf_price >= rule["free_above"] else rule["del"]
            hand_fee = rule["hand"]
            surge_fee = rule["surge"]
            small_cart_fee = rule["small_cart"] if shelf_price < rule["small_cart_below"] else 0.0
            total_fees = round(del_fee + hand_fee + surge_fee + small_cart_fee, 2)
            landed = round(shelf_price + total_fees, 2)
            status_info = store_status_map.get(store_key, {"is_open": True, "status_text": "🟢 Open"})

            calculated_dict[store_key] = {
                "price": shelf_price,
                "delivery": del_fee,
                "handling": hand_fee,
                "surge": round(surge_fee + small_cart_fee, 2),
                "small_cart": small_cart_fee,
                "total_fees": total_fees,
                "landed": landed,
                "eta": rule["eta"],
                "delivery_type": rule["type"],
                "brand_product": title,
                "is_open": status_info["is_open"],
                "status_text": status_info["status_text"],
                "url": urls.get(store_key, "#")
            }

            if status_info["is_open"] and landed < min_landed:
                min_landed = landed
                best_store_key = store_key

        if not best_store_key:
            best_store_key = min(calculated_dict.keys(), key=lambda k: calculated_dict[k]["landed"])
            min_landed = calculated_dict[best_store_key]["landed"]

        results_payload.append({
            "query_item": item_query,
            "name": title,
            "unit": unit,
            "winner": {
                "store": best_store_key,
                "landed": min_landed
            },
            "calculated": calculated_dict
        })

    all_store_baskets = []
    best_basket_store = None

    for store_key in active_store_keys:
        rule = STORE_RULES[store_key]
        items_subtotal = round(basket_store_subtotals[store_key], 2)
        combined_delivery = 0.0 if items_subtotal >= rule["free_above"] else rule["del"]
        combined_handling = rule["hand"]
        combined_surge = rule["surge"] if items_subtotal < rule["free_above"] else 0.0
        combined_small_cart = rule["small_cart"] if items_subtotal < rule["small_cart_below"] else 0.0
        combined_fees = round(combined_delivery + combined_handling + combined_surge + combined_small_cart, 2)
        grand_total = round(items_subtotal + combined_fees, 2)
        status_info = store_status_map.get(store_key, {"is_open": True, "status_text": "🟢 Open"})

        store_basket_obj = {
            "store": store_key,
            "store_name": rule["name"],
            "items_total": items_subtotal,
            "fees_total": combined_fees,
            "delivery_fee": combined_delivery,
            "handling_fee": combined_handling,
            "surge_fee": combined_surge,
            "small_cart_fee": combined_small_cart,
            "free_delivery_unlocked": combined_delivery == 0.0,
            "total": grand_total,
            "eta": rule["eta"],
            "delivery_type": rule["type"],
            "is_open": status_info["is_open"],
            "status_text": status_info["status_text"]
        }
        all_store_baskets.append(store_basket_obj)

    all_store_baskets.sort(key=lambda x: x["total"])

    for b in all_store_baskets:
        if b["is_open"]:
            best_basket_store = b
            break

    if not best_basket_store:
        best_basket_store = all_store_baskets[0]

    highest_basket_total = all_store_baskets[-1]["total"]
    max_basket_savings = round(highest_basket_total - best_basket_store["total"], 2)

    basket_summary = {
        "best_single_store": best_basket_store,
        "all_stores_ranking": all_store_baskets,
        "max_savings": max_basket_savings,
        "total_items_queried": len(raw_items),
        "queried_items_list": raw_items
    }

    return {
        "query": q,
        "category": category,
        "wait_and_save": wait_and_save,
        "status": "success",
        "results": results_payload,
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
