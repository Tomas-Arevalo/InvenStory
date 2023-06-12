import pandas as pd

def update_orders_db(db, df):
    #TODO: main function for updating orders
    tmp_df = pd.DataFrame(columns={'order_id', 
                                'number',
                                'supplier_id',
                                'date_created',
                                'date_received',
                                'status'})

    for i, row in df.iterrows():
        print(row['order_id'])
        if check_exists(db, row['order_id']):

            # Anticipate orders from suppliers who no longer exist (foreign key fails since they are not in suppliers table)
            try:
                update_order(db,row)
            
            # Skip the order if the supplier no longer exists
            except ValueError:
                continue
        else: 
            tmp_df = tmp_df.append(row)
    
    for i, product in tmp_df.iterrows():
        insert_order(db, product)


def update_order(db, order):
    # Updates order that is already on the table

    # Create Query
    db.execute('''UPDATE orders SET id = ?,
                                    number = ?,
                                    supplier_id = ?,
                                    date_created = ?,
                                    date_received = ?,
                                    status = ?
                                WHERE id = ?;
                    ''',
                    order['order_id'],
                    order['number'],
                    order['supplier_id'],
                    order['date_created'],
                    order['date_received'],
                    order['status'],
                    order['order_id'])

def insert_order(db, order):
    print('inserting order ', order['number'])
    # Insert a new order into the orders table
    db.execute('''INSERT INTO orders (id, number, supplier_id, date_created, date_received, status)
                    VALUES(?,?,?,?,?,?);''',
                    order['order_id'], order['number'], order['supplier_id'],
                    order['date_created'], order['date_received'], order['status'])


def check_exists(db,id):
    # Check if object exists in SQL database for orders
    results = db.execute('''SELECT id FROM orders WHERE id=?''', id)
    return len(results) > 0
