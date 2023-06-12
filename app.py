import os
import pandas as pd

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

import update_db.all_tables_update as update

from helpers import apology, login_required, create_replenishment, get_sold_per_day, get_average_lead_time

# Import update_db functions
import update_db.replenishment_update as ReUp

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set API Key, expires on Jan 1 2022 (email if you need more time)
key = '2tQzNrcZpJ7vDDXgznMJzk_03SFEDOqfiTIbRbl0'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///invenstory.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get the users first name, last name, email, and password from the form
        first = request.form.get("first name")
        last = request.form.get("last name")
        email = request.form.get("email")
        ths_pass = request.form.get("THS password")
        password = request.form.get("password")
        confirmed_password = request.form.get("confirmation")
        
        # Query database for email
        user_list = db.execute("SELECT * FROM users WHERE email = ?", email)
        
        # Checks whether user submitted and email
        if not email:
            return apology("must provide email!", 400)
        
        # Checks if email already exists
        elif len(user_list) != 0:
            return apology("this email already exists!", 400)
        
        # Checks whether user submitted a password and confirmed password
        elif not password or not confirmed_password:
            return apology("must provide password!", 400)
        
        # Checks whether user submitted matching passwords
        elif password != confirmed_password:
            return apology("passwords do not match!", 400)
        
        elif ths_pass != "aE$bAb6*z=":
            return apology("THS Password is not correct!", 400)
        
        # Hashes the password and ths password
        hash_password = generate_password_hash(password)
        hash_ths = generate_password_hash(ths_pass)
        
        # Inserts all the users information into the users table
        db.execute("INSERT INTO users (first, last, email, hashThs, hashPass) VALUES (?, ?, ?, ?, ?) ", first, last, email, hash_ths, hash_password,)
        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        
        # Query the database for email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        
        # Ensure the email exists and password/API key are both correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hashPass"], request.form.get("password")):
            return apology("invalid email and/or password", 403)
        
        # Remember which user is logged in
        session["user_id"] = rows[0]["id"]
        
        # Redirect the user to the home page
        return redirect("/")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/lookup", methods=["GET", "POST"])
@login_required
def lookup():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get the base name of the products from the form
        base_name = request.form.get("base_name")
        
        # Make sure user inputted a base name
        if base_name == None:
            return apology("Please input a product. Try again!", 400)
        
        # Make sure user inputted a correct base name
        elif len(db.execute("SELECT * FROM products WHERE base_name=? ORDER BY sku", base_name)) == 0:
            return apology("Please input a correct product. Try again!", 400)
        
        else:

            # Get the list of products that have the same base name and order them by sku
            products = db.execute("SELECT * FROM products WHERE base_name=? ORDER BY sku", base_name)
            
            # Get the length of the list of products
            length = len(products)

            # Get the start and end date from the user inputted form
            start_date = request.form.get("start_year") + "-" + request.form.get("start_month") + "-" + request.form.get("start_day")
            end_date = request.form.get("end_year") + "-" + request.form.get("end_month") + "-" + request.form.get("end_day")
            
            # Create a sold per day list and append the sold per day values of each product to the end of the list
            # If start_date equals end_date, that means the user didn't input a date
            sold_per_day_list = []
            if start_date == end_date:
                for product in products:
                    sold_per_day_list.append(get_sold_per_day(product["id"]))
            
            # Check whether user inputted valid dates
            elif start_date > end_date:
                return apology("Please valid dates!", 400)
            
            # Calculate sold per day with dates and append it to the sold_per_day_list
            else:
                for product in products:
                    sold_per_day_list.append(get_sold_per_day(product["id"], start_date, end_date))
            
            # Bring the user to lookedup.html and pass in the list of products, its length, 
            # and the sold per day list to create the table in the html using jinja
            return render_template("lookup.html", products=products, length=length, sold_per_day_list=sold_per_day_list)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("lookup.html")



@app.route("/replenishment", methods=["GET", "POST"])
@login_required
def replenishment():

    # If method is post, return a replenishment table for all products, either as variants or merged products
    if request.method == "POST":

        # Get values from checkboxes
        merge = request.form.get("merge")
        refresh = request.form.get("refresh")
        
        # Set merge to None if it was not selected - so it can be passed as argument for functions 
        if merge != 'on':
            merge = None
        
        if refresh == 'on':

            # Re-calculate values for replenishment
            df = create_replenishment(merge)

            # Update or insert values into table
            ReUp.update_replenishment_db(db, df, merge)
            
        # Check if the user would like the product variants to be merged
        if merge:

            # Execute query on corresponding table (replenishment or replenishment_merged)
            data = db.execute('''SELECT *
                FROM replenishment_merged
                ORDER BY days_until_reorder ASC''')
        else:
            data = db.execute('''SELECT *
                FROM replenishment_variants
                ORDER BY days_until_reorder ASC''')

        return render_template("replenishment.html", data=data)

    else:
        return render_template("replenishment.html")

@app.route("/remove_replenishment", methods=["POST"])
@login_required
def remove():
    # Removes the selected product from the replenishment database
    
    # Gather Information from page
    id = request.form.get("id")
    print('id: ', id)

    # No way to check if merge was already checked
    # Instead return whether a '/' was in the product name (no base_names have slashes)
    name = request.form.get("name")

    merge = not (' /' in name)

    # Remove the selected Id from the corresponding table
    if merge:
        db.execute('''DELETE FROM replenishment_merged WHERE id = ?''', id)
        data = db.execute('''SELECT *
            FROM replenishment_merged
            ORDER BY days_until_reorder ASC''')
    else:
        db.execute('''DELETE FROM replenishment_variants WHERE id = ?''', id)
        data = db.execute('''SELECT *
            FROM replenishment_variants
            ORDER BY days_until_reorder ASC''')

    # Re-run the replenishment query

    return render_template("replenishment.html", data=data)

@app.route("/add_to_list", methods=["POST"])
@login_required
def add():
    id = request.form.get("id")
    name = request.form.get("name")

    # No way to check if merge was already checked
    # Instead return whether a '/' was in the product name (no base_names have slashes)
    merge = not (' /' in name)

    # Remove the selected Id from the corresponding table
    if merge:
        db.execute('''SELECT * FROM replenishment_merged WHERE id = ?''', id)
        data = db.execute('''SELECT *
            FROM replenishment_merged
            ORDER BY days_until_reorder ASC''')
    else:
        db.execute('''SELECT * FROM replenishment_variants WHERE id = ?''', id)
        data = db.execute('''SELECT *
            FROM replenishment_variants
            ORDER BY days_until_reorder ASC''')
    
    return render_template('/replenishment.html', data=data)
    


@app.route("/")
@login_required
def dashboard(): 
    
    # Gets list of 10 top most needed to be reordered products
    rep_report = db.execute("SELECT * FROM replenishment_merged ORDER BY days_until_reorder ASC LIMIT 10")
    
    # Gets list of top 5 best selling products
    best_sellers = db.execute("SELECT * FROM replenishment_merged ORDER BY sold_per_day DESC LIMIT 5")
    return render_template("dashboard.html", report=rep_report, best=best_sellers)


@app.route("/compare", methods=["GET", "POST"])
@login_required
def compare():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        
        # Create empty list to pass the products into when accessing the form
        og_product_list = []
        for i in range(1,6):
            og_product_list.append(request.form.get(f"product{i}"))
        length = 0
        
        # Calculate how many products the user inu=putted
        for product in og_product_list:
            if product == "":
                break
            length += 1
        
        # Create a product list
        product_list = []
        for i in range(length):
            product_list.append(og_product_list[i])
        
        # Make sure User inputted at least 2 products
        if length < 2:
            return apology("Please input at least 2 products", 400)
        else:
            
            # Creat cost, price, revenue, margin, sold per day, and lead time list
            cost = []
            price = []
            revenue = []
            margin =[]
            sold_per_day = []
            lead_time = []

            # Get the optional user inputted start and end date
            start_date = request.form.get("start_year") + "-" + request.form.get("start_month") + "-" + request.form.get("start_day")
            end_date = request.form.get("end_year") + "-" + request.form.get("end_month") + "-" + request.form.get("end_day")
            
            # Loop through product list
            for product in product_list:
                
                # Get the id of one of the product variants
                ids = db.execute("SELECT id FROM products WHERE base_name=? ORDER BY sku", product)
                id = ids[0]['id']
                
                # Get the current_cost of the product and append it to the cost list
                current_cost = db.execute("SELECT AVG(cost) FROM order_products WHERE product_id=?", id)[0]['AVG(cost)']
                cost.append(current_cost)
                
                # Get the retail price of the product and append it to the price list
                product_price = db.execute("SELECT price FROM sales WHERE product_id=? ORDER BY price DESC", id)[0]['price']
                price.append(product_price)
                
                # Calculate the total revenue of each group of products
                total_revenue = 0
                
                # Loop through all the product variants
                for singular_id in ids:
                    
                    # Get the revenue for each variant and add it to the toal revenue
                    product_revenue = float(db.execute("SELECT SUM(total_price) FROM sales WHERE product_id=?", singular_id['id'])[0]['SUM(total_price)'])
                    total_revenue += product_revenue
                
                # Append the total revenue to the revenue list
                revenue.append(total_revenue)
                
                # Calculate the profit margin and add it to the margin list
                profit_margin = (product_price - current_cost)/product_price
                margin.append(profit_margin)
                
                # Check whether user inputted a start and end date
                if start_date == end_date:

                    # Calculate sold per day without dates, append it to solder_per_day list
                    total_sold_per_day = 0
                    for product in ids:
                        sold_per_day_value = get_sold_per_day(product['id'])
                        total_sold_per_day += sold_per_day_value
                    sold_per_day.append(total_sold_per_day)
                
                # Check whether user inputted valid dates
                elif start_date > end_date:
                    return apology("Please valid dates!", 400)
                else:

                    # Calculate sold per day with dates, append it to solder_per_day list
                    total_sold_per_day = 0
                    for product in ids:
                        sold_per_day_value = get_sold_per_day(product['id'], start_date, end_date)
                        total_sold_per_day += sold_per_day_value
                    sold_per_day.append(total_sold_per_day)
                
                # Calculate lead time and append it to lead_time list
                lead_time.append(get_average_lead_time(id)) 
            
            # Go to compare.html and pass in values to be used in jinja
            return render_template("compare.html", product_list=product_list, cost=cost, price=price, revenue=revenue, margin=margin, sold_per_day=sold_per_day, lead_time=lead_time)
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("compare.html")


@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    if request.method == "POST":

        products = request.form.get("products")
        suppliers = request.form.get("suppliers")
        sales = request.form.get("sales")
        orders = request.form.get("orders")
        replenishment = request.form.get("replenishment")

        # If user wants to update products, update both products and unique produts (to avoid having another checkbox)
        if products == 'on':
            update.update_products(key,db)
            update.update_unique_products(db)
        
        # Update suppliers if user requests
        if suppliers == 'on':
            update.update_suppliers(key, db)
        
        # Update sales if user requests
        if sales == 'on':
            update.update_sales(key, db)
        
        # Update orders and order products, cuts out an extra checkbox for order products
        # New orders in the database have no use if their products aren't imported too
        if orders == 'on':
            update.update_orders(key,db)
            update.update_order_products(key, db)
        
        # Update both merged and variant replenishment
        if replenishment == 'on':
            update.update_replenishment(db)
        
        return render_template('/dashboard.html')
    
    else:
        return render_template('/refresh.html')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
