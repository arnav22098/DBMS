import sqlite3
import datetime
def main():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    
#     cursor.execute("""
#     ALTER TABLE customers
#     ADD COLUMN blocked INTEGER
# """)
    
#     # Create tables
#     cursor.execute("""
#         CREATE TABLE vendors (
#             vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             contact_info TEXT,
#             location TEXT
#         )
#     """)

    # cursor.execute("""
    #     CREATE TABLE products (
    #         product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT,
    #         price REAL,
    #         quantity INTEGER,
    #         category TEXT,
    #         description TEXT,
    #         retailer_id INTEGER,
    #         FOREIGN KEY (retailer_id) REFERENCES vendors (vendor_id)
    #     )
    # """)
    
#     cursor.execute("""
#                 CREATE TABLE customers (
#                    customer_id INTEGER AUTO_INCREMENT PRIMARY KEY , name VARCHAR (255) , 
#                       address TEXT , profile_pic TEXT ,email VARCHAR (255) UNIQUE , phone_no VARCHAR (255) )
#                       """)
  
#     cursor.execute("""  CREATE TABLE delivery_agents (
# agent_id INT AUTO_INCREMENT PRIMARY KEY ,name VARCHAR (255) ,contact VARCHAR (255) , assigned_customer_id INT ,
#  FOREIGN KEY ( assigned_customer_id ) REFERENCES customers ( customer_id )
#  )""")
    
#     cursor.execute("""  CREATE TABLE carts (
#  cart_id INT AUTO_INCREMENT PRIMARY KEY ,
#  customer_id INT ,total_price DECIMAL (10 , 2) , no_of_items INT , 
#  FOREIGN KEY ( customer_id ) REFERENCES customers ( customer_id ))
# """)
    
#     cursor.execute(""" CREATE TABLE cart_items (
#  cart_item_id INT AUTO_INCREMENT PRIMARY KEY , cart_id INT , product_id INT , quantity INT ,
#  FOREIGN KEY ( cart_id ) REFERENCES carts ( cart_id ) ,
#  FOREIGN KEY ( product_id ) REFERENCES products ( product_id )
#  )""")
    
#     cursor.execute("""  CREATE TABLE inventory (
#  product_id INT , current_stock INT ,
#  reorder_level INT ,PRIMARY KEY ( product_id ) ,
#  FOREIGN KEY ( product_id ) REFERENCES products ( product_id )
#  )""")
    
#     cursor.execute(""" CREATE TABLE orders (order_id INT AUTO_INCREMENT PRIMARY KEY , cart_id INT ,
#  customer_id INT ,delivery_agent_id INT ,
#  order_date DATE , order_status VARCHAR (255) , FOREIGN KEY ( cart_id ) REFERENCES carts ( cart_id ) ,
#  FOREIGN KEY ( customer_id ) REFERENCES customers ( customer_id )
#  ,FOREIGN KEY ( delivery_agent_id ) REFERENCES delivery_agents ( agent_id ))
# """)
    
#     cursor.execute("""  CREATE TABLE product_reviews (
#  review_id INT AUTO_INCREMENT PRIMARY KEY ,
#  product_id INT ,
#  customer_id INT ,
#  rating INT ,
#  comment TEXT , review_date DATE , FOREIGN KEY ( product_id ) REFERENCES products ( product_id ) ,
#  FOREIGN KEY ( customer_id ) REFERENCES customers ( customer_id ) )
# """)
   
#     cursor.execute("""
#                    CREATE TABLE transactions (
# transaction_id INTEGER  PRIMARY KEY  AUTOINCREMENT,
# date_and_time DATETIME ,
# type VARCHAR (255) ,
#  description TEXT
#  )
# """)
    
#     cursor.execute("""  CREATE TABLE payments (
#  payment_id INTEGER  PRIMARY KEY AUTOINCREMENT ,
#  order_id INT , payment_method VARCHAR (255) , payment_status VARCHAR (255) , payment_date DATE , FOREIGN KEY ( order_id ) REFERENCES orders ( order_id )
#  )
# """)
    
    
#     cursor.execute("""
#     CREATE TABLE login_attempts (
#         attempt_id INT AUTO_INCREMENT PRIMARY KEY,
#         customer_id INT,
#         success BOOLEAN,
#         attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
#     )
# """)
#     cursor.execute("""
#     CREATE TRIGGER block_customer_after_three_failures
#     AFTER INSERT ON login_attempts
#     FOR EACH ROW
#     WHEN (SELECT COUNT(*) FROM login_attempts WHERE customer_id = NEW.customer_id AND success = 0) >= 3
#     BEGIN
#         UPDATE customers SET blocked = 1 WHERE customer_id = NEW.customer_id;
#     END;
# """)
#     cursor.execute("""
#     CREATE TRIGGER check_stock_before_order
#     BEFORE INSERT ON orders
#     FOR EACH ROW
#     WHEN (SELECT quantity FROM products WHERE product_id = NEW.product_id) < NEW.quantity
#     BEGIN
#         SELECT RAISE(FAIL, 'Not enough stock for this product.');
#     END;
# """)
    
    


#     # ... Create the rest of the tables here ...

#     # Insert data into vendors table
#     vendors = [
#         ('Kiran Enterprises', 'info@kiranent.com', 'Mumbai'),
#         ('Sharma Textiles', 'contact@sharmatextiles.com', 'Surat'),
#         ('Patel Manufacturing', 'sales@patelmanufacturing.com', 'Ahmedabad'),
#         ('Raj Exports', 'exports@rajexports.com', 'Jaipur'),
#         ('Verma Electronics', 'support@vermaelectronics.com', 'Delhi'),
#         ('Gupta and Sons', 'info@guptasons.com', 'Kolkata'),
#         ('Singh Suppliers', 'contact@singhsuppliers.com', 'Chandigarh'),
#         ( 'Iyer Food Products', 'sales@iyerfoods.com', 'Chennai'),
#         ('Bose Industries', 'info@boseindustries.com', 'Pune'),
#         ('Mishra Crafts', 'contact@mishracrafts.com', 'Lucknow')
#     ]
#     cursor.executemany("""
#         INSERT INTO vendors (name, contact_info, location) VALUES (?, ?, ?)
#     """, vendors)

    # Insert data into products table
    # products = [
    #     ('Basmati Rice', 80.00, 200, 'Groceries', 'Premium basmati rice', 1),
    #     ('Cotton Shirt', 500.00, 150, 'Apparel', '100% cotton shirt', 2),
    #     ('LED Bulb', 120.00, 500, 'Electronics', 'Energy saving LED bulb', 3),
    #     ('Handcrafted Vase', 600.00, 50, 'Decor', 'Handcrafted decorative vase', 4),
    #     ('Wireless Headphones', 1500.00, 100, 'Electronics', 'Bluetooth wireless headphones', 5),
    #     ('Spices Pack', 300.00, 200, 'Groceries', 'Organic mixed spices', 6),
    #     ('Leather Wallet', 700.00, 100, 'Accessories', 'Genuine leather wallet', 7),
    #     ('Organic Tea', 250.00, 150, 'Beverages', 'Assorted organic tea', 8),
    #     ('Yoga Mat', 800.00, 120, 'Fitness', 'Eco-friendly yoga mat', 9),
    #     ('Ceramic Dinner Set', 2000.00, 80, 'Kitchenware', 'Premium ceramic dinner set', 10)
    # ]
    # cursor.executemany("""
    #     INSERT INTO products (name, price, quantity, category, description, retailer_id) VALUES (?, ?, ?, ?, ?, ?)
    # """, products)

    # customers = [
    #      ('Raj Kumar', 'Delhi', 'raj_profile.jpg', 'raj.kumar@example.com', '9123456780'),
    #     ('Sita Garg', 'Mumbai', 'sita_profile.jpg', 'sita.garg@example.com', '9234567891'),
    #     ('Amit Patel', 'Ahmedabad', 'amit_profile.jpg', 'amit.patel@example.com', '9345678902'),
    #     ('Priya Singh', 'Kolkata', 'priya_profile.jpg', 'priya.singh@example.com', '9456789013'),
    #     ('Vijay Kumar', 'Bangalore', 'vijay_profile.jpg', 'vijay.kumar@example.com', '9567890124'),
    #     ('Anita Sharma', 'Pune', 'anita_profile.jpg', 'anita.sharma@example.com', '9678901235'),
    #     ('Mohit Verma', 'Chennai', 'mohit_profile.jpg', 'mohit.verma@example.com', '9789012346'),
    #     ('Kavita Krishnan', 'Hyderabad', 'kavita_profile.jpg', 'kavita.krishnan@example.com', '9890123457'),
    #     ('Sunil Dutt', 'Jaipur', 'sunil_profile.jpg', 'sunil.dutt@example.com', '9901234568'),
    #     ('Neha Malik', 'Chandigarh', 'neha_profile.jpg', 'neha.malik@example.com', '9012345679')
    # ]
    # cursor.executemany("""
    #     INSERT INTO customers (name, address, profile_pic, email, phone_no) VALUES (?, ?, ?, ?, ?)
    # """, customers)
    
    # delivery_agents = [
    #     ('Arjun Mehta', 'arjun.mehta@example.com', 1),
    #     ('Bhavna Kaur', 'bhavna.kaur@example.com', 2),
    #     ('Chetan Kumar', 'chetan.kumar@example.com', 3),
    #     ('Deepika Sen', 'deepika.sen@example.com', 4),
    #     ('Eshaan Ali', 'eshaan.ali@example.com', 5),
    #     ('Falguni Pathak', 'falguni.pathak@example.com', 6),
    #     ('Gaurav Singh', 'gaurav.singh@example.com', 7),
    #     ('Hina Patel', 'hina.patel@example.com', 8),
    #     ('Ishaan Dev', 'ishaan.dev@example.com', 9),
    #     ('Jyoti Sharma', 'jyoti.sharma@example.com', 10)
    # ]
    # cursor.executemany("""
    #     INSERT INTO delivery_agents (name, contact, assigned_customer_id) VALUES (?, ?, ?)
    # """, delivery_agents)
    
    # carts = [
    #     (1, 1080, 2),
    #     (2, 2200, 3),
    #     (3, 850, 1),
    #     (4, 1250, 5),
    #     (5, 1600, 2),
    #     (6, 900, 3),
    #     (7, 700, 1),
    #     (8, 2450, 2),
    #     (9, 1100, 3),
    #     (10, 1500, 2)
    # ]
    # cursor.executemany("""
    #     INSERT INTO carts (customer_id, total_price, no_of_items) VALUES (?, ?, ?)
    # """, carts)
    
    # cart_items = [
    #     (1, 1, 2),
    #     (1, 3, 1),
    #     (2, 4, 2),
    #     (2, 5, 1),
    #     (2, 6, 1),
    #     (3, 7, 1),
    #     (4, 8, 1),
    #     (4, 9, 2),
    #     (4, 10, 2),
    #     (5, 1, 1)
    # ]
    # cursor.executemany("""
    #     INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, ?)
    # """, cart_items)
    
    # inventory = [
    #     (1, 200, 50),
    #     (2, 150, 30),
    #     (3, 500, 100),
    #     (4, 50, 10),
    #     (5, 100, 20),
    #     (6, 200, 50),
    #     (7, 100, 20),
    #     (8, 150, 30),
    #     (9, 120, 20),
    #     (10, 80, 10)
    # ]
    
    # cursor.executemany("""  INSERT INTO inventory ( product_id , current_stock , reorder_level ) 
    #                    VALUES (?, ?, ?)""", inventory)    
    
    # orders = [  (1, 1, 1, '2021-08-01', 'Delivered'),
    #             (2, 2, 2, '2021-08-02', 'In Transit'),
    #             (3, 3, 3, '2021-08-03', 'Delivered'),
    #             (4, 4, 4, '2021-08-04', 'Delivered'),
    #             (5, 5, 5, '2021-08-05', 'In Transit'),
    #             (6, 6, 6, '2021-08-06', 'Delivered'),
    #             (7, 7, 7, '2021-08-07', 'In Transit'),
    #             (8, 8, 8, '2021-08-08', 'Delivered'),
    #             (9, 9, 9, '2021-08-09', 'Delivered'),
    #             (10, 10, 10, '2021-08-10', 'In Transit')
    #         ]
    # cursor.executemany("""  INSERT INTO orders ( cart_id , customer_id , delivery_agent_id , order_date , order_status ) 
    #                    VALUES (?, ?, ?, ?, ?)""", orders)
    
    # product_reviews = [
    #     ( 1, 1, 5, 'Great quality rice', '2021-08-01'),
    #     ( 2, 2, 4, 'Nice shirt, fits well', '2021-08-02'),
    #     ( 3, 3, 3, 'Good bulb, bright light', '2021-08-03'),
    #     ( 4, 4, 5, 'Beautiful vase, love it', '2021-08-04'),
    #     ( 5, 5, 4, 'Headphones are comfortable', '2021-08-05'),
    #     ( 6, 6, 5, 'Spices are aromatic', '2021-08-06'),
    #     ( 7, 7, 3, 'Wallet is of good quality', '2021-08-07'),
    #     ( 8, 8, 4, 'Tea tastes great', '2021-08-08'),
    #     ( 9, 9, 5, 'Yoga mat is non-slip', '2021-08-09'),
    #     (10, 10, 4, 'Dinner set looks elegant', '2021-08-10')
    # ]              
    # cursor.executemany("""  INSERT INTO product_reviews ( product_id , customer_id , rating , comment , review_date ) 
    #                    VALUES (?, ?, ?, ?, ?)""", product_reviews)
    
    # transactions = [
    #     ('2021-08-01 10:00:00', 'Credit', '1'),
    #     ('2021-08-02 11:00:00', 'Debit', '2'),
    #     ('2021-08-03 12:00:00', 'Credit', '3'),
    #     ('2021-08-04 13:00:00', 'Debit', ' 4'),
    #     ('2021-08-05 14:00:00', 'Credit', '5'),
    #     ('2021-08-06 15:00:00', 'Debit', '6'),
    #     ('2021-08-07 16:00:00', 'Credit', '7'),
    #     ('2021-08-08 17:00:00', 'Debit', '8'),
    #     ('2021-08-09 18:00:00', 'Credit', '9'),
    #     ('2021-08-10 19:00:00', 'Debit', '10')
    # ]
    # cursor.executemany("""  INSERT INTO transactions ( date_and_time , type , description ) 
    #                    VALUES (?, ?, ?)""", transactions)
    
    # payments = [
    #     (1, 'Credit Card', 'Success', '2021-08-01'),
    #     (2, 'Debit Card', 'Success', '2021-08-02'),
    #     (3, 'Credit Card', 'Success', '2021-08-03'),
    #     (4, 'Debit Card', 'Success', '2021-08-04'),
    #     (5, 'Credit Card', 'Success', '2021-08-05'),
    #     (6, 'Debit Card', 'Success', '2021-08-06'),
    #     (7, 'Credit Card', 'Success', '2021-08-07'),
    #     (8, 'Debit Card', 'Success', '2021-08-08'),
    #     (9, 'Credit Card', 'Success', '2021-08-09'),
    #     (10, 'Debit Card', 'Success', '2021-08-10')
    # ]
    # cursor.executemany("""  INSERT INTO payments ( order_id , payment_method , payment_status , payment_date ) 
    #                    VALUES (?, ?, ?, ?)""", payments)
    
   
    
    # cursor.execute("""
    #              CREATE TABLE customers (
    #                 customer_id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR (255) , 
    #                    address TEXT , profile_pic TEXT ,email VARCHAR (255) UNIQUE , phone_no VARCHAR (255) )
    #                    """)
    # customers = [
    #       ('Raj Kumar', 'Delhi', 'raj_profile.jpg', 'raj.kumar@example.com', '9123456780'),
    #      ('Sita Garg', 'Mumbai', 'sita_profile.jpg', 'sita.garg@example.com', '9234567891'),
    #      ('Amit Patel', 'Ahmedabad', 'amit_profile.jpg', 'amit.patel@example.com', '9345678902'),
    #      ('Priya Singh', 'Kolkata', 'priya_profile.jpg', 'priya.singh@example.com', '9456789013'),
    #      ('Vijay Kumar', 'Bangalore', 'vijay_profile.jpg', 'vijay.kumar@example.com', '9567890124'),
    #     ('Anita Sharma', 'Pune', 'anita_profile.jpg', 'anita.sharma@example.com', '9678901235'),
    #     ('Mohit Verma', 'Chennai', 'mohit_profile.jpg', 'mohit.verma@example.com', '9789012346'),
    #     ('Kavita Krishnan', 'Hyderabad', 'kavita_profile.jpg', 'kavita.krishnan@example.com', '9890123457'),
    #     ('Sunil Dutt', 'Jaipur', 'sunil_profile.jpg', 'sunil.dutt@example.com', '9901234568'),
    #     ('Neha Malik', 'Chandigarh', 'neha_profile.jpg', 'neha.malik@example.com', '9012345679')
    # ]
    # cursor.executemany("""
    #     INSERT INTO customers (name, address, profile_pic, email, phone_no) VALUES (?, ?, ?, ?, ?)
    # """, customers)
    
    #name='Raj Kumar' 
    #phone='9123456780'
    #Cust_Id=cursor.execute("SELECT customer_id FROM customers WHERE name = ? AND phone_no = ?", (name, phone)).fetchall()
    #query = "SELECT customer_id FROM customers WHERE name = ? AND phone_no = ?"
    query = "SELECT *  from transactions"
    #cursor.execute(query, (name, phone, ))
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
       print(row)
    
    


    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
    
    
    
    
