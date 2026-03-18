from typing import Any, Literal, Optional

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

app = FastAPI(title="QuickBite Food Delivery API", version="1.0.0")

menu = [
    {"id": 1, "name": "Margherita Pizza", "price": 249, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Farmhouse Pizza", "price": 349, "category": "Pizza", "is_available": True},
    {"id": 3, "name": "Veg Burger", "price": 159, "category": "Burger", "is_available": True},
    {"id": 4, "name": "Cheese Burger", "price": 199, "category": "Burger", "is_available": False},
    {"id": 5, "name": "Cold Coffee", "price": 129, "category": "Drink", "is_available": True},
    {"id": 6, "name": "Chocolate Brownie", "price": 149, "category": "Dessert", "is_available": True},
]

orders: list[dict[str, Any]] = []
order_counter = 1

cart: list[dict[str, Any]] = []
DELIVERY_CHARGE = 30


class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=20)
    delivery_address: str = Field(..., min_length=10)
    order_type: Literal["delivery", "pickup"] = "delivery"


class NewMenuItem(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    is_available: bool = True


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


def find_menu_item(item_id: int) -> Optional[dict[str, Any]]:
    for item in menu:
        if item["id"] == item_id:
            return item
    return None


def calculate_bill(price: int, quantity: int, order_type: str = "delivery") -> int:
    total = price * quantity
    if order_type == "delivery":
        total += DELIVERY_CHARGE
    return total


def filter_menu_logic(
    items: list[dict[str, Any]],
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None,
) -> list[dict[str, Any]]:
    filtered = []

    for item in items:
        if category is not None and item["category"].lower() != category.lower():
            continue
        if max_price is not None and item["price"] > max_price:
            continue
        if is_available is not None and item["is_available"] != is_available:
            continue
        filtered.append(item)

    return filtered


def _create_order_record(
    customer_name: str,
    delivery_address: str,
    item: dict[str, Any],
    quantity: int,
    order_type: str,
) -> dict[str, Any]:
    global order_counter

    order_total = calculate_bill(item["price"], quantity, order_type)
    new_order = {
        "order_id": order_counter,
        "customer_name": customer_name,
        "item_id": item["id"],
        "item_name": item["name"],
        "quantity": quantity,
        "order_type": order_type,
        "delivery_address": delivery_address,
        "total_price": order_total,
        "status": "placed",
    }
    orders.append(new_order)
    order_counter += 1
    return new_order


@app.get("/")
def home() -> dict[str, str]:
    return {"message": "Welcome to QuickBite Food Delivery"}


@app.get("/menu")
def get_menu() -> dict[str, Any]:
    return {"total": len(menu), "items": menu}


@app.get("/menu/summary")
def get_menu_summary() -> dict[str, Any]:
    available_count = sum(1 for item in menu if item["is_available"])
    categories = sorted({item["category"] for item in menu})
    return {
        "total_menu_items": len(menu),
        "available_items": available_count,
        "unavailable_items": len(menu) - available_count,
        "categories": categories,
    }


@app.get("/menu/filter")
def filter_menu(
    category: Optional[str] = Query(default=None),
    max_price: Optional[int] = Query(default=None, gt=0),
    is_available: Optional[bool] = Query(default=None),
) -> dict[str, Any]:
    filtered_items = filter_menu_logic(menu, category, max_price, is_available)
    return {"count": len(filtered_items), "items": filtered_items}


@app.get("/menu/search")
def search_menu(keyword: str = Query(..., min_length=1)) -> dict[str, Any]:
    kw = keyword.lower().strip()
    matches = [
        item
        for item in menu
        if kw in item["name"].lower() or kw in item["category"].lower()
    ]

    if not matches:
        return {
            "message": "No menu items matched your search keyword.",
            "total_found": 0,
            "items": [],
        }

    return {"keyword": keyword, "total_found": len(matches), "items": matches}


@app.get("/menu/sort")
def sort_menu(
    sort_by: str = Query(default="price"),
    order: str = Query(default="asc"),
) -> dict[str, Any]:
    allowed_sort_fields = {"price", "name", "category"}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be one of: price, name, category",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    sorted_menu = sorted(menu, key=lambda item: item[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "items": sorted_menu}


@app.get("/menu/page")
def menu_pagination(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=3, ge=1, le=10),
) -> dict[str, Any]:
    total = len(menu)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    items = menu[start : start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": items,
    }


@app.get("/menu/browse")
def browse_menu(
    keyword: Optional[str] = Query(default=None),
    sort_by: str = Query(default="price"),
    order: str = Query(default="asc"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=4, ge=1, le=10),
) -> dict[str, Any]:
    filtered = menu

    if keyword is not None:
        kw = keyword.lower().strip()
        filtered = [
            item
            for item in filtered
            if kw in item["name"].lower() or kw in item["category"].lower()
        ]

    allowed_sort_fields = {"price", "name", "category"}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be one of: price, name, category",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    sorted_filtered = sorted(
        filtered,
        key=lambda item: item[sort_by],
        reverse=(order == "desc"),
    )

    total = len(sorted_filtered)
    total_pages = (total + limit - 1) // limit if total > 0 else 0

    start = (page - 1) * limit
    items = sorted_filtered[start : start + limit]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": items,
    }


@app.post("/menu")
def create_menu_item(payload: NewMenuItem, response: Response) -> dict[str, Any]:
    for item in menu:
        if item["name"].lower() == payload.name.lower():
            raise HTTPException(status_code=400, detail="Menu item with this name already exists")

    new_id = max(item["id"] for item in menu) + 1 if menu else 1
    new_item = {
        "id": new_id,
        "name": payload.name,
        "price": payload.price,
        "category": payload.category,
        "is_available": payload.is_available,
    }
    menu.append(new_item)

    response.status_code = 201
    return new_item


@app.get("/menu/{item_id}")
def get_menu_item_by_id(item_id: int) -> dict[str, Any]:
    item = find_menu_item(item_id)
    if item is None:
        return {"error": "Item not found"}
    return item


@app.put("/menu/{item_id}")
def update_menu_item(
    item_id: int,
    price: Optional[int] = Query(default=None, gt=0),
    is_available: Optional[bool] = Query(default=None),
) -> dict[str, Any]:
    item = find_menu_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if price is not None:
        item["price"] = price
    if is_available is not None:
        item["is_available"] = is_available

    return {"message": "Menu item updated", "item": item}


@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int) -> dict[str, str]:
    item = find_menu_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    menu.remove(item)
    return {"message": f"Deleted menu item: {item['name']}"}


@app.get("/orders")
def get_orders() -> dict[str, Any]:
    return {"total_orders": len(orders), "orders": orders}


@app.get("/orders/search")
def search_orders(customer_name: str = Query(..., min_length=2)) -> dict[str, Any]:
    key = customer_name.lower().strip()
    matches = [order for order in orders if key in order["customer_name"].lower()]
    return {"customer_name": customer_name, "total_found": len(matches), "orders": matches}


@app.get("/orders/sort")
def sort_orders(order: str = Query(default="asc")) -> dict[str, Any]:
    if order not in {"asc", "desc"}:
        raise HTTPException(status_code=400, detail="order must be 'asc' or 'desc'")

    sorted_orders = sorted(
        orders,
        key=lambda placed_order: placed_order["total_price"],
        reverse=(order == "desc"),
    )
    return {"order": order, "orders": sorted_orders}


@app.post("/orders")
def place_order(payload: OrderRequest, response: Response) -> dict[str, Any]:
    item = find_menu_item(payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item["is_available"]:
        raise HTTPException(status_code=400, detail="Item is currently unavailable")

    new_order = _create_order_record(
        customer_name=payload.customer_name,
        delivery_address=payload.delivery_address,
        item=item,
        quantity=payload.quantity,
        order_type=payload.order_type,
    )
    response.status_code = 201
    return {"message": "Order placed successfully", "order": new_order}


@app.get("/orders/{order_id}")
def get_order_by_id(order_id: int) -> dict[str, Any]:
    for order in orders:
        if order["order_id"] == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.post("/cart/add")
def add_to_cart(
    item_id: int = Query(..., gt=0),
    quantity: int = Query(default=1, ge=1, le=20),
) -> dict[str, Any]:
    item = find_menu_item(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    if not item["is_available"]:
        raise HTTPException(status_code=400, detail="Cannot add unavailable item to cart")

    for cart_item in cart:
        if cart_item["item_id"] == item_id:
            cart_item["quantity"] += quantity
            cart_item["line_total"] = cart_item["quantity"] * cart_item["price"]
            return {"message": "Cart item quantity updated", "cart_item": cart_item}

    new_cart_item = {
        "item_id": item["id"],
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity,
        "line_total": item["price"] * quantity,
    }
    cart.append(new_cart_item)
    return {"message": "Item added to cart", "cart_item": new_cart_item}


@app.get("/cart")
def get_cart() -> dict[str, Any]:
    grand_total = sum(item["line_total"] for item in cart)
    return {"total_items": len(cart), "grand_total": grand_total, "items": cart}


@app.post("/cart/checkout")
def checkout_cart(payload: CheckoutRequest, response: Response) -> dict[str, Any]:
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    placed_orders: list[dict[str, Any]] = []
    subtotal = 0

    for cart_item in cart:
        menu_item = find_menu_item(cart_item["item_id"])
        if menu_item is None:
            continue

        order = _create_order_record(
            customer_name=payload.customer_name,
            delivery_address=payload.delivery_address,
            item=menu_item,
            quantity=cart_item["quantity"],
            order_type="pickup",
        )
        order["order_type"] = "delivery"
        order["delivery_charge"] = 0
        order["total_price"] = cart_item["line_total"]

        subtotal += cart_item["line_total"]
        placed_orders.append(order)

    delivery_charge = DELIVERY_CHARGE
    grand_total = subtotal + delivery_charge

    cart.clear()
    response.status_code = 201
    return {
        "message": "Checkout successful",
        "placed_orders": placed_orders,
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "grand_total": grand_total,
    }


@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int) -> dict[str, Any]:
    for cart_item in cart:
        if cart_item["item_id"] == item_id:
            cart.remove(cart_item)
            return {"message": f"Removed item {item_id} from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")
