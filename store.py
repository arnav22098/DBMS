from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime


class StoreError(Exception):
    """Raised when a user-facing store operation cannot be completed."""


@dataclass(slots=True)
class AuthResult:
    success: bool
    message: str
    customer_id: int | None = None
    customer_name: str | None = None


def authenticate_customer(
    connection: sqlite3.Connection,
    name: str,
    phone_no: str,
) -> AuthResult:
    customer = connection.execute(
        """
        SELECT customer_id, name, blocked
        FROM customers
        WHERE phone_no = ?
        """,
        (phone_no,),
    ).fetchone()

    if customer is None:
        return AuthResult(False, "Invalid credentials.")

    if int(customer["blocked"]) == 1:
        return AuthResult(False, "Your account is blocked due to too many failed login attempts.")

    if customer["name"].strip().lower() != name.strip().lower():
        with connection:
            connection.execute(
                "INSERT INTO login_attempts(customer_id, success) VALUES (?, 0)",
                (customer["customer_id"],),
            )
            blocked = connection.execute(
                "SELECT blocked FROM customers WHERE customer_id = ?",
                (customer["customer_id"],),
            ).fetchone()
        if blocked is not None and int(blocked["blocked"]) == 1:
            return AuthResult(False, "Your account is blocked due to too many failed login attempts.")
        return AuthResult(False, "Invalid credentials.")

    with connection:
        connection.execute(
            "INSERT INTO login_attempts(customer_id, success) VALUES (?, 1)",
            (customer["customer_id"],),
        )
    return AuthResult(
        True,
        "Login successful!",
        customer_id=int(customer["customer_id"]),
        customer_name=customer["name"],
    )


def list_categories(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        "SELECT DISTINCT category FROM products ORDER BY category ASC"
    ).fetchall()
    return [row["category"] for row in rows]


def list_products(
    connection: sqlite3.Connection,
    *,
    category: str | None = None,
) -> list[sqlite3.Row]:
    if category is None:
        return connection.execute(
            """
            SELECT product_id, name, category, price, quantity, description
            FROM products
            ORDER BY category ASC, name ASC
            """
        ).fetchall()
    return connection.execute(
        """
        SELECT product_id, name, category, price, quantity, description
        FROM products
        WHERE category = ?
        ORDER BY name ASC
        """,
        (category,),
    ).fetchall()


def get_product(connection: sqlite3.Connection, product_id: int) -> sqlite3.Row:
    product = connection.execute(
        """
        SELECT product_id, name, category, price, quantity, description
        FROM products
        WHERE product_id = ?
        """,
        (product_id,),
    ).fetchone()
    if product is None:
        raise StoreError("Product not found.")
    return product


def get_or_create_active_cart(connection: sqlite3.Connection, customer_id: int) -> int:
    cart = connection.execute(
        """
        SELECT cart_id
        FROM carts
        WHERE customer_id = ? AND status = 'ACTIVE'
        """,
        (customer_id,),
    ).fetchone()
    if cart is not None:
        return int(cart["cart_id"])

    cursor = connection.execute(
        """
        INSERT INTO carts(customer_id, status, total_price, no_of_items)
        VALUES (?, 'ACTIVE', 0, 0)
        """,
        (customer_id,),
    )
    return int(cursor.lastrowid)


def add_to_cart(
    connection: sqlite3.Connection,
    customer_id: int,
    product_id: int,
    quantity: int,
) -> None:
    if quantity <= 0:
        raise StoreError("Quantity must be greater than zero.")

    product = get_product(connection, product_id)
    cart_id = get_or_create_active_cart(connection, customer_id)
    existing = connection.execute(
        """
        SELECT quantity
        FROM cart_items
        WHERE cart_id = ? AND product_id = ?
        """,
        (cart_id, product_id),
    ).fetchone()
    existing_quantity = int(existing["quantity"]) if existing is not None else 0
    requested_quantity = existing_quantity + quantity
    if requested_quantity > int(product["quantity"]):
        raise StoreError(
            f"Only {product['quantity']} unit(s) of {product['name']} are currently available."
        )

    with connection:
        if existing is None:
            connection.execute(
                """
                INSERT INTO cart_items(cart_id, product_id, quantity)
                VALUES (?, ?, ?)
                """,
                (cart_id, product_id, quantity),
            )
        else:
            connection.execute(
                """
                UPDATE cart_items
                SET quantity = ?
                WHERE cart_id = ? AND product_id = ?
                """,
                (requested_quantity, cart_id, product_id),
            )
        _refresh_cart_totals(connection, cart_id)


def update_cart_item(
    connection: sqlite3.Connection,
    customer_id: int,
    product_id: int,
    quantity: int,
) -> None:
    cart_id = get_or_create_active_cart(connection, customer_id)
    if quantity < 0:
        raise StoreError("Quantity cannot be negative.")

    with connection:
        if quantity == 0:
            connection.execute(
                """
                DELETE FROM cart_items
                WHERE cart_id = ? AND product_id = ?
                """,
                (cart_id, product_id),
            )
        else:
            product = get_product(connection, product_id)
            if quantity > int(product["quantity"]):
                raise StoreError(
                    f"Only {product['quantity']} unit(s) of {product['name']} are currently available."
                )
            updated = connection.execute(
                """
                UPDATE cart_items
                SET quantity = ?
                WHERE cart_id = ? AND product_id = ?
                """,
                (quantity, cart_id, product_id),
            )
            if updated.rowcount == 0:
                raise StoreError("That product is not currently in the cart.")
        _refresh_cart_totals(connection, cart_id)


def get_cart_items(
    connection: sqlite3.Connection,
    customer_id: int,
) -> list[sqlite3.Row]:
    cart_id = get_or_create_active_cart(connection, customer_id)
    return connection.execute(
        """
        SELECT
            ci.product_id,
            p.name,
            p.category,
            p.price,
            ci.quantity,
            ROUND(p.price * ci.quantity, 2) AS line_total
        FROM cart_items ci
        JOIN products p ON p.product_id = ci.product_id
        WHERE ci.cart_id = ?
        ORDER BY p.name ASC
        """,
        (cart_id,),
    ).fetchall()


def checkout(
    connection: sqlite3.Connection,
    customer_id: int,
    payment_method: str,
) -> dict[str, object]:
    payment_method = payment_method.strip()
    if not payment_method:
        raise StoreError("Payment method cannot be blank.")

    cart_id = get_or_create_active_cart(connection, customer_id)
    items = connection.execute(
        """
        SELECT
            ci.product_id,
            ci.quantity,
            p.name,
            p.price,
            p.quantity AS stock_quantity
        FROM cart_items ci
        JOIN products p ON p.product_id = ci.product_id
        WHERE ci.cart_id = ?
        ORDER BY p.name ASC
        """,
        (cart_id,),
    ).fetchall()
    if not items:
        raise StoreError("Your cart is empty.")

    total_price = round(sum(float(item["price"]) * int(item["quantity"]) for item in items), 2)
    delivery_agent = connection.execute(
        """
        SELECT
            d.agent_id,
            d.name
        FROM delivery_agents
        AS d
        LEFT JOIN orders o ON o.delivery_agent_id = d.agent_id
        WHERE d.is_available = 1
        GROUP BY d.agent_id, d.name
        ORDER BY COUNT(o.order_id) ASC, d.agent_id ASC
        LIMIT 1
        """
    ).fetchone()
    if delivery_agent is None:
        raise StoreError("No delivery agent is currently available.")

    order_items: list[dict[str, object]] = []
    with connection:
        for item in items:
            if int(item["quantity"]) > int(item["stock_quantity"]):
                raise StoreError(
                    f"Not enough stock for {item['name']}. Available: {item['stock_quantity']}."
                )

        order_cursor = connection.execute(
            """
            INSERT INTO orders(cart_id, customer_id, delivery_agent_id, order_date, order_status, total_price)
            VALUES (?, ?, ?, ?, 'Placed', ?)
            """,
            (
                cart_id,
                customer_id,
                int(delivery_agent["agent_id"]),
                datetime.now().date().isoformat(),
                total_price,
            ),
        )
        order_id = int(order_cursor.lastrowid)

        for item in items:
            connection.execute(
                """
                INSERT INTO order_items(order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
                """,
                (
                    order_id,
                    int(item["product_id"]),
                    int(item["quantity"]),
                    float(item["price"]),
                ),
            )
            connection.execute(
                """
                UPDATE products
                SET quantity = quantity - ?
                WHERE product_id = ?
                """,
                (int(item["quantity"]), int(item["product_id"])),
            )
            order_items.append(
                {
                    "product_id": int(item["product_id"]),
                    "name": item["name"],
                    "quantity": int(item["quantity"]),
                    "unit_price": float(item["price"]),
                }
            )

        connection.execute(
            """
            INSERT INTO payments(order_id, payment_method, payment_status, payment_date, amount)
            VALUES (?, ?, 'Paid', ?, ?)
            """,
            (
                order_id,
                payment_method,
                datetime.now().date().isoformat(),
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
                datetime.now().isoformat(timespec="seconds"),
                f"Payment received for order {order_id} using {payment_method}.",
            ),
        )
        connection.execute(
            """
            UPDATE carts
            SET status = 'CHECKED_OUT', updated_at = CURRENT_TIMESTAMP
            WHERE cart_id = ?
            """,
            (cart_id,),
        )
        connection.execute(
            """
            DELETE FROM cart_items
            WHERE cart_id = ?
            """,
            (cart_id,),
        )
        connection.execute(
            """
            INSERT INTO carts(customer_id, status, total_price, no_of_items)
            VALUES (?, 'ACTIVE', 0, 0)
            """,
            (customer_id,),
        )

    return {
        "order_id": order_id,
        "total_price": total_price,
        "payment_method": payment_method,
        "delivery_agent": delivery_agent["name"],
        "order_items": order_items,
    }


def purchase_history(
    connection: sqlite3.Connection,
    customer_id: int,
) -> list[dict[str, object]]:
    orders = connection.execute(
        """
        SELECT
            o.order_id,
            o.order_date,
            o.order_status,
            o.total_price,
            d.name AS delivery_agent,
            p.payment_method,
            p.payment_status
        FROM orders o
        LEFT JOIN delivery_agents d ON d.agent_id = o.delivery_agent_id
        LEFT JOIN payments p ON p.order_id = o.order_id
        WHERE o.customer_id = ?
        ORDER BY o.order_id DESC
        """,
        (customer_id,),
    ).fetchall()

    history: list[dict[str, object]] = []
    for order in orders:
        items = connection.execute(
            """
            SELECT
                oi.product_id,
                pr.name,
                oi.quantity,
                oi.unit_price
            FROM order_items oi
            JOIN products pr ON pr.product_id = oi.product_id
            WHERE oi.order_id = ?
            ORDER BY pr.name ASC
            """,
            (int(order["order_id"]),),
        ).fetchall()
        history.append(
            {
                "order_id": int(order["order_id"]),
                "order_date": order["order_date"],
                "order_status": order["order_status"],
                "total_price": float(order["total_price"]),
                "delivery_agent": order["delivery_agent"],
                "payment_method": order["payment_method"],
                "payment_status": order["payment_status"],
                "items": [
                    {
                        "product_id": int(item["product_id"]),
                        "name": item["name"],
                        "quantity": int(item["quantity"]),
                        "unit_price": float(item["unit_price"]),
                    }
                    for item in items
                ],
            }
        )
    return history


def _refresh_cart_totals(connection: sqlite3.Connection, cart_id: int) -> None:
    summary = connection.execute(
        """
        SELECT
            COALESCE(SUM(ci.quantity), 0) AS no_of_items,
            COALESCE(SUM(ci.quantity * p.price), 0) AS total_price
        FROM cart_items ci
        JOIN products p ON p.product_id = ci.product_id
        WHERE ci.cart_id = ?
        """,
        (cart_id,),
    ).fetchone()
    connection.execute(
        """
        UPDATE carts
        SET total_price = ?, no_of_items = ?, updated_at = CURRENT_TIMESTAMP
        WHERE cart_id = ?
        """,
        (
            round(float(summary["total_price"]), 2),
            int(summary["no_of_items"]),
            cart_id,
        ),
    )
