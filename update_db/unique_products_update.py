import pandas as pd

def update_unique_products_db(db):
    # Updates database of unique product names, used to merge and compile variants
    unique_names = db.execute('''SELECT id, base_name FROM products WHERE base_name IN
                                (SELECT DISTINCT base_name FROM products)''')
    
    for product in unique_names:
        print('checking ', product['base_name'])
        # Check if the product is in the database already
        if check_exists(db,product):
            print('     exists')
            continue
        else:
            # If it is not, insert the row
            insert_product(db, product)
            print('     inserted', product['base_name'])

def check_exists(db, product):
    rows = db.execute('''SELECT base_name FROM unique_products WHERE base_name = ?''', product['base_name'])
    return len(rows) > 0

def insert_product(db, product):
    db.execute('''INSERT INTO unique_products (id, base_name) 
                    VALUES (?,?)''', 
                    product['id'], product['base_name'])
    