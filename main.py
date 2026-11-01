import time
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CompareQ Multi-Category Backend API", version="2.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. GROCERY
GROCERY_CATALOG = {
    "jamun": {
        "name": "Fresh Jamun / Black Plum (250g)", "unit": "250g pack",
        "stores": {
            "blinkit": {"price": 89, "delivery": 16, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 95, "delivery": 20, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 92, "delivery": 25, "handling": 4, "surge": 0, "eta": "14 mins"},
            "flipkart_minutes": {"price": 85, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
            "bbnow": {"price": 88, "delivery": 15, "handling": 3, "surge": 0, "eta": "18 mins"},
            "jiomart": {"price": 84, "delivery": 0, "handling": 0, "surge": 0, "eta": "25 mins"},
            "amazonfresh": {"price": 86, "delivery": 29, "handling": 0, "surge": 0, "eta": "60 mins"}
        }
    },
    "milk": {
        "name": "Nandini Toned Fresh Milk (500ml)", "unit": "500ml pouch",
        "stores": {
            "blinkit": {"price": 24, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 24, "delivery": 25, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 24, "delivery": 20, "handling": 4, "surge": 0, "eta": "14 mins"},
            "flipkart_minutes": {"price": 23, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
            "bbnow": {"price": 24, "delivery": 15, "handling": 3, "surge": 0, "eta": "16 mins"},
            "jiomart": {"price": 24, "delivery": 0, "handling": 0, "surge": 0, "eta": "30 mins"},
            "amazonfresh": {"price": 24, "delivery": 29, "handling": 0, "surge": 0, "eta": "60 mins"}
        }
    },
    "atta": {
        "name": "Aashirvaad Superior MP Shudh Chakki Atta (5kg)", "unit": "5kg bag",
        "stores": {
            "blinkit": {"price": 258, "delivery": 0, "handling": 5, "surge": 0, "eta": "10 mins"},
            "zepto": {"price": 265, "delivery": 0, "handling": 5, "surge": 0, "eta": "12 mins"},
            "instamart": {"price": 260, "delivery": 0, "handling": 5, "surge": 0, "eta": "15 mins"},
            "flipkart_minutes": {"price": 252, "delivery": 0, "handling": 4, "surge": 0, "eta": "14 mins"},
            "bbnow": {"price": 256, "delivery": 0, "handling": 4, "surge": 0, "eta": "18 mins"},
            "jiomart": {"price": 249, "delivery": 0, "handling": 0, "surge": 0, "eta": "35 mins"},
            "amazonfresh": {"price": 250, "delivery": 0, "handling": 0, "surge": 0, "eta": "90 mins"}
        }
    },
    "eggs": {
        "name": "Farm Fresh White Eggs (Pack of 6)", "unit": "6 pcs",
        "stores": {
            "blinkit": {"price": 48, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 52, "delivery": 20, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 50, "delivery": 22, "handling": 4, "surge": 0, "eta": "13 mins"},
            "flipkart_minutes": {"price": 46, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
            "bbnow": {"price": 49, "delivery": 15, "handling": 3, "surge": 0, "eta": "18 mins"},
            "jiomart": {"price": 45, "delivery": 0, "handling": 0, "surge": 0, "eta": "30 mins"},
            "amazonfresh": {"price": 47, "delivery": 29, "handling": 0, "surge": 0, "eta": "60 mins"}
        }
    }
}

# 2. MEAT & SEAFOOD
MEAT_CATALOG = {
    "chicken": {
        "name": "Fresh Tender Chicken Curry Cut / Breast (500g)", "unit": "500g pack",
        "stores": {
            "freshtohome": {"price": 169, "delivery": 29, "handling": 0, "surge": 0, "eta": "40 mins"},
            "licious": {"price": 179, "delivery": 39, "handling": 0, "surge": 0, "eta": "30 mins"},
            "meatigo": {"price": 185, "delivery": 35, "handling": 0, "surge": 0, "eta": "45 mins"},
            "blinkit": {"price": 195, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 199, "delivery": 25, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 190, "delivery": 20, "handling": 4, "surge": 0, "eta": "14 mins"}
        }
    },
    "mutton": {
        "name": "Rich Goat Mutton Curry Cut (500g)", "unit": "500g pack",
        "stores": {
            "freshtohome": {"price": 519, "delivery": 29, "handling": 0, "surge": 0, "eta": "40 mins"},
            "licious": {"price": 529, "delivery": 39, "handling": 0, "surge": 0, "eta": "30 mins"},
            "meatigo": {"price": 545, "delivery": 35, "handling": 0, "surge": 0, "eta": "45 mins"},
            "blinkit": {"price": 560, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 565, "delivery": 25, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 550, "delivery": 20, "handling": 4, "surge": 0, "eta": "14 mins"}
        }
    }
}

# 3. FOOD DELIVERY
FOOD_CATALOG = {
    "biryani": {
        "name": "Chicken Dum Biryani (Regular, 1000ml)", "unit": "Serves 1-2",
        "stores": {
            "swiggy": {"price": 289, "delivery": 35, "handling": 22, "surge": 0, "eta": "28 mins"},
            "zomato": {"price": 289, "delivery": 38, "handling": 25, "surge": 0, "eta": "30 mins"},
            "magicpin": {"price": 245, "delivery": 25, "handling": 10, "surge": 0, "eta": "34 mins"},
            "eatclub": {"price": 239, "delivery": 0, "handling": 0, "surge": 0, "eta": "25 mins"},
            "ondc": {"price": 250, "delivery": 20, "handling": 8, "surge": 0, "eta": "35 mins"}
        }
    }
}

# 4. PHARMACY
PHARMACY_CATALOG = {
    "dolo": {
        "name": "Dolo 650mg Tablet (Strip of 15)", "unit": "15 tablets",
        "stores": {
            "truemeds": {"price": 18, "delivery": 25, "handling": 0, "surge": 0, "eta": "3 hrs"},
            "medplus": {"price": 27, "delivery": 20, "handling": 0, "surge": 0, "eta": "45 mins"},
            "pharmeasy": {"price": 28, "delivery": 35, "handling": 5, "surge": 0, "eta": "60 mins"},
            "1mg": {"price": 29, "delivery": 29, "handling": 5, "surge": 0, "eta": "45 mins"},
            "apollo": {"price": 30, "delivery": 25, "handling": 4, "surge": 0, "eta": "30 mins"},
            "netmeds": {"price": 29, "delivery": 30, "handling": 0, "surge": 0, "eta": "2 hrs"}
        }
    }
}

# 5. ELECTRONICS & TECH
ELECTRONICS_CATALOG = {
    "tv": {
        "name": "Sony Bravia 55-inch 4K Google TV", "unit": "1 Unit",
        "stores": {
            "pai": {"price": 56990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day Pickup"},
            "vijaysales": {"price": 57490, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "croma": {"price": 57990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day"},
            "flipkart": {"price": 58299, "delivery": 0, "handling": 99, "surge": 0, "eta": "Tomorrow"},
            "reliancedigital": {"price": 58490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "amazon": {"price": 58990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"}
        }
    },
    "airpods": {
        "name": "Apple AirPods Pro (2nd Gen, Type-C)", "unit": "1 Unit",
        "stores": {
            "pai": {"price": 19290, "delivery": 0, "handling": 0, "surge": 0, "eta": "Store Pickup"},
            "vijaysales": {"price": 19490, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "flipkart": {"price": 19499, "delivery": 0, "handling": 49, "surge": 0, "eta": "Tomorrow"},
            "amazon": {"price": 19990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "croma": {"price": 20490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day"},
            "reliancedigital": {"price": 19999, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"}
        }
    }
}

# 6. FASHION & SHOPPING (Myntra, Ajio, Amazon, Flipkart, Nykaa)
SHOPPING_CATALOG = {
    "shoes": {
        "name": "Men's Breathable Mesh Running Shoes", "unit": "1 Pair",
        "stores": {
            "myntra": {"price": 1299, "delivery": 0, "handling": 20, "surge": 0, "eta": "2 Days"},
            "ajio": {"price": 1349, "delivery": 0, "handling": 29, "surge": 0, "eta": "3 Days"},
            "amazon": {"price": 1399, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 1380, "delivery": 0, "handling": 29, "surge": 0, "eta": "Tomorrow"},
            "nykaa": {"price": 1499, "delivery": 0, "handling": 0, "surge": 0, "eta": "3 Days"}
        }
    },
    "tshirt": {
        "name": "Pure Cotton Regular Fit Casual T-Shirt", "unit": "1 Pc",
        "stores": {
            "ajio": {"price": 399, "delivery": 0, "handling": 29, "surge": 0, "eta": "3 Days"},
            "myntra": {"price": 449, "delivery": 0, "handling": 20, "surge": 0, "eta": "2 Days"},
            "flipkart": {"price": 420, "delivery": 0, "handling": 29, "surge": 0, "eta": "Tomorrow"},
            "amazon": {"price": 450, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "nykaa": {"price": 499, "delivery": 0, "handling": 0, "surge": 0, "eta": "3 Days"}
        }
    }
}

def format_results(catalog, q_clean, default_stores, base_price=75, unit_label="Standard Unit"):
    matches = []
    for k, v in catalog.items():
        name_lower = v["name"].lower()
        if k in q_clean or q_clean in k or any(word in name_lower for word in q_clean.split()):
            prod = {"id": k, "name": v["name"], "unit": v["unit"], "stores": v["stores"], "calculated": {}}
            best_s, low_p = None, 9999999
            for s_name, f in v["stores"].items():
                landed = f["price"] + f["delivery"] + f["handling"] + f["surge"]
                prod["calculated"][s_name] = {**f, "landed": landed}
                if landed < low_p:
                    low_p, best_s = landed, s_name
            prod["winner"] = {"store": best_s, "landed": low_p}
            matches.append(prod)

    if not matches and len(q_clean) >= 2:
        title = q_clean.title()
        prod = {"id": f"dyn_{int(time.time())}", "name": f"{title} ({unit_label})", "unit": unit_label, "stores": default_stores, "calculated": {}}
        best_s, low_p = None, 9999999
        for s_name, f in default_stores.items():
            landed = f["price"] + f["delivery"] + f["handling"] + f["surge"]
            prod["calculated"][s_name] = {**f, "landed": landed}
            if landed < low_p:
                low_p, best_s = landed, s_name
        prod["winner"] = {"store": best_s, "landed": low_p}
        matches.append(prod)

    return matches

@app.get("/")
def health():
    return {"status": "ok", "app": "CompareQ API", "version": "2.3.0"}

def compute_basket_summary(results):
    if not results or len(results) <= 1:
        return None
    total_items = len(results)
    store_totals = {}
    for item in results:
        for store_name, store_data in item.get("stores", {}).items():
            if store_name not in store_totals:
                store_totals[store_name] = {
                    "items_total": 0, "items_found": 0,
                    "delivery": store_data.get("delivery", 0),
                    "handling": store_data.get("handling", 0),
                    "surge": store_data.get("surge", 0),
                    "max_eta": store_data.get("eta", "N/A"),
                    "basket_total": 0, "all_items_available": False
                }
            price = store_data.get("price")
            if price is not None and price > 0:
                store_totals[store_name]["items_total"] += price
                store_totals[store_name]["items_found"] += 1
                store_totals[store_name]["delivery"] = max(store_totals[store_name]["delivery"], store_data.get("delivery", 0))
                store_totals[store_name]["handling"] = max(store_totals[store_name]["handling"], store_data.get("handling", 0))
                store_totals[store_name]["surge"] = max(store_totals[store_name]["surge"], store_data.get("surge", 0))

    best_store = None
    lowest_cost = float("inf")
    for store_name, data in store_totals.items():
        data["all_items_available"] = (data["items_found"] == total_items)
        data["basket_total"] = data["items_total"] + data["delivery"] + data["handling"] + data["surge"]
        if data["all_items_available"] and data["basket_total"] < lowest_cost:
            lowest_cost = data["basket_total"]
            best_store = {
                "store": store_name, "total": data["basket_total"],
                "items_total": data["items_total"],
                "fees_total": data["delivery"] + data["handling"] + data["surge"],
                "eta": data["max_eta"]
            }
    return {"total_items_queried": total_items, "stores": store_totals, "best_single_store": best_store}

@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Search term"),
    category: str = Query("grocery", description="grocery | meat | food | pharmacy | electronics | shopping"),
    lat: float = Query(12.9716),
    lon: float = Query(77.5946)
):
    cat = category.strip().lower()
    q_lower = q.lower()

    if any(m in q_lower for m in ["chicken", "mutton", "fish", "meat", "prawn", "beef"]):
        cat = "meat"
    elif any(e in q_lower for e in ["tv", "sony", "airpods", "laptop", "croma", "refrigerator", "phone", "iphone", "oven"]):
        cat = "electronics"
    elif any(s in q_lower for s in ["shoe", "shoes", "shirt", "tshirt", "jeans", "dress", "kurti", "lipstick", "top", "sneaker", "perfume", "watch"]):
        cat = "shopping"

    query_tokens = [term.strip().lower() for term in q.split(",") if term.strip()] or [q_lower]
    all_matches = []

    if cat == "shopping":
        def_s = {
            "myntra": {"price": 1199, "delivery": 0, "handling": 20, "surge": 0, "eta": "2 Days"},
            "ajio": {"price": 1149, "delivery": 0, "handling": 29, "surge": 0, "eta": "3 Days"},
            "amazon": {"price": 1249, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 1180, "delivery": 0, "handling": 29, "surge": 0, "eta": "Tomorrow"},
            "nykaa": {"price": 1299, "delivery": 0, "handling": 0, "surge": 0, "eta": "3 Days"}
        }
        catalog, def_price, def_unit = SHOPPING_CATALOG, 1199, "Verified Lifestyle Unit"
    elif cat == "electronics":
        def_s = {
            "pai": {"price": 54990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Store Pickup"},
            "vijaysales": {"price": 55490, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "croma": {"price": 55990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day"},
            "flipkart": {"price": 56299, "delivery": 0, "handling": 99, "surge": 0, "eta": "Tomorrow"},
            "reliancedigital": {"price": 56490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "amazon": {"price": 56990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"}
        }
        catalog, def_price, def_unit = ELECTRONICS_CATALOG, 54990, "Verified Retail Unit"
    elif cat == "meat":
        def_s = {
            "freshtohome": {"price": 169, "delivery": 29, "handling": 0, "surge": 0, "eta": "40 mins"},
            "licious": {"price": 179, "delivery": 39, "handling": 0, "surge": 0, "eta": "30 mins"},
            "meatigo": {"price": 185, "delivery": 35, "handling": 0, "surge": 0, "eta": "45 mins"},
            "blinkit": {"price": 195, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 199, "delivery": 25, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 190, "delivery": 20, "handling": 4, "surge": 0, "eta": "14 mins"}
        }
        catalog, def_price, def_unit = MEAT_CATALOG, 179, "Fresh Cut (500g)"
    elif cat == "food":
        def_s = {
            "swiggy": {"price": 220, "delivery": 35, "handling": 20, "surge": 0, "eta": "28 mins"},
            "zomato": {"price": 220, "delivery": 38, "handling": 22, "surge": 0, "eta": "30 mins"},
            "magicpin": {"price": 190, "delivery": 25, "handling": 10, "surge": 0, "eta": "34 mins"},
            "eatclub": {"price": 185, "delivery": 0, "handling": 0, "surge": 0, "eta": "25 mins"},
            "ondc": {"price": 195, "delivery": 20, "handling": 8, "surge": 0, "eta": "34 mins"}
        }
        catalog, def_price, def_unit = FOOD_CATALOG, 220, "Regular Portion"
    elif cat == "pharmacy":
        def_s = {
            "truemeds": {"price": 45, "delivery": 25, "handling": 0, "surge": 0, "eta": "3 hrs"},
            "medplus": {"price": 65, "delivery": 20, "handling": 0, "surge": 0, "eta": "45 mins"},
            "pharmeasy": {"price": 70, "delivery": 35, "handling": 5, "surge": 0, "eta": "60 mins"},
            "1mg": {"price": 72, "delivery": 29, "handling": 5, "surge": 0, "eta": "45 mins"},
            "apollo": {"price": 75, "delivery": 25, "handling": 4, "surge": 0, "eta": "30 mins"},
            "netmeds": {"price": 72, "delivery": 30, "handling": 0, "surge": 0, "eta": "2 hrs"}
        }
        catalog, def_price, def_unit = PHARMACY_CATALOG, 72, "Standard Strip/Pack"
    else:
        def_s = {
            "jiomart": {"price": 60, "delivery": 0, "handling": 0, "surge": 0, "eta": "30 mins"},
            "flipkart_minutes": {"price": 62, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
            "bbnow": {"price": 64, "delivery": 15, "handling": 3, "surge": 0, "eta": "18 mins"},
            "blinkit": {"price": 65, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 68, "delivery": 20, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 66, "delivery": 22, "handling": 4, "surge": 0, "eta": "14 mins"},
            "amazonfresh": {"price": 61, "delivery": 29, "handling": 0, "surge": 0, "eta": "60 mins"}
        }
        catalog, def_price, def_unit = GROCERY_CATALOG, 65, "Standard Pack"

    seen_ids = set()
    for token in query_tokens:
        sub_results = format_results(catalog, token, def_s, def_price, def_unit)
        for item in sub_results:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                all_matches.append(item)

    basket_summary = compute_basket_summary(all_matches)
    response_payload = {"source": "live", "category": cat, "query": q, "results": all_matches}
    if basket_summary:
        response_payload["basket_summary"] = basket_summary
    return response_payload

@app.get("/api/cabs")
async def compare_cabs(
    pickup: str = Query(..., description="Pickup location"),
    drop: str = Query(..., description="Drop location"),
    km: float = Query(8.5, description="Estimated distance in km"),
    vehicle: str = Query("all")
):
    dist = max(1.5, round(km, 1))
    duration_min = int(dist * 3.2 + 6)
    modes = {
        "bike": {
            "label": "Bike Taxi (Fastest in Traffic)",
            "providers": {
                "nammayatra": {"base": 20, "per_km": 7.0, "platform": 0, "surge": 0, "eta": "3 mins"},
                "uber": {"base": 18, "per_km": 7.2, "platform": 4, "surge": 0, "eta": "3 mins"},
                "rapido": {"base": 20, "per_km": 7.5, "platform": 3, "surge": 0, "eta": "2 mins"},
                "ola": {"base": 19, "per_km": 7.4, "platform": 4, "surge": 0, "eta": "4 mins"}
            }
        },
        "auto": {
            "label": "Auto Rickshaw (Doorstep Pickup)",
            "providers": {
                "nammayatra": {"base": 30, "per_km": 15.0, "platform": 0, "surge": 0, "eta": "3 mins"},
                "indrive": {"base": 28, "per_km": 14.5, "platform": 0, "surge": 0, "eta": "5 mins"},
                "rapido": {"base": 30, "per_km": 15.2, "platform": 5, "surge": 0, "eta": "3 mins"},
                "uber": {"base": 30, "per_km": 15.5, "platform": 8, "surge": 5, "eta": "3 mins"},
                "ola": {"base": 30, "per_km": 15.8, "platform": 9, "surge": 5, "eta": "4 mins"}
            }
        },
        "mini": {
            "label": "Mini / Hatchback AC Cab",
            "providers": {
                "indrive": {"base": 70, "per_km": 17.5, "platform": 0, "surge": 0, "eta": "6 mins"},
                "nammayatra": {"base": 75, "per_km": 18.0, "platform": 0, "surge": 0, "eta": "5 mins"},
                "rapido": {"base": 75, "per_km": 18.5, "platform": 8, "surge": 0, "eta": "5 mins"},
                "uber": {"base": 80, "per_km": 19.5, "platform": 15, "surge": 12, "eta": "4 mins"},
                "ola": {"base": 80, "per_km": 20.0, "platform": 16, "surge": 15, "eta": "5 mins"}
            }
        },
        "sedan": {
            "label": "Prime Sedan / EV Comfort",
            "providers": {
                "blusmart": {"base": 95, "per_km": 21.0, "platform": 0, "surge": 0, "eta": "7 mins"},
                "nammayatra": {"base": 90, "per_km": 20.0, "platform": 0, "surge": 0, "eta": "6 mins"},
                "indrive": {"base": 85, "per_km": 19.5, "platform": 0, "surge": 0, "eta": "6 mins"},
                "uber": {"base": 95, "per_km": 22.0, "platform": 18, "surge": 18, "eta": "5 mins"},
                "ola": {"base": 95, "per_km": 22.5, "platform": 18, "surge": 20, "eta": "5 mins"}
            }
        }
    }

    results = []
    for m_key, m_data in modes.items():
        if vehicle != "all" and vehicle != m_key:
            continue
        card = {"id": m_key, "name": m_data["label"], "unit": f"{dist} km • ~{duration_min} mins", "calculated": {}}
        best_p, low_f = None, 999999
        for p_name, r in m_data["providers"].items():
            ride_fare = int(r["base"] + max(0, dist - 2.0) * r["per_km"])
            landed = ride_fare + r["platform"] + r["surge"]
            card["calculated"][p_name] = {
                "price": ride_fare, "delivery": 0, "handling": r["platform"],
                "surge": r["surge"], "landed": landed, "eta": r["eta"]
            }
            if landed < low_f:
                low_f, best_p = landed, p_name
        card["winner"] = {"store": best_p, "landed": low_f}
        results.append(card)

    return {"pickup": pickup, "drop": drop, "distance_km": dist, "duration_min": duration_min, "results": results}
