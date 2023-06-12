import pandas as pd

def update_replenishment_db(db, df, merge=None):
    tmp_df = pd.DataFrame(columns={'id',
                            'name',
                            'sku',
                            'supplier',
                            'total_inventory',
                            'sold_per_day',
                            'lead_time',
                            'days_covered',
                            'days_until_reorder'})
    
    print(df)
    for i, product in df.iterrows():

        # Check that the row exists in the table already
        if check_exists(db, product['id'], merge):
            # If it does, update the row in the table
            update_product(db, product, merge)
        else:
            # If it doesn't, insert the product
            insert_product(db, product, merge)

def check_exists(db, id, merge=None):

    # Query the corresponding table
    if merge:
        rows = db.execute('''SELECT id FROM replenishment_merged WHERE id = ?;''', id)
    else:
        rows = db.execute('''SELECT id FROM replenishment_variants WHERE id = ?;''', id)
    
    # Return whether or not that row is in the table
    return len(rows) > 0


def update_product(db, product, merge=None):
    # Check if the products have been merged
    if merge:

        # Update the corresponding table
         db.execute('''UPDATE replenishment_merged SET id = ?,
                    name = ?,
                    sku = ?,
                    supplier = ?,
                    total_inventory = ?,
                    sold_per_day = ?,
                    lead_time = ?,
                    days_covered = ?,
                    days_until_reorder = ?
                WHERE id = ?;''', 
                    product['id'], product['name'], product['sku'],
                    product['supplier'], product['total_inventory'], 
                    product['sold_per_day'], product['lead_time'],
                    product['days_covered'], product['days_until_reorder'],
                    product['id'])
    else:
        db.execute('''UPDATE replenishment_variants SET id = ?,
                    name = ?,
                    sku = ?,
                    supplier = ?,
                    total_inventory = ?,
                    sold_per_day = ?,
                    lead_time = ?,
                    days_covered = ?,
                    days_until_reorder = ?
                WHERE id = ?;''', 
                    product['id'], product['name'], product['sku'],
                    product['supplier'], product['total_inventory'], 
                    product['sold_per_day'], product['lead_time'],
                    product['days_covered'], product['days_until_reorder'],
                    product['id'])

def insert_product(db, product, merge):
    if merge:
        db.execute('''INSERT INTO replenishment_merged
                    (id,
                    name,
                    sku,
                    supplier,
                    total_inventory,
                    sold_per_day,
                    lead_time,
                    days_covered,
                    days_until_reorder) 
                    VALUES (?,?,?,?,?,?,?,?,?)''',
                    product['id'], product['name'], product['sku'],
                    product['supplier'], product['total_inventory'], 
                    product['sold_per_day'], product['lead_time'],
                    product['days_covered'], product['days_until_reorder'])
        print('inserted ', product['name'])
    else:
        db.execute('''INSERT INTO replenishment_variants
                    (id,
                    sku,
                    name,
                    supplier,
                    total_inventory,
                    sold_per_day,
                    lead_time,
                    days_covered,
                    days_until_reorder) 
                    VALUES (?,?,?,?,?,?,?,?,?)''',
                    product['id'], product['sku'], product['name'],
                    product['supplier'], product['total_inventory'], 
                    product['sold_per_day'], product['lead_time'],
                    product['days_covered'], product['days_until_reorder'])
                    
