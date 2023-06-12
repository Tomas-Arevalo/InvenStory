import API_load as API
import pandas as pd
import create as DB

# Import functions for updating each table
import update_db.product_update as PrUp
import update_db.order_update as OrUp
import update_db.supplier_update as SpUp
import update_db.order_products_update as OpUp
import update_db.sales_update as SaUp
import update_db.unique_products_update as UpUp
import update_db.replenishment_update as ReUp

from datetime import datetime
import sqlite3
import helpers as h
from cs50 import SQL

# Each update function carries out the data pipeline, from API--> JSON --> Pandas --> SQL table

def update_products(key, db):
    df = API.get_products(key)
    print('Finished Getting Products')
    PrUp.update_products_db(db, df)

def update_orders(key, db):
    df = API.get_orders(key)
    print('Finished Getting Orders')
    OrUp.update_orders_db(db, df)

def update_suppliers(key, db):
    df = API.get_suppliers(key)
    print('Finished getting suppliers')
    SpUp.update_suppliers_db(db,df)

def update_order_products(key, db):
    # Use the date of the last pull (we did it on 12/7)
    df = API.get_order_products(key, db, '2021-12-07')
    print('Finished getting order products')
    OpUp.update_order_products_db(db,df)

def update_sales(key, db):
    df = API.get_sales(key)
    print('Finished getting sales')
    SaUp.update_sales_db(db,df)

def update_unique_products(db):
    UpUp.update_unique_products_db(db)
    print('Finished updating unique products')

def update_replenishment(db):
    df = h.create_replenishment(1)
    ReUp.update_replenishment_db(db, df, 1)
    df = h.create_replenishment()
    ReUp.update_replenishment_db(db,df)




