import pandas as pd

def update_suppliers_db(db, df):
    tmp_df = pd.DataFrame(columns=['id', 'name'])

    for i, row in df.iterrows():
        print(row)
        if not check_exists(db, row['id']):
            print('     does not exis')
            tmp_df = tmp_df.append(row)

    for i, row in tmp_df.iterrows():
        insert_supplier(db, row)

def check_exists(db, id):
    # Check if a supplier is already in the table
    # Supplier ids do not change so no need to write an update function
    results = db.execute('SELECT id FROM suppliers WHERE id = ?;', id)
    print(results)
    return len(results) > 0

def insert_supplier(db, supplier):
    db.execute('INSERT INTO suppliers(id, name) VALUES(?, ?);', supplier['id'], supplier['name'])
