import pandas as pd

# This set of functions uses a sql db instead of a cursor- the cursor was too slow.
# It skipped rows when iterating, resulting in somewhat race conditions

def update_sales_db(db, df):
    print('updating sales')

    tmp_df = pd.DataFrame(columns={'id',
                                'product_id',
                                'quantity',
                                'price',
                                'total_price',
                                'sale_date',
                        })
    print('tmp created')
    
    for i, row in df.iterrows():
        if check_exists(db, row['id'], row['product_id']):
            update = update_sale(db,row)
            if update > 0:
                continue
            print('     udpated', row['id'])

        else: 
            tmp_df = tmp_df.append(row)
    
    for i, sale in tmp_df.iterrows():
        insert = (insert_sale(db, sale))
        if insert > 0:
            print(row)
            continue
        print('     inserted')



def update_sale(db, sale):
    # Updates order that is already on the table

    # Create Query
    query = ('''UPDATE sales SET id = ?,
                                    product_id = ?,
                                    quantity = ?,
                                    price = ?,
                                    total_price = ?,
                                    sale_date = ?
                    WHERE id = ?''')

    # Create parameters from the sale
    try:
        db.execute(query, sale['id'], sale['product_id'], sale['quantity'],
            sale['price'], sale['total_price'], sale['sale_date'], sale['id'])
        return 0

    # In case the product is not active (and not in our database), react to error with foreign key
    except ValueError:
        return 1

def insert_sale(db, sale):
    # Insert a new order into the orders table
    query = ('''INSERT INTO sales (id, product_id, quantity, price, total_price, sale_date)
                    VALUES(?,?,?,?,?,?)''')

    # Create parameters from the sale
    try:
        db.execute(query, sale['id'], sale['product_id'], sale['quantity'],
            sale['price'], sale['total_price'], sale['sale_date'])
        return 0
    
    # In case the product is not active (and not in our database), react to error
    except ValueError:
        return 1


def check_exists(db, id, product_id):
    # Check if object exists in SQL database for sales
    results = db.execute('SELECT id FROM sales WHERE id = ? AND product_id = ?;', id, product_id)
    return len(results) > 0
