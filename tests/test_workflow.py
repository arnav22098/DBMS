from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analytics import customer_spending_summary, favorite_product_for_customer
from db import get_connection
from seed import reset_database
from store import (
    add_to_cart,
    authenticate_customer,
    checkout,
    get_cart_items,
    purchase_history,
)


class ShoppingWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_database.db"
        reset_database(self.db_path)
        self.connection = get_connection(self.db_path)

    def tearDown(self) -> None:
        self.connection.close()
        self.temp_dir.cleanup()

    def test_customer_is_blocked_after_three_failed_attempts(self) -> None:
        for _ in range(3):
            result = authenticate_customer(self.connection, "Wrong Name", "9123456780")
            self.assertFalse(result.success)

        blocked_result = authenticate_customer(self.connection, "Raj Kumar", "9123456780")
        self.assertFalse(blocked_result.success)
        self.assertIn("blocked", blocked_result.message.lower())

    def test_checkout_creates_order_payment_and_reduces_stock(self) -> None:
        add_to_cart(self.connection, 3, 10, 1)
        add_to_cart(self.connection, 3, 6, 2)
        order = checkout(self.connection, 3, "UPI")

        self.assertGreater(order["order_id"], 0)
        self.assertEqual(order["payment_method"], "UPI")

        stock = self.connection.execute(
            "SELECT quantity FROM products WHERE product_id = 10"
        ).fetchone()
        self.assertEqual(stock["quantity"], 79)

        payment = self.connection.execute(
            "SELECT payment_status, amount FROM payments WHERE order_id = ?",
            (order["order_id"],),
        ).fetchone()
        self.assertEqual(payment["payment_status"], "Paid")
        self.assertAlmostEqual(payment["amount"], 2600.0)

        cart_items = get_cart_items(self.connection, 3)
        self.assertEqual(cart_items, [])

    def test_customer_analytics_use_order_items_instead_of_broken_order_columns(self) -> None:
        spending = customer_spending_summary(self.connection, 1)
        favorite = favorite_product_for_customer(self.connection, 1)

        self.assertEqual(spending["total_orders"], 1)
        self.assertAlmostEqual(spending["total_spent"], 1660.0)
        self.assertIsNotNone(favorite)
        assert favorite is not None
        self.assertEqual(favorite["name"], "Basmati Rice")

    def test_purchase_history_returns_order_items(self) -> None:
        history = purchase_history(self.connection, 1)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["items"][0]["name"], "Basmati Rice")


if __name__ == "__main__":
    unittest.main()
