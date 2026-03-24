import sqlite3
import datetime


class Product:
    def __init__(self, id, name, price, quantity):
        self.id = id
        self.name = name
        self.price = price
        self.quantity = quantity
        
    def __str__(self):
        return self.name

    def decrease_quantity(self, quantity):
        if self.quantity >= quantity:
            self.quantity -= quantity
        else:
            print(f"Only {self.quantity} {self.name}(s) left in stock.")

class Cart:
    def __init__(self):
        self.items = []

    def add_product(self, product):
        self.items.append(product)
        


    def total_price(self):
        return sum(item.price for item in self.items)

    def add__product(self, product, quantity, conn):
        if product[2] >= quantity:
            self.items.append((product, quantity))
        # Decrease the quantity in the database
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE product_id = ?
        """, (quantity, product[0]))
            conn.commit()
        else:
            print(f"Only {product[2]} {product[1]}(s) left in stock.")



    def display_cart(self):
        for item in self.items:
            product, quantity = item
            print(f"{product} - ${product.price} x {quantity}")
            
    def clear_cart(self):
        self.items = []
    

    
    def add_product(self, product,quantity):
        if product.quantity >= quantity:
            self.items.append((product, quantity))
            product.decrease_quantity(quantity)
        else:
            print(f"Only {product.quantity} {product.name}(s) left in stock.")


def get_products(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, name, price, quantity FROM products")
    return [Product(id, name, price, quantity) for id, name, price, quantity in cursor.fetchall()]

#  get_categories that returns a list of categories
def get_categories(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products")
    return [row[0] for row in cursor.fetchall()]

# get_products_by_category that returns a list of products in a category

def get_products_by_category(conn, category):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    return [Product(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()]

def insert_order(conn, customer_id, total_price):
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO orders (customer_id, total_price) VALUES (?, ?)", (customer_id, total_price))
        conn.commit()
    except sqlite3.OperationalError as e:
        print("Error:", e)

def get_customer_purchase_history(conn, customer_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE customer_id = ?", (customer_id,))
    orders = cursor.fetchall()
    for order in orders:
        print(order)

def get_customer_spending(conn, customer_id):
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_price) FROM orders WHERE customer_id = ?", (customer_id,))
    total_spent = cursor.fetchone()[0]
    print(f"Total spent by customer {customer_id}: {total_spent}")
    
def get_customer_product_preference(conn, customer_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT product_id, COUNT(*) 
        FROM orders 
        WHERE customer_id = ? 
        GROUP BY product_id 
        ORDER BY COUNT(*) DESC 
        LIMIT 1
    """, (customer_id,))
    favorite_product = cursor.fetchone()
    print(f"Favorite product of customer {customer_id}: {favorite_product[0]}")
    

def login(cursor, name, phone_no):
    cursor.execute("SELECT blocked FROM customers WHERE name = ? AND phone_no = ?", (name, phone_no))
    result = cursor.fetchone()

    if result is None:
        print("Invalid credentials.")
        return False
    elif result[0] == 1:
        print("Your account is blocked due to too many failed login attempts.")
        return False
    else:
        
        print("Login successful!")
        return True

def get_customer_id(cursor, name, phone_no):
    cursor.execute("SELECT customer_id FROM customers WHERE name = ? AND phone_no = ?", (name, phone_no))
    return cursor.fetchone()[0]

def main():
    global login_attempts   
    conn = sqlite3.connect(r'C:\Users\arnav\my_database.db')
    cursor = conn.cursor()  # Initialize the cursor
    products = get_products(conn)
    cart = Cart()

    # Login loop
    # Login loop
    login_attempts = 0
    while True:
        print("\nOptions:")
        print("1. Login")
        print("2. Exit")
        option = int(input("\nChoose an option: "))

        if option == 1:
            id = input("Enter your name: ")
            name = input("Enter your phoneNo: ")
            cursor.execute("SELECT * FROM customers WHERE name = ? AND phone_no = ?", (id, name))
            result = cursor.fetchone()
            # Check if the login is successful
            if not login(cursor, id, name):  # Replace with your login function
                login_attempts += 1
                if login_attempts >= 3:
                    print("Too many failed login attempts. Please try again later.")
                    break  # Insert a successful login attempt
                
            else:
                # print("Login successful!")
                
                conn.commit()
                

    
    
                Cust_id= get_customer_id(cursor, id, name)
    # Menu loop
                while True:
                    print("\nCategories:")
                    categories = get_categories(conn)
                    for i, category in enumerate(categories):
                        print(f"{i+1}. {category}")
                    print(f"{len(categories) + 1}. Proceed to next options")  # Additional option
                    
                    category_option = int(input("\nChoose a category or proceed to next options: "))
                    if category_option == len(categories) + 1:  # If the user chose to proceed to next options
                        while True:
                            print("\nOptions:")
                            print("1. View cart")
                            print("2. Checkout")
                            print("3. Exit")
                            print("4. Customer Analysis")# Loop for cart, checkout, and exit options
                

                            option = int(input("\nChoose an option: "))

                            if option == 1:
                                print("\nYour Cart:")
                                cart.display_cart()
 
                            elif option == 2:
                                print("\nCheckout:")
                                cart.display_cart()
                                confirm = input("Do you want to confirm your order? (yes/no): ")
                                if confirm.lower() != "yes":
                                   print("Order cancelled.")
                                   continue

                                payment_method = input("Enter payment method (e.g., credit, debit, cash): ")
                                Cust_Id=cursor.execute("SELECT customer_id FROM customers WHERE name = ? AND phone_no = ?", (id, name)).fetchone()
                            # Insert the payment record
    #                             cursor.execute("""
    #                             INSERT INTO payments (order_id, payment_method, payment_status, payment_date)
    #                             VALUES (?, ?, ?, ?)
    #                         """, (int(Cust_Id[0][0]), payment_method, "Pending", datetime.date.today()))
    #                             conn.commit()
                            
    # # Insert the transaction record
    #                             cursor.execute("""
    #     INSERT INTO transactions (date_and_time, type, description)
    #     VALUES (?, ?, ?)
    # """, (datetime.datetime.now(), "Payment", f"Payment for order {Cust_Id[0][0]}"))
    #                             conn.commit()
    # # print("payment for order {Cust_Id[0][0]}")
    # # Display the transaction
                                print(Cust_Id[0])
                                cursor.execute("SELECT * FROM transactions WHERE transaction_id = ? ", (Cust_Id[0],))
                                transaction = cursor.fetchone()
                                print("Your transaction:", transaction)

    # Assign a delivery agent
                                cursor.execute("""
        UPDATE delivery_agents
        SET assigned_customer_id = ?
        WHERE agent_id = (SELECT MIN(agent_id) FROM delivery_agents WHERE assigned_customer_id =?)
    """, (Cust_Id[0], Cust_Id[0]))
                                conn.commit()

    # Display the delivery agent and estimated delivery date
                                cursor.execute("SELECT name FROM delivery_agents WHERE assigned_customer_id = ?", (Cust_Id[0],))
                                agent = cursor.fetchone()[0]
                                print("Your delivery agent:", agent)
                                print("Estimated delivery date:", datetime.date.today() + datetime.timedelta(days=3))

    
                                cart.clear_cart()  # Clear the cart after successful payment

                            elif option == 3:
                                break  # Exit the options loop
                
                            elif option == 4:
                                customer_id = input("Enter the customer id: ")
                                get_customer_purchase_history(conn, Cust_id)
                                get_customer_spending(conn, Cust_id)
                                get_customer_product_preference(conn, Cust_id)
                    
                        if option == 3:
                            break  # Exit the categories loop
                    else:
                        selected_category = categories[category_option - 1]

                        print(f"\nProducts in {selected_category}:")
                        products = get_products_by_category(conn, selected_category)
                        for i, product in enumerate(products):
                            print(f"{i+1}. {product.name} - ${product.price}")


                        print("\nOptions:")
                        print("1. Add product to cart")
                        print("2. View cart")
                        print("3. Checkout")
                        print("4. Exit")

                        option = int(input("\nChoose an option: "))

                        if option == 1:
                            product_name = input("Enter the product name: ")
                            quantity = int(input("Enter the quantity: "))
                            product = next((p for p in products if p.name == product_name), None)
                            Cust_Id=cursor.execute("SELECT customer_id FROM customers WHERE name = ? AND phone_no = ?", (id, name)).fetchone()[0]
                            if product is not None:
                                cart.add_product(product, quantity)
                            else:
                                print("Product not found. Please enter a valid product name.")
                        elif option == 2:
                            print("\nYour Cart:")
                            cart.display_cart()
                        elif option == 3:
                            print("\nCheckout:")
                            cart.display_cart()
                            confirm = input("Do you want to confirm your order? (yes/no): ")
                            if confirm.lower() != "yes":
                                print("Order cancelled.")
                                continue

                            payment_method = input("Enter payment method (e.g., credit, debit, cash): ")
                            Cust_Id=cursor.execute("SELECT customer_id FROM customers WHERE name = ? AND phone_no = ?", (id, name)).fetchone()

                            # Insert the payment record
                            cursor.execute("""
                                INSERT INTO payments (order_id, payment_method, payment_status, payment_date)
                                VALUES (?, ?, ?, ?)
                            """, (Cust_Id[0], 'payment_method', "Pending", datetime.date.today()))
                            conn.commit()
                            
    # Insert the transaction record
                            cursor.execute("""
        INSERT INTO transactions (date_and_time, type, description)
        VALUES (?, ?, ?)
    """, (datetime.datetime.now(), "Payment", f"Payment for order {Cust_Id[0]}"))
                            conn.commit()
    # print("payment for order {Cust_Id[0][0]}")
    # Display the transaction
                            cursor.execute("SELECT * FROM transactions WHERE transaction_id = ? ", (Cust_Id[0],))
                            transaction = cursor.fetchone()
                            print("Your transaction:", transaction)

    # # Assign a delivery agent
                            cursor.execute("""
        UPDATE delivery_agents
        SET assigned_customer_id = ?
        WHERE agent_id = (SELECT MIN(agent_id) FROM delivery_agents WHERE assigned_customer_id =?)
    """, (Cust_Id[0], Cust_Id[0]))
                            conn.commit()

    # Display the delivery agent and estimated delivery date
                            cursor.execute("SELECT name FROM delivery_agents WHERE assigned_customer_id = ?", (Cust_Id[0],))
                            agent = cursor.fetchone()[0]
                            print("Your delivery agent:", agent)
                            print("Estimated delivery date:", datetime.date.today() + datetime.timedelta(days=3))

    
                            cart.clear_cart()  # Clear the cart after successful payment
                            
                        elif option == 4:
                            break  # Exit the menu loop
                
          #delivery agent and customer analysis to be included      
        elif option == 2:
            break  # Exit the login loop

    conn.close()

if __name__ == "__main__":
    main()