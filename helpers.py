import sqlite3 
from cs50 import SQL
import numpy as np
import pandas as pd

from flask import redirect, render_template, request, session
from functools import wraps
from datetime import datetime, timedelta
import time

db = SQL('sqlite:///invenstory.db')

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def get_product(product_id):
    product = db.execute('SELECT * FROM products WHERE id=?;', product_id)

    return product[0]


def get_sold_in_time(product_id, start_date, end_date):
    # Returns number of product sold and total revenue in a given time period

    # Create Query
    sales = db.execute('SELECT quantity,total_price FROM sales WHERE product_id=? AND sale_date >= ?AND sale_date <= ?;', product_id, start_date, end_date)
    date = db.execute('SELECT sale_date FROM sales WHERE product_id=? AND sale_date >= ?AND sale_date <= ? LIMIT 1;', product_id, start_date, end_date)
    
    # Set date for first sale, used in calculating sold per day
    first_sale_date = None
    if len(date) > 0:
        first_sale_date = date[0]['sale_date']


    number_sold = 0
    total_revenue = 0

    # Sum quantities and revenue of all sales
    for sale in sales:
        number_sold = number_sold + sale['quantity']
        total_revenue  = total_revenue + sale['total_price']
    
    return {'sold': number_sold, 'revenue': total_revenue, 'first_sale_date':first_sale_date}

def get_sold_per_day(product_id, start_date=None, end_date=None):
    # Returns number of product sold per day in a given time period
    
    if end_date:
        # Convert string input into datetime object
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.today()
    
    if start_date:
        # Convert string input into datetime object
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        # If there is no date for start_date, set it to 60 days ago
        start_date = end_date - timedelta(days=60)

    # Execute get_sold_in_time()
    sales_data = get_sold_in_time(product_id, start_date, end_date)
    
    # Get number sold
    sold = sales_data['sold']

    # If there was a first sale in the time period, set the start date to that
    # This ensures new products are not given artifically low sold per day numbers
    if sales_data['first_sale_date']:
        start_date = convert_to_datetime(sales_data['first_sale_date'])

    # Find change in dates (time between)   
    change = np.timedelta64(end_date-start_date, 'D')
    change = change.astype('int')

    # If the start and end date are the same, set the change to 1 to avoid dividing by 0
    if change == 0:
        change = 1

    return sold/change


def compile_variants(product_id):
    # Combines all variants of a product into one list of dict

    # Execute Query to find all products with same base_name
    variants = db.execute('''SELECT * FROM products WHERE base_name = 
                                    (SELECT base_name FROM products WHERE id = ?)
                                    ORDER BY sku ASC ;''', product_id)

    # Return modified query response
    return variants

def merge_variants(product_id, start_date=None, end_date=None):
    # Takes in product_id and merges all variants into one product object 
    variants = compile_variants(product_id)

    # Information should be the first number of all the product variants
    id = variants[0]['id']
    sku = variants[0]['sku']
    name = variants[0]['base_name']
    supplier = variants[0]['supplier']

    total_inventory = 0
    sold_per_day = 0

    variant_one_name = variants[0]['variant_one_name']
    variant_two_name = variants[0]['variant_two_name']

    # Iterate through variants to calculate total inventor and sold per day for all variants
    for variant in variants:
        total_inventory = total_inventory + get_total_inventory(variant['id'])
        sold_per_day = sold_per_day + get_sold_per_day(variant['id'], start_date, end_date)

    product_merged = {
        'id':id,
        'name':name,
        'sku':sku,
        'supplier':supplier,
        'total_inventory':total_inventory,
        'variant_one_name':variant_one_name,
        'variant_two_name':variant_two_name,
        'sold_per_day':sold_per_day
    }

    # execute compile variants, iterate through and add up inventory levels, create new object
    return product_merged

def get_total_inventory(product_id):

    #Return product object from query using product_id
    product = get_product(product_id)

    total_inventory = 0

    # Create lsit of outlets to iterate through
    inventory_levels = (product['inventory_jfk'],product['inventory_mta'],product['inventory_quality'],product['inventory_basement'],product['inventory_garage'])

    # Iterate through outlets, add each to the total inventory level
    for outlet in inventory_levels:
        total_inventory = total_inventory + outlet

    return total_inventory


def get_days_covered(product_id, start_date, end_date):
    # Takes in product id and computes sold per day, then dividing to find how many days are left in stock
    
    # Retreive product, sold per day, and inventory levels
    sold_per = get_sold_per_day(product_id, start_date, end_date)
    if sold_per == 0:
        sold_per = 0.00001

    inventory = get_total_inventory(product_id)

    days_covered = inventory/sold_per

    # For some product with negative (incorrect) inventory counts, return 0
    if days_covered >= 0:
        return days_covered
    else:
        return 0


def get_order_lead_time(order):
    # Computes the lead time (time to fulfill) for a stock order - useful for days covered
    
    # Convert dates to datetime objects
    created = convert_to_datetime(order['date_created'])
    
    received = convert_to_datetime(order['date_received'])
    
    # Subtract dates, then convert to int
    change = np.timedelta64(received-created, 'D')
    change = change.astype('float')
    
    return change


def get_received_orders(product_id):
    # Queries for all orders that include a given product

    # Selects all columns of order info for orders including the given product
    orders = db.execute('''SELECT * FROM orders WHERE id IN
                (SELECT order_id FROM order_products WHERE product_id=? AND status= 'RECEIVE_SUCCESS')''',
                product_id)
    
    # Returns list of orders (each is a dict)
    return orders

def get_average_lead_time(product_id):
    # Computes average lead time for a product, accounting for COVID-19 increases in lead time

    # Retrieve all orders including the given product
    orders = get_received_orders(product_id)
    # Create count and total object for averaging
    count = 0
    total_lead_time = 0.0

    # Create count and total for orders that are before COVID-19 Pandemic (this data is less accurate)
    cutoff_count = 0
    total_cutoff_lead_time = 0.0

    # Iterate through all orders.
    for order in orders:

        # Convert date created to datetime for comparison
        date_created = convert_to_datetime(order['date_created']) 
        

        # If order created after March 2020 (COVID lead times are longer)
        if date_created > datetime(2020, 3, 1):
            total_lead_time = total_lead_time + get_order_lead_time(order)
            count = count + 1
        
        # If not, add it to fall back lead time
        else:
            total_cutoff_lead_time = total_cutoff_lead_time + get_order_lead_time(order)
            cutoff_count = cutoff_count + 1

    # If there were orders after March 01 2020, calculate average of those
    if count > 0:
        return round(total_lead_time/count)
    
    # If there were no orders after March 01 2020, calculate with older orders:
    if cutoff_count > 0:
        return round(total_cutoff_lead_time/cutoff_count)
    
    else:
        return 0


def convert_to_datetime(date_string):
    # Conversion function specific to the type of datetime formatting used in Vend API
    
    # Remove the hour, minute, second, nanoseconds from string (all we need is Month/Day/Year)
    date_string = date_string[:len(date_string)-15]

    # Convert to datetime object
    date = datetime.strptime(date_string, '%Y-%m-%d')

    return date


def get_lowest_days_covered(product_id, start_date, end_date):
    # Calculates lowest days covered for all variants of a product
    # For replenishment, we order more of a product whenever one variant reaches critically low leves

    # Compile product variants
    product = compile_variants(product_id)

    # Create days covered variable
    days_covered = get_days_covered(product[0]['id'], start_date, end_date)

    # Iterate through variants and calculate days covered
    for variant in product[1::]:
        days = get_days_covered(variant['id'], start_date, end_date)

        # If current days covered is less than the minimum, replace the minimum
        if days < days_covered and days > 0:
            days_covered = days

    return days_covered

def create_replenishment(merge=None):

    # We did not want to waste time loading our oldest sales, so for now replenishment will only use these dates
    start_date = '2021-10-7'
    end_date = '2021-12-7'

    df = pd.DataFrame(columns={'id',
                            'name',
                            'sku',
                            'supplier',
                            'total_inventory',
                            'sold_per_day',
                            'lead_time',
                            'days_covered',
                            'days_until_reorder'})
    if merge:
            # If products are meant to be merged, iterate through products table and merge variants
            products = db.execute('''SELECT id FROM unique_products''')
            
            for row in products:
                # Compile and merge product 
                merged_variants = merge_variants(row['id'], start_date, end_date)
                
                # Calculate average lead time for the first variant (lead time is usually the same for all variants)
                average_lead_time = get_average_lead_time(row['id'])
                
                # Skip products that have not sold at all or have no inventory or have no lead time (they are of no use)
                if merged_variants['total_inventory'] < 0 or merged_variants['sold_per_day'] == 0 or average_lead_time == 0:
                    continue

                # Calculate lowest days covered for all variants
                lowest_days_covered = int(get_lowest_days_covered(row['id'], start_date, end_date))
                days_until_reorder = lowest_days_covered - int(average_lead_time)

                # Append product to dataframe
                df = df.append({'id':merged_variants['id'],
                                'name':merged_variants['name'],
                                'sku':merged_variants['sku'],
                                'supplier':merged_variants['supplier'],
                                'total_inventory':merged_variants['total_inventory'],
                                'sold_per_day':merged_variants['sold_per_day'],
                                'lead_time':average_lead_time,
                                'days_covered':lowest_days_covered,
                                'days_until_reorder':days_until_reorder
                                }, ignore_index=True)
    else:
        # If user does not want variants merged together, repeat this process for individual variants
        variants = db.execute('SELECT name, sku, supplier, id FROM products;')
        
        # Iterate through products and calculate necessary metrics
        for variant in variants:
            total_inventory = get_total_inventory(variant['id'])
            sold_per_day = get_sold_per_day(variant['id'], start_date,end_date)
            average_lead_time = get_average_lead_time(variant['id'])

            # Skip products that have not sold at all and have no inventory (they are of no use)
            if total_inventory <= 0 or sold_per_day == 0:
                continue
            
            else:
                days_covered = total_inventory/sold_per_day
                days_until_reorder = days_covered - average_lead_time

            df = df.append({'id':variant['id'],
                            'name':variant['name'],
                            'sku':variant['sku'],
                            'supplier':variant['supplier'],
                            'total_inventory':total_inventory,
                            'sold_per_day':sold_per_day,
                            'lead_time':average_lead_time,
                            'days_covered':days_covered,
                            'days_until_reorder':days_until_reorder
                                }, ignore_index=True)
    return(df)
            
            