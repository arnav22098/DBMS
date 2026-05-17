PRAGMA foreign_keys = ON;

DROP TRIGGER IF EXISTS block_customer_after_three_failures;
DROP TRIGGER IF EXISTS sync_inventory_after_product_insert;
DROP TRIGGER IF EXISTS sync_inventory_after_product_quantity_update;
DROP TRIGGER IF EXISTS cart_items_touch_cart_after_insert;
DROP TRIGGER IF EXISTS cart_items_touch_cart_after_update;
DROP TRIGGER IF EXISTS cart_items_touch_cart_after_delete;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS product_reviews;
DROP TABLE IF EXISTS cart_items;
DROP TABLE IF EXISTS carts;
DROP TABLE IF EXISTS login_attempts;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS delivery_agents;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS vendors;

CREATE TABLE vendors (
    vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_info TEXT NOT NULL,
    location TEXT NOT NULL
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    profile_pic TEXT,
    email TEXT NOT NULL UNIQUE,
    phone_no TEXT NOT NULL UNIQUE,
    blocked INTEGER NOT NULL DEFAULT 0 CHECK (blocked IN (0, 1))
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    price REAL NOT NULL CHECK (price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    retailer_id INTEGER NOT NULL,
    FOREIGN KEY (retailer_id) REFERENCES vendors (vendor_id)
);

CREATE TABLE inventory (
    product_id INTEGER PRIMARY KEY,
    current_stock INTEGER NOT NULL CHECK (current_stock >= 0),
    reorder_level INTEGER NOT NULL CHECK (reorder_level >= 0),
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);

CREATE TABLE delivery_agents (
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT NOT NULL,
    is_available INTEGER NOT NULL DEFAULT 1 CHECK (is_available IN (0, 1))
);

CREATE TABLE carts (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'CHECKED_OUT')),
    total_price REAL NOT NULL DEFAULT 0 CHECK (total_price >= 0),
    no_of_items INTEGER NOT NULL DEFAULT 0 CHECK (no_of_items >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_active_cart_per_customer
ON carts(customer_id)
WHERE status = 'ACTIVE';

CREATE TABLE cart_items (
    cart_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    FOREIGN KEY (cart_id) REFERENCES carts (cart_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    UNIQUE (cart_id, product_id)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cart_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    delivery_agent_id INTEGER,
    order_date TEXT NOT NULL,
    order_status TEXT NOT NULL CHECK (
        order_status IN ('Placed', 'Confirmed', 'Delivered', 'Cancelled')
    ),
    total_price REAL NOT NULL CHECK (total_price >= 0),
    FOREIGN KEY (cart_id) REFERENCES carts (cart_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (delivery_agent_id) REFERENCES delivery_agents (agent_id)
);

CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL CHECK (payment_status IN ('Pending', 'Paid', 'Failed')),
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount >= 0),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    date_and_time TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE
);

CREATE TABLE product_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    review_date TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE login_attempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    success INTEGER NOT NULL CHECK (success IN (0, 1)),
    attempt_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TRIGGER block_customer_after_three_failures
AFTER INSERT ON login_attempts
FOR EACH ROW
WHEN NEW.success = 0
AND (
    SELECT COUNT(*)
    FROM login_attempts
    WHERE customer_id = NEW.customer_id
      AND success = 0
) >= 3
BEGIN
    UPDATE customers
    SET blocked = 1
    WHERE customer_id = NEW.customer_id;
END;

CREATE TRIGGER sync_inventory_after_product_insert
AFTER INSERT ON products
FOR EACH ROW
BEGIN
    INSERT INTO inventory(product_id, current_stock, reorder_level)
    VALUES (NEW.product_id, NEW.quantity, 10);
END;

CREATE TRIGGER sync_inventory_after_product_quantity_update
AFTER UPDATE OF quantity ON products
FOR EACH ROW
BEGIN
    UPDATE inventory
    SET current_stock = NEW.quantity
    WHERE product_id = NEW.product_id;
END;

CREATE TRIGGER cart_items_touch_cart_after_insert
AFTER INSERT ON cart_items
FOR EACH ROW
BEGIN
    UPDATE carts
    SET updated_at = CURRENT_TIMESTAMP
    WHERE cart_id = NEW.cart_id;
END;

CREATE TRIGGER cart_items_touch_cart_after_update
AFTER UPDATE ON cart_items
FOR EACH ROW
BEGIN
    UPDATE carts
    SET updated_at = CURRENT_TIMESTAMP
    WHERE cart_id = NEW.cart_id;
END;

CREATE TRIGGER cart_items_touch_cart_after_delete
AFTER DELETE ON cart_items
FOR EACH ROW
BEGIN
    UPDATE carts
    SET updated_at = CURRENT_TIMESTAMP
    WHERE cart_id = OLD.cart_id;
END;
