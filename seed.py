from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from analytics import customer_spending_summary, favorite_product_for_customer
from db import DB_PATH, apply_schema, get_connection


VENDORS = [
    ("Kiran Enterprises", "info@kiranent.com", "Mumbai"),
    ("Sharma Textiles", "contact@sharmatextiles.com", "Surat"),
    ("Patel Manufacturing", "sales@patelmanufacturing.com", "Ahmedabad"),
    ("Raj Exports", "exports@rajexports.com", "Jaipur"),
    ("Verma Electronics", "support@vermaelectronics.com", "Delhi"),
]

PRODUCTS = [
    ("Basmati Rice", 80.0, 198, "Groceries", "Premium basmati rice", 1),
    ("Cotton Shirt", 500.0, 149, "Apparel", "100% cotton shirt", 2),
    ("LED Bulb", 120.0, 498, "Electronics", "Energy saving LED bulb", 3),
    ("Handcrafted Vase", 600.0, 50, "Decor", "Handcrafted decorative vase", 4),
    ("Wireless Headphones", 1500.0, 99, "Electronics", "Bluetooth wireless headphones", 5),
    ("Spices Pack", 300.0, 200, "Groceries", "Organic mixed spices", 1),
    ("Leather Wallet", 700.0, 100, "Accessories", "Genuine leather wallet", 2),
    ("Organic Tea", 250.0, 150, "Beverages", "Assorted organic tea", 1),
    ("Yoga Mat", 800.0, 120, "Fitness", "Eco-friendly yoga mat", 3),
    ("Ceramic Dinner Set", 2000.0, 80, "Kitchenware", "Premium ceramic dinner set", 4),
]

CUSTOMERS = [
    ("Raj Kumar", "Delhi", "raj_profile.jpg", "raj.kumar@example.com", "9123456780"),
    ("Sita Garg", "Mumbai", "sita_profile.jpg", "sita.garg@example.com", "9234567891"),
    ("Amit Patel", "Ahmedabad", "amit_profile.jpg", "amit.patel@example.com", "9345678902"),
    ("Priya Singh", "Kolkata", "priya_profile.jpg", "priya.singh@example.com", "9456789013"),
    ("Vijay Kumar", "Bangalore", "vijay_profile.jpg", "vijay.kumar@example.com", "9567890124"),
]

DELIVERY_AGENTS = [
    ("Arjun Mehta", "arjun.mehta@example.com", 1),
    ("Bhavna Kaur", "bhavna.kaur@example.com", 1),
    ("Chetan Kumar", "chetan.kumar@example.com", 1),
]

PRODUCT_REVIEWS = [
    (1, 1, 5, "Great quality rice", "2024-02-10"),
    (2, 2, 4, "Nice shirt, fits well", "2024-02-12"),
    (5, 1, 5, "Sound quality is excellent", "2024-02-15"),
]

SEED_ORDERS = [
    {
        "customer_id": 1,
        "delivery_agent_id": 1,
        "order_date": "2024-03-01",
        "order_status": "Delivered",
        "payment_method": "Credit Card",
        "items": [
            {"product_id": 1, "quantity": 2, "unit_price": 80.0},
            {"product_id": 5, "quantity": 1, "unit_price": 1500.0},
        ],
    },
    {
        "customer_id": 2,
        "delivery_agent_id": 2,
        "order_date": "2024-03-03",
        "order_status": "Delivered",
        "payment_method": "Debit Card",
        "items": [
            {"product_id": 2, "quantity": 1, "unit_price": 500.0},
            {"product_id": 3, "quantity": 2, "unit_price": 120.0},
        ],
    },
]


def reset_database(db_path: Path | str = DB_PATH) -> Path:
    path = Path(db_path)
    if path.exists():
        path.unlink()

    connection = get_connection(path)
    apply_schema(connection)
    _seed_reference_data(connection)
    _seed_order_history(connection)
    _seed_active_carts(connection)
    connection.close()
    return path


def _seed_reference_data(connection) -> None:
    with connection:
        connection.executemany(
            "INSERT INTO vendors(name, contact_info, location) VALUES (?, ?, ?)",
            VENDORS,
        )
        connection.executemany(
            """
            INSERT INTO products(name, price, quantity, category, description, retailer_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            PRODUCTS,
        )
        connection.executemany(
            """
            INSERT INTO customers(name, address, profile_pic, email, phone_no)
            VALUES (?, ?, ?, ?, ?)
            """,
            CUSTOMERS,
        )
        connection.executemany(
            """
            INSERT INTO delivery_agents(name, contact, is_available)
            VALUES (?, ?, ?)
            """,
            DELIVERY_AGENTS,
        )
        connection.executemany(
            """
            INSERT INTO product_reviews(product_id, customer_id, rating, comment, review_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            PRODUCT_REVIEWS,
        )


def _seed_order_history(connection) -> None:
    for order in SEED_ORDERS:
        total_price = round(
            sum(item["quantity"] * item["unit_price"] for item in order["items"]),
            2,
        )
        with connection:
            cart_cursor = connection.execute(
                """
                INSERT INTO carts(customer_id, status, total_price, no_of_items)
                VALUES (?, 'CHECKED_OUT', ?, ?)
                """,
                (
                    order["customer_id"],
                    total_price,
                    sum(item["quantity"] for item in order["items"]),
                ),
            )
            cart_id = int(cart_cursor.lastrowid)

            order_cursor = connection.execute(
                """
                INSERT INTO orders(
                    cart_id,
                    customer_id,
                    delivery_agent_id,
                    order_date,
                    order_status,
                    total_price
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    cart_id,
                    order["customer_id"],
                    order["delivery_agent_id"],
                    order["order_date"],
                    order["order_status"],
                    total_price,
                ),
            )
            order_id = int(order_cursor.lastrowid)

            for item in order["items"]:
                connection.execute(
                    """
                    INSERT INTO order_items(order_id, product_id, quantity, unit_price)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        order_id,
                        item["product_id"],
                        item["quantity"],
                        item["unit_price"],
                    ),
                )

            connection.execute(
                """
                INSERT INTO payments(order_id, payment_method, payment_status, payment_date, amount)
                VALUES (?, ?, 'Paid', ?, ?)
                """,
                (
                    order_id,
                    order["payment_method"],
                    order["order_date"],
                    total_price,
                ),
            )
            connection.execute(
                """
                INSERT INTO transactions(order_id, date_and_time, type, description)
                VALUES (?, ?, 'Payment', ?)
                """,
                (
                    order_id,
                    f"{order['order_date']}T09:00:00",
                    f"Seed payment for order {order_id}.",
                ),
            )


def _seed_active_carts(connection) -> None:
    existing = {
        int(row["customer_id"])
        for row in connection.execute(
            "SELECT customer_id FROM carts WHERE status = 'ACTIVE'"
        ).fetchall()
    }
    with connection:
        for customer_id in range(1, len(CUSTOMERS) + 1):
            if customer_id in existing:
                continue
            connection.execute(
                """
                INSERT INTO carts(customer_id, status, total_price, no_of_items)
                VALUES (?, 'ACTIVE', 0, 0)
                """,
                (customer_id,),
            )


def _print_seed_summary() -> None:
    connection = get_connection()
    summary = customer_spending_summary(connection, 1)
    favorite = favorite_product_for_customer(connection, 1)
    print(f"Database ready at: {DB_PATH}")
    print(f"Seeded {len(CUSTOMERS)} customers and {len(PRODUCTS)} products.")
    print(
        f"Raj Kumar has {summary['total_orders']} seeded order(s) worth INR {summary['total_spent']:.2f}."
    )
    if favorite is not None:
        print(f"Raj Kumar's current favorite product is: {favorite['name']}.")
    connection.close()


def main() -> None:
    reset_database()
    _print_seed_summary()


if __name__ == "__main__":
    main()
