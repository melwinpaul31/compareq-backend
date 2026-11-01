import time
import math
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CompareQ Multi-Category Backend API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE = {}
CACHE_TTL = 900  # 15 minutes

# 1. QUICK GROCERY CATALOG (7 Aggregators)
GROCERY_CATALOG = {
    "jamun": {
        "name": "Fresh Jamun / Black Plum (250g)", "unit": "250g pack",
        "stores": {
            "blinkit": {"price": 89, "delivery": 16, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 95, "delivery": 20, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 92, "delivery": 25, "handling": 4, "surge": 0, "eta": "14 mins"},
            "flipkart": {"price": 85, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
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
            "flipkart": {"price": 23, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
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
            "flipkart": {"price": 252, "delivery": 0, "handling": 4, "surge": 0, "eta": "14 mins"},
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
            "flipkart": {"price": 86, "delivery": 18, "handling": 2, "surge": 0, "eta": "14 mins"},
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
            "flipkart": {"price": 46, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
            "bbnow": {"price": 49, "delivery": 15, "handling": 3, "surge": 0, "eta": "18 mins"},
            "jiomart": {"price": 45, "delivery": 0, "handling": 0, "surge": 0, "eta": "30 mins"},
            "amazonfresh": {"price": 47, "delivery": 29, "handling": 0, "surge": 0, "eta": "60 mins"}
        }
    }
}

# 2. FOOD DELIVERY CATALOG (5 Aggregators)
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

# 3. PHARMACY CATALOG (6 Aggregators)
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

# 4. E-COMMERCE & ELECTRONICS CATALOG (7 Aggregators)
SHOPPING_CATALOG = {
    "airpods": {
        "name": "Apple AirPods Pro (2nd Gen, USB-C)", "unit": "1 Unit",
        "stores": {
            "amazon": {"price": 19990, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 19499, "delivery": 0, "handling": 49, "surge": 0, "eta": "Tomorrow"},
            "croma": {"price": 20490, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day"},
            "reliancedigital": {"price": 19999, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "vijaysales": {"price": 19790, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "myntra": {"price": 20990, "delivery": 0, "handling": 20, "surge": 0, "eta": "2 Days"},
            "ajio": {"price": 21490, "delivery": 0, "handling": 29, "surge": 0, "eta": "3 Days"}
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
    return {"status": "ok", "app": "CompareQ Multi-Category API", "version": "2.0.0"}

@app.get("/api/compare")
async def compare_items(
    q: str = Query(..., description="Search term"),
    category: str = Query("grocery", description="grocery | food | pharmacy | shopping"),
    lat: float = Query(12.9716),
    lon: float = Query(77.5946)
):
    q_clean = q.strip().lower()
    cat = category.strip().lower()
    cache_key = f"{cat}_{q_clean}_{lat:.2f}_{lon:.2f}"
    if cache_key in CACHE:
        ts, data = CACHE[cache_key]
        if time.time() - ts < CACHE_TTL:
            return {"source": "cache", "category": cat, "query": q, "results": data}

    if cat == "food":
        def_s = {
            "swiggy": {"price": 220, "delivery": 35, "handling": 20, "surge": 0, "eta": "28 mins"},
            "zomato": {"price": 220, "delivery": 38, "handling": 22, "surge": 0, "eta": "30 mins"},
            "magicpin": {"price": 190, "delivery": 25, "handling": 10, "surge": 0, "eta": "35 mins"},
            "eatclub": {"price": 185, "delivery": 0, "handling": 0, "surge": 0, "eta": "25 mins"},
            "ondc": {"price": 195, "delivery": 20, "handling": 8, "surge": 0, "eta": "34 mins"}
        }
        res = format_results(FOOD_CATALOG, q_clean, def_s, 220, "Regular Portion")
    elif cat == "pharmacy":
        def_s = {
            "1mg": {"price": 85, "delivery": 29, "handling": 5, "surge": 0, "eta": "45 mins"},
            "apollo": {"price": 88, "delivery": 25, "handling": 4, "surge": 0, "eta": "30 mins"},
            "pharmeasy": {"price": 82, "delivery": 35, "handling": 5, "surge": 0, "eta": "60 mins"},
            "netmeds": {"price": 84, "delivery": 30, "handling": 0, "surge": 0, "eta": "2 hrs"},
            "truemeds": {"price": 55, "delivery": 25, "handling": 0, "surge": 0, "eta": "3 hrs"},
            "medplus": {"price": 80, "delivery": 20, "handling": 0, "surge": 0, "eta": "45 mins"}
        }
        res = format_results(PHARMACY_CATALOG, q_clean, def_s, 85, "Standard Strip/Pack")
    elif cat == "shopping":
        def_s = {
            "amazon": {"price": 1499, "delivery": 0, "handling": 0, "surge": 0, "eta": "Tomorrow"},
            "flipkart": {"price": 1449, "delivery": 0, "handling": 29, "surge": 0, "eta": "Tomorrow"},
            "croma": {"price": 1549, "delivery": 0, "handling": 0, "surge": 0, "eta": "Same Day"},
            "reliancedigital": {"price": 1499, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "vijaysales": {"price": 1480, "delivery": 0, "handling": 0, "surge": 0, "eta": "2 Days"},
            "myntra": {"price": 1520, "delivery": 0, "handling": 20, "surge": 0, "eta": "2 Days"},
            "ajio": {"price": 1490, "delivery": 0, "handling": 29, "surge": 0, "eta": "3 Days"}
        }
        res = format_results(SHOPPING_CATALOG, q_clean, def_s, 1499, "Verified Retail Unit")
    else:
        def_s = {
            "blinkit": {"price": 65, "delivery": 15, "handling": 4, "surge": 0, "eta": "11 mins"},
            "zepto": {"price": 68, "delivery": 20, "handling": 4, "surge": 0, "eta": "10 mins"},
            "instamart": {"price": 66, "delivery": 22, "handling": 4, "surge": 0, "eta": "14 mins"},
            "flipkart": {"price": 62, "delivery": 18, "handling": 2, "surge": 0, "eta": "15 mins"},
            "bbnow": {"price": 64, "delivery": 15, "handling": 3, "surge": 0, "eta": "18 mins"},
            "jiomart": {"price": 60, "delivery": 0, "handling": 0, "surge": 0, "eta": "30 mins"},
            "amazonfresh": {"price": 61, "delivery": 29, "handling": 0, "surge": 0, "eta": "60 mins"}
        }
        res = format_results(GROCERY_CATALOG, q_clean, def_s, 65, "Standard Pack")

    CACHE[cache_key] = (time.time(), res)
    return {"source": "live", "category": cat, "query": q, "results": res}

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
                "nammayatra": {"base": 75, "per_km": 18.0, "platform": 0, "surge": 0, "eta": "5 mins"},
                "indrive": {"base": 70, "per_km": 17.5, "platform": 0, "surge": 0, "eta": "6 mins"},
                "uber": {"base": 80, "per_km": 19.5, "platform": 15, "surge": 12, "eta": "4 mins"},
                "ola": {"base": 80, "per_km": 20.0, "platform": 16, "surge": 15, "eta": "5 mins"},
                "rapido": {"base": 75, "per_km": 18.5, "platform": 8, "surge": 0, "eta": "5 mins"}
            }
        },
        "sedan": {
            "label": "Prime Sedan / EV Comfort",
            "providers": {
                "blusmart": {"base": 95, "per_km": 21.0, "platform": 0, "surge": 0, "eta": "7 mins"},
                "nammayatra": {"base": 90, "per_km": 20.0, "platform": 0, "surge": 0, "eta": "6 mins"},
                "uber": {"base": 95, "per_km": 22.0, "platform": 18, "surge": 18, "eta": "5 mins"},
                "ola": {"base": 95, "per_km": 22.5, "platform": 18, "surge": 20, "eta": "5 mins"},
                "indrive": {"base": 85, "per_km": 19.5, "platform": 0, "surge": 0, "eta": "6 mins"}
            }
        },
        "suv": {
            "label": "XL / 6-Seater SUV (Innova / Ertiga)",
            "providers": {
                "nammayatra": {"base": 130, "per_km": 26.0, "platform": 0, "surge": 0, "eta": "8 mins"},
                "uber": {"base": 140, "per_km": 28.5, "platform": 25, "surge": 25, "eta": "7 mins"},
                "ola": {"base": 140, "per_km": 29.0, "platform": 25, "surge": 30, "eta": "8 mins"},
                "blusmart": {"base": 145, "per_km": 27.5, "platform": 0, "surge": 0, "eta": "9 mins"}
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
