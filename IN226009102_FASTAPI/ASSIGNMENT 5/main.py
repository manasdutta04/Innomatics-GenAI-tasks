from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

# ── Shared Data ────────────────────────────────────────────────────────────────

products = [
    {"id": 1, "name": "Wireless Mouse",   "price": 25.99, "category": "Electronics"},
    {"id": 2, "name": "Mechanical Keyboard", "price": 89.99, "category": "Electronics"},
    {"id": 3, "name": "Notebook",          "price":  4.99, "category": "Stationery"},
    {"id": 4, "name": "Ballpoint Pen",     "price":  1.49, "category": "Stationery"},
]

orders = []  # populated via POST /orders


# ── Q1 — Search Products by Keyword (case-insensitive) ────────────────────────

@app.get("/products/search")
def search_products(keyword: str = Query(...)):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for keyword '{keyword}'"}
    return {"keyword": keyword, "count": len(results), "products": results}


# ── Q2 — Sort Products by Field ───────────────────────────────────────────────

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price"),
    order:   str = Query("asc"),
):
    allowed = ["price", "name"]
    if sort_by not in allowed:
        return {"error": f"Invalid sort_by '{sort_by}'. Allowed: {allowed}"}

    sorted_products = sorted(
        products,
        key=lambda p: p[sort_by],
        reverse=(order == "desc"),
    )
    return {"sort_by": sort_by, "order": order, "products": sorted_products}


# ── Q3 — Paginate the Product List ───────────────────────────────────────────

@app.get("/products/page")
def get_products_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=20),
):
    total = len(products)
    start = (page - 1) * limit
    paged = products[start: start + limit]
    return {
        "page":        page,
        "limit":       limit,
        "total":       total,
        "total_pages": -(-total // limit),   # ceiling division
        "products":    paged,
    }


# ── Q4 — Search Orders by Customer Name ──────────────────────────────────────

@app.post("/orders")
def create_order(order: dict):
    order["id"] = len(orders) + 1
    orders.append(order)
    return {"message": "Order placed", "order": order}


@app.get("/orders/search")
def search_orders(customer: str = Query(...)):
    results = [o for o in orders if customer.lower() in o.get("customer", "").lower()]
    if not results:
        return {"message": f"No orders found for customer '{customer}'"}
    return {"customer": customer, "count": len(results), "orders": results}


# ── Q5 — Sort Products by Category + Price ───────────────────────────────────

@app.get("/products/sort-by-category")
def sort_by_category():
    category_order = {"Electronics": 0, "Stationery": 1}
    sorted_products = sorted(
        products,
        key=lambda p: (category_order.get(p["category"], 99), p["price"]),
    )
    return {"products": sorted_products}


# ── Q6 — Browse Products (Search + Sort + Paginate combined) ─────────────────

@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = Query(None),
    sort_by: str           = Query("price"),
    order:   str           = Query("asc"),
    page:    int           = Query(1, ge=1),
    limit:   int           = Query(4, ge=1, le=20),
):
    # Step 1 — Filter
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # Step 2 — Sort
    if sort_by in ["price", "name"]:
        result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))

    # Step 3 — Paginate
    total = len(result)
    start = (page - 1) * limit
    paged = result[start: start + limit]

    return {
        "keyword":     keyword,
        "sort_by":     sort_by,
        "order":       order,
        "page":        page,
        "limit":       limit,
        "total_found": total,
        "total_pages": -(-total // limit),
        "products":    paged,
    }


# ── BONUS — Paginate Orders List ──────────────────────────────────────────────

@app.get("/orders/page")
def get_orders_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    start = (page - 1) * limit
    return {
        "page":        page,
        "limit":       limit,
        "total":       len(orders),
        "total_pages": -(-len(orders) // limit),
        "orders":      orders[start: start + limit],
    }