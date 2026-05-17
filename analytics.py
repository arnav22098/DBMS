from __future__ import annotations

import sqlite3


def customer_spending_summary(connection: sqlite3.Connection, customer_id: int) -> dict[str, float | int]:
    row = connection.execute(
        """
        SELECT COUNT(*) AS total_orders, COALESCE(SUM(total_price), 0) AS total_spent
        FROM orders
        WHERE customer_id = ?
        """,
        (customer_id,),
    ).fetchone()
    return {
        "total_orders": int(row["total_orders"]),
        "total_spent": float(row["total_spent"]),
    }


def favorite_product_for_customer(
    connection: sqlite3.Connection,
    customer_id: int,
) -> dict[str, int | str] | None:
    row = connection.execute(
        """
        SELECT
            p.product_id,
            p.name,
            SUM(oi.quantity) AS total_quantity
        FROM order_items oi
        JOIN orders o ON o.order_id = oi.order_id
        JOIN products p ON p.product_id = oi.product_id
        WHERE o.customer_id = ?
        GROUP BY p.product_id, p.name
        ORDER BY total_quantity DESC, p.name ASC
        LIMIT 1
        """,
        (customer_id,),
    ).fetchone()
    if row is None:
        return None
    return {
        "product_id": int(row["product_id"]),
        "name": row["name"],
        "total_quantity": int(row["total_quantity"]),
    }


def top_customers_by_spend(
    connection: sqlite3.Connection,
    limit: int = 5,
) -> list[dict[str, float | int | str]]:
    rows = connection.execute(
        """
        SELECT
            c.customer_id,
            c.name,
            COUNT(o.order_id) AS total_orders,
            COALESCE(SUM(o.total_price), 0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY total_spent DESC, total_orders DESC, c.name ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [
        {
            "customer_id": int(row["customer_id"]),
            "name": row["name"],
            "total_orders": int(row["total_orders"]),
            "total_spent": float(row["total_spent"]),
        }
        for row in rows
    ]


def low_stock_products(
    connection: sqlite3.Connection,
) -> list[dict[str, int | str]]:
    rows = connection.execute(
        """
        SELECT
            p.product_id,
            p.name,
            i.current_stock,
            i.reorder_level
        FROM inventory i
        JOIN products p ON p.product_id = i.product_id
        WHERE i.current_stock <= i.reorder_level
        ORDER BY i.current_stock ASC, p.name ASC
        """
    ).fetchall()
    return [
        {
            "product_id": int(row["product_id"]),
            "name": row["name"],
            "current_stock": int(row["current_stock"]),
            "reorder_level": int(row["reorder_level"]),
        }
        for row in rows
    ]
