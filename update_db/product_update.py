import pandas as pd


# Update products table with all new and existing products
def update_products_db(db, df):
    df = remove_duplicates(df)

    # Create temp pandas dataframe to store all of the new products (ones that do not already exist in the database)
    tmp_df = pd.DataFrame(columns=["product_id",
                            "name",
                            "base_name",
                            "sku", 
                            "supplier",
                            "inventory_jfk",
                            "inventory_mta",
                            "inventory_quality", 
                            "inventory_basement",
                            "inventory_garage",
                            "variant_one_name", "variant_one",
                            "variant_two_name","variant_two"])

    for i, row in df.iterrows():
        # Check if product exists in table already
        if check_exists(db, row['product_id']):
            
            # If so, update the product (avoids creating duplicates)
            update_product(db,row)
            print('     updated', row['name'])
        else: 
            tmp_df = tmp_df.append(row)
            print('     does not exist')

    
    for i, product in tmp_df.iterrows():
        insert_product(db, product)



# Update the products table if a product is already in the table
def update_product(db, product):
    db.execute("""UPDATE products SET id = ?, 
            name = ?,
            base_name = ?, 
            sku = ?, 
            supplier = ?, 
            inventory_jfk = ?, 
            inventory_mta = ?, 
            inventory_quality = ?, 
            inventory_basement = ?, 
            inventory_garage = ?,
            variant_one_name = ?,
            variant_one = ?,
            variant_two_name = ?,
            variant_two = ?
            WHERE id = ?;""",
            product['product_id'], 
            product['name'],
            product['base_name'],
            product['sku'],
            product['supplier'], 
            product['inventory_jfk'],
            product['inventory_mta'],
            product['inventory_quality'],
            product['inventory_basement'],
            product['inventory_garage'], 
            product['variant_one_name'], product['variant_one'], 
            product['variant_two_name'], product['variant_two'], 
            product['product_id'])


def check_exists(db, id):
    # Check if a product is already in the table --> then update it or add it accordingly
    results = db.execute('SELECT id FROM products WHERE id = ?;', ([id]))
    return len(results) > 0


def insert_product(db, product):
    print('inserting', product['name'] , product['product_id'])
    query = ("""INSERT INTO products (id,
                                    name,
                                    base_name,
                                    sku,
                                    supplier,
                                    inventory_jfk, 
                                    inventory_mta,
                                    inventory_quality,
                                    inventory_basement, 
                                    inventory_garage,
                                    variant_one_name,
                                    variant_one,
                                    variant_two_name,
                                    variant_two)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?);""")
    
    params = (product['product_id'], 
                product['name'],
                product['base_name'],
                product['sku'],
                product['supplier'],
                product['inventory_jfk'], 
                product['inventory_mta'], 
                product['inventory_quality'],
                product['inventory_basement'], 
                product['inventory_garage'], 
                product['variant_one_name'], product['variant_one'], 
                product['variant_two_name'], product['variant_two'])

    db.execute(query, params)


def remove_duplicates(df):
    # Removes duplicates from pandas dataframe
    # Api houses some duplicates- older versions with incorrect data

    # Sort by updated date, so newer updated versions of product are kept later on
    df = df.sort_values('updated_at', ascending=True)

    # Drop duplicates - the versions that are updated less recently are dropped
    df = df.drop_duplicates(subset='product_id', keep='last')

    return df
