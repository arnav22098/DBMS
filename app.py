from __future__ import annotations

from analytics import (
    customer_spending_summary,
    favorite_product_for_customer,
    low_stock_products,
    top_customers_by_spend,
)
from db import DB_PATH, get_connection
from seed import reset_database
from store import (
    StoreError,
    add_to_cart,
    authenticate_customer,
    checkout,
    get_cart_items,
    list_categories,
    list_products,
    purchase_history,
    update_cart_item,
)


def prompt_int(prompt: str, *, minimum: int | None = None) -> int:
    while True:
        raw_value = input(prompt).strip()
        try:
            value = int(raw_value)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Please enter a value greater than or equal to {minimum}.")
            continue
        return value


def ensure_database() -> None:
    if not DB_PATH.exists():
        reset_database(DB_PATH)


def print_products(products) -> None:
    if not products:
        print("No products found.")
        return
    print("\nAvailable products:")
    for product in products:
        print(
            f"{product['product_id']}. {product['name']} | {product['category']} | "
            f"INR {product['price']:.2f} | stock: {product['quantity']}"
        )
        print(f"   {product['description']}")


def print_cart(items) -> None:
    if not items:
        print("Your cart is empty.")
        return
    print("\nYour cart:")
    total = 0.0
    for item in items:
        print(
            f"- {item['name']} ({item['category']}) x {item['quantity']} = INR {item['line_total']:.2f}"
        )
        total += float(item["line_total"])
    print(f"Cart total: INR {total:.2f}")


def print_purchase_history(history) -> None:
    if not history:
        print("No orders found for this customer yet.")
        return
    print("\nPurchase history:")
    for order in history:
        print(
            f"Order #{order['order_id']} | {order['order_date']} | {order['order_status']} | "
            f"INR {order['total_price']:.2f} | payment: {order['payment_method']} ({order['payment_status']})"
        )
        print(f"Delivery agent: {order['delivery_agent']}")
        for item in order["items"]:
            print(f"   - {item['name']} x {item['quantity']} @ INR {item['unit_price']:.2f}")


def print_customer_analysis(connection, customer_id: int) -> None:
    spending = customer_spending_summary(connection, customer_id)
    favorite = favorite_product_for_customer(connection, customer_id)
    print("\nCustomer analysis:")
    print(f"Total orders: {spending['total_orders']}")
    print(f"Total spent: INR {spending['total_spent']:.2f}")
    if favorite is None:
        print("Favorite product: no purchases yet")
    else:
        print(
            f"Favorite product: {favorite['name']} "
            f"({favorite['total_quantity']} unit(s) purchased)"
        )


def print_operational_analysis(connection) -> None:
    print("\nTop customers by spend:")
    for row in top_customers_by_spend(connection):
        print(
            f"- {row['name']}: INR {row['total_spent']:.2f} across {row['total_orders']} order(s)"
        )

    low_stock = low_stock_products(connection)
    print("\nLow-stock products:")
    if not low_stock:
        print("- No products are currently at or below reorder level.")
    else:
        for row in low_stock:
            print(
                f"- {row['name']}: stock {row['current_stock']} / reorder level {row['reorder_level']}"
            )


def browse_by_category(connection) -> None:
    categories = list_categories(connection)
    if not categories:
        print("No categories available.")
        return
    print("\nCategories:")
    for index, category in enumerate(categories, start=1):
        print(f"{index}. {category}")
    selection = prompt_int("Choose a category number: ", minimum=1)
    if selection > len(categories):
        print("Invalid category.")
        return
    print_products(list_products(connection, category=categories[selection - 1]))


def customer_session(connection, customer_id: int, customer_name: str) -> None:
    while True:
        print(f"\nWelcome, {customer_name}!")
        print("1. Browse products by category")
        print("2. View all products")
        print("3. Add product to cart")
        print("4. Update or remove a cart item")
        print("5. View cart")
        print("6. Checkout")
        print("7. View purchase history")
        print("8. View customer analysis")
        print("9. Logout")
        choice = prompt_int("Choose an option: ", minimum=1)

        try:
            if choice == 1:
                browse_by_category(connection)
            elif choice == 2:
                print_products(list_products(connection))
            elif choice == 3:
                product_id = prompt_int("Enter the product id: ", minimum=1)
                quantity = prompt_int("Enter the quantity: ", minimum=1)
                add_to_cart(connection, customer_id, product_id, quantity)
                print("Item added to cart.")
            elif choice == 4:
                product_id = prompt_int("Enter the product id to update: ", minimum=1)
                quantity = prompt_int("Enter the new quantity (0 removes it): ", minimum=0)
                update_cart_item(connection, customer_id, product_id, quantity)
                print("Cart updated.")
            elif choice == 5:
                print_cart(get_cart_items(connection, customer_id))
            elif choice == 6:
                print_cart(get_cart_items(connection, customer_id))
                payment_method = input("Enter payment method (card, upi, cash, etc.): ").strip()
                order = checkout(connection, customer_id, payment_method)
                print(f"Order #{order['order_id']} placed successfully.")
                print(f"Assigned delivery agent: {order['delivery_agent']}")
                print(f"Order total: INR {order['total_price']:.2f}")
            elif choice == 7:
                print_purchase_history(purchase_history(connection, customer_id))
            elif choice == 8:
                print_customer_analysis(connection, customer_id)
            elif choice == 9:
                print("Logged out.")
                return
            else:
                print("Please choose a valid option.")
        except StoreError as exc:
            print(exc)


def main() -> None:
    ensure_database()
    connection = get_connection(DB_PATH)

    while True:
        print("\nOnline Shopping System")
        print("1. Login")
        print("2. Reset demo database")
        print("3. View operational analytics")
        print("4. Exit")
        choice = prompt_int("Choose an option: ", minimum=1)

        if choice == 1:
            name = input("Enter your name: ").strip()
            phone_no = input("Enter your phone number: ").strip()
            result = authenticate_customer(connection, name, phone_no)
            print(result.message)
            if result.success and result.customer_id is not None and result.customer_name is not None:
                customer_session(connection, result.customer_id, result.customer_name)
        elif choice == 2:
            connection.close()
            reset_database(DB_PATH)
            connection = get_connection(DB_PATH)
            print("Database reset complete.")
        elif choice == 3:
            print_operational_analysis(connection)
        elif choice == 4:
            connection.close()
            print("Goodbye.")
            return
        else:
            print("Please choose a valid option.")


if __name__ == "__main__":
    main()
