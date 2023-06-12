#import libraries
import requests
import pandas as pd


# Vend 0.9 API, allows for more params on products
url_1 = 'https://harvardshop.vendhq.com/api/'
# Vend 2.0 API, accesses more data, but with fewer parameters available
url_2 = 'https://harvardshop.vendhq.com/api/2.0/'


# Create pandas dataframe using get request to Vend API
def get_products(key):

    # Make API Call
    hed = {'Authorization': 'Bearer ' + key}
    product_response = requests.get(url_1+f'products?active=1&page_size=1000', headers=hed).json()

    product_response = product_response['products']

    # Set the max value for the highest possible version (index), and counter as the last on this page
    page = 1

    while True:
        temp = requests.get(url_1+'products?' + f'active=1&page_size=1000&page={page}', headers=hed).json()
        if not temp['products']:
            break
        product_response.extend(temp['products'])
        print('got page ', page)
        page = page + 1
        
    return import_products_to_df(product_response)
    
# Create pandas dataframe with only the desired columns from the API's json object
def import_products_to_df(products):
    # Build Pandas Dataframe - enables us to write into sql table easier later on
    df = pd.DataFrame(columns=["product_id",
                                "name",
                                "base_name",
                                "sku",
                                "supplier",
                                "inventory_jfk",
                                "inventory_mta",
                                "inventory_quality",
                                "inventory_basement",
                                "inventory_garage",
                                "variant_one_name",
                                "variant_one",
                                "variant_two_name",
                                "variant_two",
                                "updated_at",
                            ])

    # Iterate through all products in the json object
    for product in products:
        id = product['id']
        name = product['name']
        base_name = product['base_name']
        sku = product['sku']

        #Check that the product has an inventory feature (discounts, shipping fees do not have inventory)
        if product['track_inventory']:
            inventory = get_product_inventory(product)
        else:
            continue
        
        # Check that the product has a supplier (discounts/shipping costs do not have suppliers)
        if product['supplier_name'] == 'Route':
            continue
        if 'supplier_name' in product:
            supplier = product['supplier_name']
        else:
            supplier = None

        variant_one_name = product['variant_option_one_name']
        variant_one = product['variant_option_one_value']
        variant_two_name = product['variant_option_two_name']
        variant_two = product['variant_option_two_value']

        updated_at = product['updated_at']

        df = df.append({'product_id':id,
                        'name':name,
                        'base_name': base_name,
                        'sku':sku,
                        'supplier':supplier,
                        'inventory_jfk':inventory['jfk'],
                        'inventory_mta':inventory['mta'],
                        'inventory_quality':inventory['quality'],
                        'inventory_basement':inventory['basement'],
                        'inventory_garage':inventory['garage'],
                        'variant_one_name':variant_one_name,
                        'variant_one':variant_one, 
                        'variant_two_name':variant_two_name,
                        'variant_two':variant_two,
                        'updated_at': updated_at
                    }, ignore_index=True)

    return df


def get_product_inventory(product_json):
    # Return inventory levels for specified product in json object

    # Create variable for the array that stores inventory levels in the json object
    list = product_json['inventory']

    # Write count levels into a new dict that is outputted
    inventory = {'jfk': list[0]['count'],
                'mta' : list[1]['count'],
                'quality' : list[2]['count'],
                'basement' : list[3]['count'],
                'garage' : list[4]['count']
    }

    return inventory


def get_suppliers(key):

    # Make API call
    hed = {'Authorization': 'Bearer ' + key}
    supplier_response = requests.get(url_2+'suppliers/', headers=hed).json()
    suppliers = supplier_response['data']

    return(import_suppliers_to_df(suppliers))


def import_suppliers_to_df(suppliers):
    # Create pandas dataframe
    df = pd.DataFrame(columns=["id", "name"])

    for supplier in suppliers:
        id = supplier['id']
        name = supplier['name']

        # Add id and name to dataframe
        df = df.append({'id':id, 'name':name}, ignore_index = True)

    return df

def get_orders(key):
    # Make API call
    hed = {'Authorization': 'Bearer ' + key}
    order_response = requests.get(url_2+'consignments?type=SUPPLIER&page_size=500', headers=hed).json()

    # Set the max value for the highest possible version (index), and counter as the last on this page
    max = order_response['version']['max']

    order_response = order_response['data']

    while True:
        temp = requests.get(url_2+'consignments?' + f'type=SUPPLIER&page_size=500&after={max}', headers=hed).json()
        order_response.extend(temp['data'])
        max = temp['version']['max']
        if not temp['data']:
            break
        print('     Gotten page until', max)
    return import_orders_to_df(order_response)

def import_orders_to_df(orders_json):
    df = pd.DataFrame(columns={'order_id', 
                                'name',
                                'supplier_id',
                                'date_created',
                                'date_received',
                                'status'})
    
    for order in orders_json:
        id = order['id']

        if order['name'] != '':
            number = order['name']
        else: 
            number = order['reference']

        supplier_id = order['supplier_id']
        date_created = order['created_at']
        date_received = order['received_at']
        status = order['status']

        df = df.append({'order_id':id, 'number':number, 'supplier_id':supplier_id,
                    'date_created':date_created, 'date_received':date_received,
                    'status':status}, ignore_index=True)
        print('     Appended ', number)
    
    print(df)
    return df


def get_sales(key):
    # Make API call
    hed = {'Authorization': 'Bearer ' + key}

    # Use search API instead of all sales fulfillments - allows for more parameters

    # Hard-coded value for 'after' in API call is set because sales take long time to update
    # This was for the purpose of this project only (so CAs/TFs could actually test it without waiting 10 minutes)
    sales_response = requests.get(url_2+f'sales?page_size=500&after=19000000000', headers=hed).json()
    max = sales_response['version']['max']
    sales_response = sales_response['data']

    while True:
        # API is separated into pages by version max and min values - the first and last items on a page

        # Iterate through pages, setting after= (the start of the next page) to the previous page's max
        tmp = requests.get(url_2+f'sales?page_size=500&after={max}', headers=hed).json()

        # Add those sales to the existing json object
        sales_response.extend(tmp['data'])

        # Print that page max
        print('Got page until version = ',max)

        # Set the new max
        max = tmp['version']['max']

        # Check that the page is not empty - if so, break
        if not tmp['data']:
            break

    return import_sales_to_df(sales_response)

def import_sales_to_df(sales_json):
    df = pd.DataFrame(columns={ 
        'id', 'product_id', 'quantity', 'price', 'total_price', 'sale_date'
    })

    for sale in sales_json:

        # Iterate through sales, selecting only completed sales, omitting returns
        for product in sale['line_items']:
            if (product['status'] == 'CONFIRMED' or product['status'] == 'CLOSED') and product['is_return'] == False:
                
                # Define variables for desired fields to be passed into pandas
                id = product['id']
                product_id = product['product_id']
                quantity = product['quantity']
                price = product['price']
                total_price = quantity * price
                sale_date = sale['created_at']
                
                # Append that sale to the dataframe
                df = df.append({'id':id,
                                'product_id':product_id,
                                'quantity':quantity,
                                'price':price,
                                'total_price':total_price,
                                'sale_date':sale_date}, ignore_index=True)
    print(df)
    return df


def get_order_products(key, db, date_since):
    # Create table of the products and counts of products that have been ordered
    # These are a special case because the API doesn't allow a call to access all of them at once
    
    # Must be requested for one individual order
    # User specifies date_since (earliest date of order) so request doesn't take unneccessarily long
    # Orders from years ago will not have changed since then

    # Create API call
    hed = {'Authorization': 'Bearer ' + key}

    # Create dataframe
    df = pd.DataFrame(columns={'order_id','product_id','count',
                                'received','cost','status'})
    
    # Create list of order numbers after the given date to cycle through to create dataframe
    order_ids = db.execute('''SELECT id FROM orders WHERE date_created >= ?;''', [date_since])

    for id in order_ids:
        # Use consignments API to obtain product info for that order
        order_products = requests.get(url_2+'consignments/' + id + '/products', headers=hed).json()
        
        # Only include the data field of the API response
        order_products = order_products['data']

        # Loop through products in the order, add them to dataframe
        for product in order_products:
            df = df.append({'order_id':id, 
                            'product_id':product['product_id'],
                            'count':product['count'],
                            'received': product['received'],
                            'cost':product['cost'],
                            'status':product['status']
                            }, ignore_index=True)

        # Print notification to the terminal
        print('Got order product from order on ', product['created_at'])

    return df 