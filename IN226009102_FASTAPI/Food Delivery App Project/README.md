# FastAPI Food Delivery App

This project is a complete FastAPI backend for a Food Delivery App and covers all Day 1 to Day 6 internship concepts:

- GET APIs
- POST APIs with Pydantic validation
- Helper functions
- CRUD operations
- Multi-step workflows
- Search, sorting, and pagination

## Project Structure

- main.py
- requirements.txt
- README.md
- screenshots/

## Run Locally

1. Create and activate virtual environment
2. Install dependencies
3. Start server

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open Swagger UI at:

http://127.0.0.1:8000/docs

## Endpoints Implemented

### Day 1 (GET basics)

1. GET /
2. GET /menu
3. GET /menu/{item_id}
4. GET /orders
5. GET /menu/summary

### Day 2 and Day 3 (POST + Pydantic + Helpers)

6. OrderRequest model with validations
7. Helper functions: find_menu_item(), calculate_bill(), filter_menu_logic()
8. POST /orders
9. order_type logic (delivery or pickup)
10. GET /menu/filter

### Day 4 (CRUD)

11. POST /menu
12. PUT /menu/{item_id}
13. DELETE /menu/{item_id}

### Day 5 (Workflow)

14. POST /cart/add and GET /cart
15. DELETE /cart/{item_id} and POST /cart/checkout

### Day 6 (Advanced APIs)

16. GET /menu/search
17. GET /menu/sort
18. GET /menu/page
19. GET /orders/search and GET /orders/sort
20. GET /menu/browse (combined search + sort + pagination)

## Screenshot Checklist

Capture one screenshot per question from Swagger and save in screenshots/ using names like:

- Q1_home_route.png
- Q2_get_menu.png
- Q3_get_menu_by_id.png
- Q4_get_orders.png
- Q5_menu_summary.png
- Q6_pydantic_validation.png
- Q7_helpers_logic.png
- Q8_post_order.png
- Q9_order_type_billing.png
- Q10_menu_filter.png
- Q11_post_menu_item.png
- Q12_put_menu_item.png
- Q13_delete_menu_item.png
- Q14_cart_add_and_view.png
- Q15_cart_delete_and_checkout.png
- Q16_menu_search.png
- Q17_menu_sort.png
- Q18_menu_pagination.png
- Q19_orders_search_sort.png
- Q20_menu_browse_combined.png

## GitHub and LinkedIn Submission

After testing all APIs:

1. Push this project to your own GitHub repository.
2. Publish a LinkedIn post with:
   - Project name
   - What you built
   - FastAPI features used
   - GitHub repo link
   - Project screenshots
3. Tag Innomatics Research Labs in the LinkedIn post.
