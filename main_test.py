import API_load as API
import update_db.all_tables_update as update
import sqlite3
import create as DB
import helpers as h
from cs50 import SQL

# Test file for testing API and DB functions

# Create variables to be passed into tests
key = '2tQzNrcZpJ7vDDXgznMJzk_03SFEDOqfiTIbRbl0'
data = sqlite3.connect('invenstory.db')
cursor = data.cursor()
db = SQL('sqlite:///invenstory.db')
DB.create_db()
product_id = '614dbe9e-6c0c-11e2-b1f5-4040782fde00'

# Test helper functions on a sample product_id (above)

# Test get_sold_in_time
print('total sold: ', h.get_sold_in_time(product_id,'2021-10-01','2021-12-05'))

# Test get_sold_per_day
# Should return a dict of 3 values (sold, revenue, first_sale_date)
print(h.get_sold_per_day(product_id,'2021-10-01','2021-12-05'))

# Test get_product
# Should return list of dicts of each variant information
print('get_product:' ,h.get_product(product_id), end ='\n\n')

# Test compile and merge variants
# Should return list of dicts of each variant information
print('compiled variants: ', h.compile_variants(product_id), end ='\n\n')
print('merged variants: ', h.merge_variants(product_id,'2021-10-01','2021-12-05'), end ='\n\n')
print('total inventory: ', h.get_total_inventory(product_id), end ='\n\n')
orders = h.get_received_orders(product_id)
for i in orders:
     print('        ',i['id'])
    
print('average lead time: ', h.get_average_lead_time('614dbe9e-6c0c-11e2-b1f5-4040782fde00'), end ='\n\n')


# Check that each of the update functions works:

# Check the update products function pulls from API and inserts into db
update.update_products(key,db)

# Check that orders can be pulled from API and inserted or updated into db
update.update_orders(key, db)

# Check suppliers
update.update_suppliers(key,db)

# Check order products
update.update_order_products(key,db)


# Check that sales can update
update.update_sales(key,db)

# Check that unique products can be pulled from products table into another table
update.update_unique_products(db)

# Check that both replenishment tables (merged and variants) can be updated using helpers and products table
update.update_replenishment(db)