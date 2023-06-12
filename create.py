import sqlite3

def create_db():
    db = sqlite3.connect('invenstory.db')
    cursor = db.cursor()

    # Create supplier table
    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers
                    (id TEXT PRIMARY KEY,
                    name TEXT);
                ''')

    # Create Product table
    cursor.execute('''CREATE TABLE IF NOT EXISTS products
                    (id TEXT PRIMARY KEY,
                    name TEXT,
                    base_name TEXT,
                    sku TEXT,
                    supplier TEXT,
                    inventory_jfk INT,
                    inventory_mta INT,
                    inventory_quality INT,
                    inventory_basement INT,
                    inventory_garage INT,
                    variant_one_name TEXT,
                    variant_one TEXT,
                    variant_two_name TEXT,
                    variant_two TEXT,
                    created_at)
                ''')

    # Create order table
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders
                    (id TEXT PRIMARY KEY,
                    number TEXT,
                    supplier_id TEXT,
                    date_created DATETIME,
                    date_received DATETIME,
                    status TEXT,
                    CONSTRAINT FK_suppliers FOREIGN KEY (supplier_id) REFERENCES suppliers(id));
                ''')

    # Create order products table (stores order information of each product)
    cursor.execute('''CREATE TABLE IF NOT EXISTS order_products
                    (order_id TEXT,
                    count INT,
                    received INT,
                    cost FLOAT,
                    status TEXT,
                    CONSTRAINT FK_orders FOREIGN KEY (order_id) REFERENCES orders(id),
                    CONSTRAINT FK_products FOREIGN KEY (product_id) REFERENCES products(id))
                ''')


    # Create sales products table (stores order information by each product, not by each sale)
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales
                    (id TEXT,
                    product_id TEXT,
                    quantity INT,
                    price FLOAT,
                    total_price FLOAT,
                    sale_date DATETIME,
                    CONSTRAINT FK_products FOREIGN KEY (product_id) REFERENCES products(id))
                ''')

    # Create users table
    db.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY,
                    first TEXT NOT NULL,
                    last TEXT NOT NULL,
                    email TEXT NOT NULL,
                    hasThs TEXT NOT NULL,
                    hashPass TEXT NOT NULL,
                    level TEXT NOT NULL DEFAULT 'regular')
                ''')

    # Create table for unique products - speeds up process of merging for replenishment
    db.execute('''CREATE TABLE IF NOT EXISTS unique_products
                    (id TEXT PRIMARY KEY,
                    base_name TEXT NOT NULL)
                ''')
    
    # Create replenishment table for merged products
    db.execute('''CREATE TABLE IF NOT EXISTS replenishment_merged
                    (id TEXT PRIMARY KEY,
                    name TEXT,
                    sku TEXT,
                    supplier TEXT,
                    total_inventory INT,
                    sold_per_day FLOAT,
                    lead_time INT,
                    days_covered INT,
                    days_until_reorder INT
                )''')
    
    # Create table replenishment_variants
    db.execute('''CREATE TABLE IF NOT EXISTS replenishment_variants
                    (id TEXT PRIMARY KEY,
                    name TEXT,
                    sku TEXT,
                    supplier TEXT,
                    total_inventory INT,
                    sold_per_day FLOAT,
                    lead_time INT,
                    days_covered INT,
                    days_until_reorder INT
                )''')
    
    return 0
