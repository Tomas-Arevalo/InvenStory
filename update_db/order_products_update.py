import pandas as pd
import time

def update_order_products_db(cursor, df):
    # Update all order products
    
    # Create temp dataframe for new items
    tmp_df = pd.DataFrame(columns={'order_id','product_id','count',
                                'received','cost','status'})
    
    print('made it this far')
    # Check if product is already in this order in the database
    for i, product in df.iterrows():
        if check_exists(cursor, product['product_id'], product['order_id']):
            # Update the row in the database if it is (orders may change after they are made)
            print('exists')
            update_order_product(cursor,product)
        else:
            # Insert the row in the database if not
            print("doesn't exist")
            insert_order_product(cursor, product)


def update_order_product(cursor, product):
    # Update product already in db
    
    # Create query
    query = '''UPDATE order_products SET order_id = ?,
                                        product_id = ?,
                                        count = ?,
                                        received=?,
                                        cost = ?,
                                        status = ?
                        WHERE order_id = ?
                            AND product_id = ?'''
    
    # Create params
    params = (product['order_id'],
        product['product_id'],
        product['count'],
        product['received'],
        product['cost'],
        product['status'],
        product['order_id'],
        product['product_id'])

    # Execute query
    cursor.execute(query, params)
    
        
def insert_order_product(cursor, product):

    # Create Query and Parameters
    query = '''INSERT INTO order_products (order_id, product_id,
                        count, received, cost, status)
                        VALUES (?,?,?,?,?,?)'''
    params = (product['order_id'],
        product['product_id'],
        product['count'],
        product['received'],
        product['cost'],
        product['status'])
    
    # Execute query
    cursor.execute(query, params)


def check_exists(cursor, productid, orderid):
    # Check based on product and order id
    time.sleep(0.05)
    products = cursor.execute('''SELECT product_id FROM order_products WHERE order_id = ? AND product_id = ?''', (orderid, productid))
    print(products)
    return products.fetchone() is not None
