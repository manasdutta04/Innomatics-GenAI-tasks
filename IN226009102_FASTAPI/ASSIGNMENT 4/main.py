"""
FastAPI — Assignment 4: Cart System Practice (Day 5)
=====================================================
Endpoints:
  POST   /cart/add            — add item to cart (query params: product_id, quantity)
  GET    /cart                — view current cart
  DELETE /cart/{product_id}   — remove item from cart
  POST   /cart/checkout       — checkout and place orders
  GET    /orders              — list all placed orders

Test via Swagger UI → http://127.0.0.1:8000/docs
Run with:  uvicorn main:app --reload
"""

from typing import List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# ─────────────────────────────────────────────
# App instance
# ─────────────────────────────────────────────
app = FastAPI(
    title="Cart System API",
    description="FastAPI Assignment 4 — Shopping Cart Practice",
    version="1.0.0",
)

# ─────────────────────────────────────────────
# In-memory "database"
# ─────────────────────────────────────────────

# Product catalogue  (resets on restart — by design)
PRODUCTS = {
    1: {"product_id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    2: {"product_id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    3: {"product_id": 3, "name": "USB Hub", "price": 349, "in_stock": False},
    4: {"product_id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
}

# Shopping cart — list of cart-item dicts
cart: List[dict] = []

# Orders — list of order dicts
orders: List[dict] = []

# Auto-incrementing order counter
order_counter = {"value": 0}


# ─────────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────────


class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────


def calculate_subtotal(price: int, quantity: int) -> int:
    """Return integer subtotal (price × quantity)."""
    return price * quantity


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────


# ── Root ─────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    """Health-check / welcome endpoint."""
    return {
        "message": "Cart System API is running 🛒",
        "docs": "http://127.0.0.1:8000/docs",
    }


# ── POST /cart/add ────────────────────────────
@app.post("/cart/add", tags=["Cart"])
def add_to_cart(
    product_id: int = Query(..., description="ID of the product to add"),
    quantity: int = Query(1, ge=1, description="Number of units to add"),
):
    """
    Add a product to the shopping cart.

    - Returns **"Added to cart"** for a new product.
    - Returns **"Cart updated"** when the same product already exists in the cart
      (quantity is incremented, not duplicated).
    - Raises **404** if product_id does not exist.
    - Raises **400** if the product is out of stock.
    """
    # 1. Product existence check
    product = PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id={product_id} not found",
        )

    # 2. Stock check
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock",
        )

    # 3. Duplicate check — update if already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_subtotal(product["price"], item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    # 4. New item — append to cart
    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_subtotal(product["price"], quantity),
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}


# ── GET /cart ─────────────────────────────────
@app.get("/cart", tags=["Cart"])
def view_cart():
    """
    View the current cart contents.

    - Returns all items with their subtotals.
    - **item_count** = number of unique products (not total quantity).
    - **grand_total** = sum of all subtotals.
    - Returns *"Cart is empty"* when no items have been added.
    """
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total,
    }


# ── DELETE /cart/{product_id} ─────────────────
@app.delete("/cart/{product_id}", tags=["Cart"])
def remove_from_cart(product_id: int):
    """
    Remove a specific product from the cart by its product_id.

    - Raises **404** if the product is not currently in the cart.
    """
    for index, item in enumerate(cart):
        if item["product_id"] == product_id:
            removed = cart.pop(index)
            return {
                "message": f"{removed['product_name']} removed from cart",
                "removed_item": removed,
            }

    raise HTTPException(
        status_code=404,
        detail=f"Product with id={product_id} is not in the cart",
    )


# ── POST /cart/checkout ───────────────────────
@app.post("/cart/checkout", tags=["Cart"])
def checkout(request: CheckoutRequest):
    """
    Checkout — place an order for every item currently in the cart.

    - Raises **400** if the cart is empty.
    - Creates **one order record per cart item**.
    - Clears the cart after a successful checkout.
    - Returns the list of placed orders and the grand total.
    """
    # Empty-cart guard
    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first",
        )

    grand_total = sum(item["subtotal"] for item in cart)
    placed_orders = []

    for item in cart:
        order_counter["value"] += 1
        order = {
            "order_id": order_counter["value"],
            "customer_name": request.customer_name,
            "delivery_address": request.delivery_address,
            "product": item["product_name"],
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"],
            "total_price": item["subtotal"],
        }
        orders.append(order)
        placed_orders.append(order)

    # Clear cart
    cart.clear()

    return {
        "message": "Order placed successfully! 🎉",
        "customer_name": request.customer_name,
        "orders_placed": placed_orders,
        "grand_total": grand_total,
    }


# ── GET /orders ───────────────────────────────
@app.get("/orders", tags=["Orders"])
def get_orders():
    """
    Retrieve all orders placed so far across all checkout sessions.

    - **total_orders** = number of individual order records.
    - Orders persist until the server is restarted.
    """
    if not orders:
        return {"message": "No orders placed yet", "orders": [], "total_orders": 0}

    return {
        "orders": orders,
        "total_orders": len(orders),
    }
