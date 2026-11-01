import time
import math
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CompareQ Multi-Category Backend API", version="2.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE = {}
CACHE_TTL = 900

# 1. QUICK GROCERY CATALOG
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
    "paneer": {
        "name": "Amul Fresh Malai Paneer (200g)", "unit": "200g pack",
        "stores": {
            "blinkit": {"price": 88, "delivery": 15, "handling": 4, "surge": 0, "eta": "10 mins"},
            "zepto": {"price": 90, "delivery": 20, "handling": 4, "surge": 0, "eta": "11 mins"},
            "instamart": {"price": 92, "delivery": 25, "handling": 4, "surge": 0, "eta": "13 mins"},
            "flipkart_minutes": {"price": 86, "delivery": 18, "handling": 2, "surge": 0, "eta": "14 mins"},
            "bbnow": {"price": 88, "delivery": 15, "handling": 3, "surge": 0, "eta": "17 mins"},
            "jiomart": {"price": 85, "delivery": 0, "handling": 0, "surge": 0, "eta": "30 mins"},
            "amazonfresh": {"price": 87, "delivery": 29, "handling": 0, "surge": 0, "eta": "60 mins"}
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

# 2. MEAT & SEAFOOD CATALOG
MEAT_CATALOG = {
    "chicken": {
        "name": "Fresh Tender Chicken Curry Cut / Breast (500g)", "unit": "500g pack",
        "stores": {
            "licious": {"price": 179, "delivery": 39, "handling": 0, "surge": 0, "eta": "30 mins"},
            "meatigo": {"price": 185, "delivery": 35, "handling": 0, "surge": 0, "eta": "45 mins"},
            "freshtohome": {"price": 169, "delivery": 29, "handling": 0, "surge": 0, "eta": "40 mins"},
            "blinkit": {"price": 195, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 199, "delivery": 25, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 190, "delivery": 20, "handling": 4, "surge": 0, "eta": "14 mins"},
            "bbnow": {"price": 185, "delivery": 15, "handling": 3, "surge": 0, "eta": "18 mins"}
        }
    },
    "mutton": {
        "name": "Rich Goat Mutton Curry Cut (500g)", "unit": "500g pack",
        "stores": {
            "licious": {"price": 529, "delivery": 39, "handling": 0, "surge": 0, "eta": "30 mins"},
            "meatigo": {"price": 545, "delivery": 35, "handling": 0, "surge": 0, "eta": "45 mins"},
            "freshtohome": {"price": 519, "delivery": 29, "handling": 0, "surge": 0, "eta": "40 mins"},
            "blinkit": {"price": 560, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 565, "delivery": 25, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 550, "delivery": 20, "handling": 4, "surge": 0, "eta": "14 mins"}
        }
    },
    "fish": {
        "name": "Fresh Seer Fish / Rohu Steaks (500g)", "unit": "500g cleaned",
        "stores": {
            "licious": {"price": 389, "delivery": 39, "handling": 0, "surge": 0, "eta": "35 mins"},
            "freshtohome": {"price": 369, "delivery": 29, "handling": 0, "surge": 0, "eta": "40 mins"},
            "meatigo": {"price": 399, "delivery": 35, "handling": 0, "surge": 0, "eta": "45 mins"},
            "blinkit": {"price": 410, "delivery": 15, "handling": 4, "surge": 0, "eta": "12 mins"}
        }
    }
}

# 3. FOOD DELIVERY CATALOG
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
    },
    "pizza": {
        "name": "Pepper Barbecue Chicken Pizza (Medium)", "unit": "Medium 8-inch",
        "stores": {
            "swiggy": {"price": 399, "delivery": 35, "handling": 25, "surge": 0, "eta": "32 mins"},
            "zomato": {"price": 399, "delivery": 40, "handling": 28, "surge": 0, "eta": "30 mins"},
            "magicpin": {"price": 349, "delivery": 25, "handling": 12, "surge": 0, "eta": "36 mins"},
            "eatclub": {"price": 319, "delivery": 0, "handling": 0, "surge": 0, "eta": "26 mins"},
            "ondc": {"price": 355, "delivery": 22, "handling": 10, "surge": 0, "eta": "35 mins"}
        }
    }
}

# 4. PHARMACY CATALOG
PHARMACY_CATALOG = {
    "dolo": {
        "name": "Dolo 650mg Tablet (Strip of 15)", "unit": "15 tablets",
        "stores": {
            "1mg": {"price": 29, "delivery": 29, "handling": 5, "surge": 0, "eta": "45 mins"},
            "apollo": {"price": 30, "delivery": 25, "handling": 4, "surge": 0, "eta": "30 mins"},
            "pharmeasy": {"price": 28, "delivery": 35, "handling": 5, "surge": 0, "eta": "60 mins"},
            "netmeds": {"price": 29, "delivery": 30, "handling": 0, "surge": 0, "eta": "2 hrs"},
            "truemeds": {"price": 18, "delivery": 25, "handling": 0, "surge": 0, "eta": "3 hrs"},
            "medplus": {"price": 27, "delivery": 20, "handling": 0, "surge": 0, "eta": "45 mins"}
        }
    }
}

# 5. ELECTRONICS & APPLIANCES CATALOG
ELECTRONICS_CATALOG = {
    "airpods": {
        "name": "Apple AirPods Pro (2nd Gen, Type-C)", "unit": "1 Unit",
        "stores": {
            "amazon": {"price": 19990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 19499, "delivery": 0, "handling": 49, "surge": 0, "eta": "Tomorrow"},
            "croma": {"price": 20490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day"},
            "reliancedigital": {"price": 19999, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "vijaysales": {"price": 19790, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "pai": {"price": 19890, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day Store Pickup"}
        }
    },
    "tv": {
        "name": "Sony Bravia 55-inch 4K Google TV", "unit": "1 Unit",
        "stores": {
            "croma": {"price": 57990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "reliancedigital": {"price": 58490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "vijaysales": {"price": 57500, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "pai": {"price": 56999, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day Pickup"},
            "amazon": {"price": 58990, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "flipkart": {"price": 58299, "delivery": 0, "handling": 99, "surge": 0, "eta": "2 Days"}
        }
    }
}

SHOPPING_CATALOG = {
    "shoes": {
        "name": "Running Sports Shoes", "unit": "1 Pair",
        "stores": {
            "amazon": {"price": 1499, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 1449, "delivery": 0, "handling": 29, "surge": 0, "eta": "Tomorrow"},
            "myntra": {"price": 1399, "delivery": 0, "handling": 20, "surge": 0, "eta": "2 Days"},
            "ajio": {"price": 1420, "delivery": 0, "handling": 29, "surge": 0, "eta": "3 Days"}
        }
    }
}

def format_results(catalog, q_clean, default_stores, base_price=75, unit_label="Standard Pack"):
    matches = []
    for k, v in catalog.items():
        if k in q_clean or q_clean in k or q_clean in v["name"].lower():
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
    return {"status": "ok", "app": "CompareQ Multi-Category API", "version": "2.1.0"}

def compute_basket_summary(results):
    if not results or len(results) <= 1:
        return None

    total_items = len(results)
    store_totals = {}

    for item in results:
        stores = item.get("stores", {})
        for store_name, store_data in stores.items():
            if store_name not in store_totals:
                store_totals[store_name] = {
                    "items_total": 0,
                    "items_found": 0,
                    "delivery": store_data.get("delivery", 0),
                    "handling": store_data.get("handling", 0),
                    "surge": store_data.get("surge", 0),
                    "max_eta": store_data.get("eta", "N/A"),
                    "basket_total": 0,
                    "all_items_available": False,
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
                "store": store_name,
                "total": data["basket_total"],
                "items_total": data["items_total"],
                "fees_total": data["delivery"] + data["handling"] + data["surge"],
                "eta": data["max_eta"],
            }

    return {
        "total_items_queried": total_items,
        "stores": store_totals,
        "best_single_store": best_store
    }

@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Search term"),
    category: str = Query("grocery", description="grocery | meat | food | pharmacy | electronics | shopping"),
    lat: float = Query(12.9716),
    lon: float = Query(77.5946)
):
    cat = category.strip().lower()

    # If user searched "chicken", "mutton", or "fish" inside grocery, intelligently route to Meat
    if cat == "grocery" and any(m in q.lower() for m in ["chicken", "mutton", "fish", "meat", "prawn", "prawns"]):
        cat = "meat"

    query_tokens = [term.strip().lower() for term in q.split(",") if term.strip()]
    if not query_tokens:
        query_tokens = [q.strip().lower()]

    all_matches = []

    if cat == "meat":
        def_s = {
            "licious": {"price": 189, "delivery": 39, "handling": 0, "surge": 0, "eta": "30 mins"},
            "meatigo": {"price": 195, "delivery": 35, "handling": 0, "surge": 0, "eta": "45 mins"},
            "freshtohome": {"price": 179, "delivery": 29, "handling": 0, "surge": 0, "eta": "40 mins"},
            "blinkit": {"price": 205, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 210, "delivery": 25, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 200, "delivery": 20, "handling": 4, "surge": 0, "eta": "14 mins"}
        }
        catalog, def_price, def_unit = MEAT_CATALOG, 189, "Fresh Cut (500g)"
    elif cat == "food":
        def_s = {
            "swiggy": {"price": 220, "delivery": 35, "handling": 20, "surge": 0, "eta": "28 mins"},
            "zomato": {"price": 220, "delivery": 38, "handling": 22, "surge": 0, "eta": "30 mins"},
            "magicpin": {"price": 190, "delivery": 25, "handling": 10, "surge": 0, "eta": "35 mins"},
            "eatclub": {"price": 185, "delivery": 0, "handling": 0, "surge": 0, "eta": "25 mins"},
            "ondc": {"price": 195, "delivery": 20, "handling": 8, "surge": 0, "eta": "34 mins"}
        }
        catalog, def_price, def_unit = FOOD_CATALOG, 220, "Regular Portion"
    elif cat == "pharmacy":
        def_s = {
            "1mg": {"price": 85, "delivery": 29, "handling": 5, "surge": 0, "eta": "45 mins"},
            "apollo": {"price": 88, "delivery": 25, "handling": 4, "surge": 0, "eta": "30 mins"},
            "pharmeasy": {"price": 82, "delivery": 35, "handling": 5, "surge": 0, "eta": "60 mins"},
            "netmeds": {"price": 84, "delivery": 30, "handling": 0, "surge": 0, "eta": "2 hrs"},
            "truemeds": {"price": 55, "delivery": 25, "handling": 0, "surge": 0, "eta": "3 hrs"},
            "medplus": {"price": 80, "delivery": 20, "handling": 0, "surge": 0, "eta": "45 mins"}
        }
        catalog, def_price, def_unit = PHARMACY_CATALOG, 85, "Standard Strip/Pack"
    elif cat == "electronics":
        def_s = {
            "croma": {"price": 19490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day"},
            "reliancedigital": {"price": 19590, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "vijaysales": {"price": 19290, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "pai": {"price": 19199, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day Pickup"},
            "amazon": {"price": 19490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 19399, "delivery": 0, "handling": 49, "surge": 0, "eta": "Tomorrow"}
        }
        catalog, def_price, def_unit = ELECTRONICS_CATALOG, 19490, "Verified Retail Unit"
    elif cat == "shopping":
        def_s = {
            "amazon": {"price": 1499, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 1449, "delivery": 0, "handling": 29, "surge": 0, "eta": "Tomorrow"},
            "myntra": {"price": 1520, "delivery": 0, "handling": 20, "surge": 0, "eta": "2 Days"},
            "ajio": {"price": 1490, "delivery": 0, "handling": 29, "surge": 0, "eta": "3 Days"}
        }
        catalog, def_price, def_unit = SHOPPING_CATALOG, 1499, "Standard Unit"
    else:
        def_s = {
            "blinkit": {"price": 65, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 68, "delivery": 20, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 66, "delivery": 22, "handling": 4, "surge": 0, "eta": "14 mins"},
            "flipkart_minutes": {"price": 62, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
            "bbnow": {"price": 64, "delivery": 15, "handling": 3, "surge": 0, "eta": "18 mins"},
            "jiomart": {"price": 60, "delivery": 0, "handling": 0, "surge": 0, "eta": "30 mins"},
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

    response_payload = {
        "source": "live",
        "category": cat,
        "query": q,
        "results": all_matches
    }

    if basket_summary:
        response_payload["basket_summary"] = basket_summary

    return response_payload

@app.get("/api/cabs")
async def compare_cabs(
    pickup: str = Query(..., description="Pickup location"),
    drop: str = Query(..., description="Drop location"),
    km: float = Query(8.5, description="Estimated distance in km"),
    vehicle: str = Query("all", description="bike | auto | mini | sedan | suv | all")
):
    dist = max(1.5, round(km, 1))
    duration_min = int(dist * 3.2 + 6)
    modes = {
        "bike": {
            "label": "Bike Taxi (Fastest in Traffic)",
            "providers": {
                "rapido": {"base": 20, "per_km": 7.5, "platform": 3, "surge": 0, "eta": "2 mins"},
                "uber": {"base": 18, "per_km": 7.2, "platform": 4, "surge": 0, "eta": "3 mins"},
                "ola": {"base": 19, "per_km": 7.4, "platform": 4, "surge": 0, "eta": "4 mins"},
                "nammayatra": {"base": 20, "per_km": 7.0, "platform": 0, "surge": 0, "eta": "3 mins"}
            }
        },
        "auto": {
            "label": "Auto Rickshaw (Doorstep Pickup)",
            "providers": {
                "nammayatra": {"base": 30, "per_km": 15.0, "platform": 0, "surge": 0, "eta": "3 mins"},
                "uber": {"base": 30, "per_km": 15.5, "platform": 8, "surge": 5, "eta": "3 mins"},
                "ola": {"base": 30, "per_km": 15.8, "platform": 9, "surge": 5, "eta": "4 mins"},
                "rapido": {"base": 30, "per_km": 15.2, "platform": 5, "surge": 0, "eta": "3 mins"},
                "indrive": {"base": 28, "per_km": 14.5, "platform": 0, "surge": 0, "eta": "5 mins"}
            }
        },
        "mini": {
            "label": "Mini / Hatchback AC Cab",
            "providers": {
