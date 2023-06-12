Tomas Arevalo\
Thomas Garity\
CS50 Final Project\
Fall 2021\
Documentation

Overview: Inventory management API integration using pandas data pipeline

Link: https://youtu.be/XzXVqcy3ByE

Accessing Our Project
To run our code and be able to access our website you must first download pandas—a software library written for python which we used to transfer data from the Vend API to the database.

This can be done by typing “pip install pandas” directly into your terminal.

Once you are down installing pandas, you must run flask which will take you directly to our website. This can be done by typing “flask run”.

Registering and Logging In
When you first run flask and open our website, you will be brought to the login page. You must then proceed to the register page by clicking on the Register button in the top right corner of the screen. Proceed by entering all the necessary information such as your First Name, Last Name, Email, Password, Confirmed Password, and the API Key. The Password and Confirmed Password must match. Additionally, to prevent non The Harvard Shop (THS) employees from creating their own accounts and have access to our company’s data, we have created a secondary password that must be inputted when registering which is  “aE$bAb6*z=”. Once all the information is submitted as well as a correct secondary password, you will have successfully registered and can then proceed to Log In. Type in your email and password and if all the information is correct, you will have successfully logged in.

Navigating our Website
Once you login, you will immediately be brought to our Dashboard. Here you will be able to see a warm welcome, the daily total revenue, a list of the products which are currently selling really well, and a snapshot of your replenishment list. Supplementary to our dashboard, we have 4 tools that you can use. These are Lookup Product, Replenishment, Compare Products, and Refresh. You can access them by clicking on them which will take you  directly to their corresponding pages. You are also able to logout at any time by clicking on the Logout button in the top right corner of the screen.

Lookup Products
After clicking on the Lookup Products button in the NAVbar you will then be brought to the lookup tool. Here you must input the base name of a product which is essentially the name of the product without its attribute which is usually its size and color. Below I will write up a list of base names that you can input into the form, but you are welcome to look at the products table in invenstroy.db to find more base names. If you decide to do this, beware that since some products are no longer being sold, there may be a lot of zeros. The zeros do not reflect incorrect data. Additionally, since we are pulling from the Vend API, if you see negative numbers for inventory levels, those are the numbers that Vend has, and is not an error on our part. After our annual inventory count which is done in late January, there will be no more negative numbers. One last feature in look up is the ability to choose a time period for the data which will be queried. This is entirely optional, but you're welcome to select a start and end date. If you don’t select a time period, it will default to the past two months. The time period is only used to calculate the sold per day of each product.
Once you click the blue button that says “Look Up”, you will then be shown a table. The first column is the product name which includes the name as well as its size and color. The second column is SKU which is an ID that can be found on the product tag in stores. It is used for internal tracking and is not to be mistaken for the product id which the API creates. The third column is the supplier of the product. The fourth through seventh columns are inventory levels at the four locations in which products can be stored. The Basement is where most of our inventory is kept. MTA, JFK, and Garage are the three storefronts for The Harvard Shop. Lastly, the eighth column is how many of each variant (variants are just a different sizes or colors, but all under the same base name) is being sold per day. 

List of Base Names (enter exactly as written):
Harvard Crest T-Shirt
Harvard Pin
H 1636 Hat
Harvard Arc T-shirt
Premium Cotton H Sweater
Varsity Script Hat
Hahvahd T-Shirt
Merino Wool H Sweater
Harvard Hooded Crest Sweatshirt
Black "Harvard" Beanie
Felt H Hat
Classic H Hat

Replenishment
After clicking on the Replenishment button in the NAVbar you will then be brought to the replenishment report tool. This tool is mainly used to know when to reorder a certain product. To use it is fairly simple. You have two options which you can check off. The first is to merge product variants which combine all the data of each variant into its overarching base name.

For the most part, when we order products from our suppliers we get all sizes at once so we will almost always check off merge product variants. The second option is to Refresh Data (Results in longer load time). This recreates the database using new sold per day values and will likely change how soon we have to reorder. The sold per values change once new sales data is inputted.

Once you click the blue button that says “Generate Report”, you will then be shown a table. The first 5 columns are similar if not the same as the columns in the Lookup tool. The only difference between the two is that total inventory is the sum of the inventory levels at all 4 locations. Name, SKU, supplier, and sold per day are all the same type of values. The following columns are then lead time, days covered, days until reorder, and actions. Lead time is how long it takes for an order of that product to arrive. Days covered is how many days we have until we run out of a product. Days until order is how many days we have until we have to order a product from our supplier again. Lastly, actions is just a remove button which allows you to remove the product from the database and an add to list button that adds a product or variant to the list of products that are going to be ordered. You should only do this for products which you are certain that they do not need to be monitored. An example of this would be the pajama sets, which we have decided we will not be ordering again in the foreseeable future. If you do remove a product, once you update the database the following week, it will pop back up in case you need it again.

Compare Products
After clicking on the Compare Products button in the NAVbar you will then be brought to the compare products tool. This is fairly similar to the Look Up tool with the main difference being that you have to input at least two products and have a max of five. The time period is again optional and works in the same manner as in Look up. It is also only used to calculate the sold per day for each product.
Once you click the blue button that says “Compare Products”, you will then be shown a table. The first column is all the attributes which will be compared across products, and the first row is the base names of which products you chose to compare. All the information of the products will be directly under its corresponding base name. The attributes which are being compared across products are cost, price, revenue, margin, sold per day, and lead time. The cost is how much the average cost of one unit of the corresponding product. The price is the retail price which customers will see in stores and online. The revenue is the total revenue earned through sales of all the product’s variants. The margin is the marginal benefit of a singular product—(product price - product cost)/product price. Sold per day is again how much of each product is sold every day whether online or physically in the stores. Lastly, lead time is how long it will take for an order to arrive at the Basement (where our inventory is sold).

Refresh
After clicking on the Refresh button in the NAVbar you will then be brought to the refresh tool. Here you can choose which database to be updated using the API. After choosing which database you want to be updated, then click on the blue button which says refresh and wait. Once it is done, you will be redirected to the Dashboard.


API_load.py and update_db

Vend, now called LightSpeed, is the point of sale (POS) software we use at the Harvard Shop. It stores our inventory counts, sales data, and history of supplier orders (orders to get more inventory from suppliers). All of our raw data used in the project was pulled from the Vend API. Our functions for doing this can be found in the file API_load.py

We will do our best to explain the elements of the Vend API that we used in our project, but if you have any other questions about the schema of the API, please take a look at: https://docs.vendhq.com/reference/introduction 

In order to make API calls, you are required to obtain an API key from Vend. We have provided you with a key, which has been hardcoded into the files where it is needed. This was a conscious decision, since we felt it would be less secure for users who are registering themselves to pass the key over the web and then to store it in our database. The API key we have provided, in main_test.py and app.py will expire on January 1, 2022. please let us know if you need more time with it.

With the vend API, we execute requests using the general format:

json_object = requests.get(https://harvardshop.vendhq.com/api/[[category]]?[[parameters]], headers=hed).json()

Where json_object is a json string that contains information about the specific [[category]], which, in our project , is one of the following:

products
consignments (general orders and stock transfers -- we narrow this down to only contain supplier orders in get_orders)
consignment products (products included in an order)
these take the form consignments/{{order id}}/products
so we have to iterate through all orders and then make a request for the products in that individual order
sales
suppliers (who we buy products from)
search

headers=hed defines the header included in the api request - where we set our key to gain permission to access the database 

Data Pipeline

For most tables using information from the API in our database, we implemented a data pipeline in API_load.py and the update_db folder (synopsized in all_tables_update)

The flow of information was as follows:

API → JSON string → pandas dataframe (in the function convert_[[table name]]_to_df in API_load → SQL table (in the corresponding [table_name]_update_db.py

API to json (get_[table name]()) in API_load
an example of a string object returned by requesting products would be:

{'pagination': {'page': 8, 'page_size': 200, 'pages': 9, 'results': 1700},
 'products': [{'account_code_purchase': '',
   'account_code_sales': '',
   'active': True,
   'base_name': 'Harvard Serif Hat',
   'brand_id': '',
   'brand_name': '',
   'button_order': '1',
   'deleted_at': '',
   'description': '',
   'display_retail_price_tax_inclusive': 0,
   'handle': 'harvard-serif-hat',
   'has_variants': True,
   'id': 'f2fd6cb8-abff-491c-a3f2-9087a68e66bd',
   'image': 'https://secure.vendhq.com/images/placeholder/product/no-image-white-thumb.png',
   'image_large': 'https://secure.vendhq.com/images/placeholder/product/no-image-white-original.png',
   'images': [],
   'inventory': [{'count': '0',
     'outlet_id': '605445f3-3846-11e2-b1f5-4040782fde00',
     'outlet_name': 'JFK',
     'reorder_point': '',
     'restock_level': ''},
    {'count': '0',
     'outlet_id': '01f9c6db-e35e-11e2-a415-bc764e10976c',
     'outlet_name': 'Mt Auburn',
     'reorder_point': '',
     'restock_level': ''},
    {'count': '0',
     'outlet_id': 'a2ec3422-cb33-11e3-a0f5-b8ca3a64f8f4',
     'outlet_name': 'Quality Graphics',
     'reorder_point': '',
     'restock_level': ''},
    {'count': '0',
     'outlet_id': 'f92e438b-3db4-11e2-b1f5-4040782fde00',
     'outlet_name': 'Basement',
     'reorder_point': '',
     'restock_level': ''},
    {'count': '0',
     'outlet_id': '064dce89-c73d-11e5-ec2a-c92ca32c62a3',
     'outlet_name': 'Garage',
     'reorder_point': '',
     'restock_level': ''}],
   'name': 'Harvard Serif Hat / Black',
   'price': 24.99,
   'price_book_entries': [{'customer_group_id': '5f22ccb4-2397-11e2-b195-4040782fde00',
     'customer_group_name': 'All Customers',
     'display_retail_price_tax_inclusive': 0,
     'id': '7770a304-f304-414d-856f-7878ad3a753b',
     'loyalty_value': None,
     'max_units': '',
     'min_units': '',
     'outlet_id': '',
     'outlet_name': '',
     'price': 24.99,
     'price_book_id': '5f284770-2397-11e2-b195-4040782fde00',
     'price_book_name': 'General Price Book (All Products)',
     'product_id': 'f2fd6cb8-abff-491c-a3f2-9087a68e66bd',
     'tax': 0.0,
     'tax_id': '9c955296-7991-11e2-b1f5-4040782fde00',
     'tax_name': 'No Sales Tax',
     'tax_rate': 0.0,
     'type': 'BASE',
     'valid_from': '',
     'valid_to': ''}],
   'sku': '12733',
   'source_id': '',
   'supplier_code': '',
   'supplier_name': 'Quality',
   'supply_price': '9.68',
   'tags': '',
   'tax': 0.0,
   'tax_id': '9c955296-7991-11e2-b1f5-4040782fde00',
  

… and the list continues (there are about 40 fields (some of which are dicts) within a products object.
 
the string is separated into two main lists: a pagination (api 0.9) or version (api 2.0) string, and a data string, containing the data we want
for requests that take up more than one page - vend sets limits on page_size (the number of elements returned), we used while loops to append multiple request


API_load

To save time, memory, and lines of code, we did not transfer all fields into the pandas dataframe. We selected ones that we knew we would need 



