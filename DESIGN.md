Tomas Arevalo\
Thomas Garity\
CS50 Final Project\
Fall 2021\
Design

What is Our Project


Accessing the API and Creating Our Database

The bulk of our time (30+ hours) was spend constructing our data pipeline - API’s were new to both of us, so we spent extra time learning them and 

First, when accessing the API, we had the choice of using API 0.9 or 2.0
for most tables, we chose 2.0 for the larger number of fields available in each json object, for example, supplier_id (a foreign key we see as very useful)
for products, we chose to use 0.9 because it can be requested using the parameter ‘active=’ - this drastically decreased the size of the output, since it only returned currently active products (ones we sell and stock right now). The general benefit of 0.9 is that it offers more parameters

In API_load.py,
we chose to use while loops to iterate through the API because the pagination or version of a json response is purely relational - it only tells the max and minimum numbers of the first and last items returned. it made more sense to keep querying and then check if there was any data returned

There were a couple key design choices we had to make when constructing our data pipeline:
what kind of dataframe to write to - we chose pandas for:
 the readily available functions like drop_duplicates - which was useful because the API occasionally spun out duplicates
it was easy to use and call keys, like a dict
it accepted null/Nan values, which meant we could filter the data later on
In update_db folder (and the respective python files for updating)
We chose to minimize the number of fields we requested in each query to save time spent querying. this was a tip we discovered online about SQL queries
inserting was done in batches to save time with queries
There are lots of try and except statements in the update files
these are explained more specifically in the comments of each file, but they check for valueErrors, so when there are duplicates or objects with Foreign keys that are not in the table they reference
this can be attributed to messy data management over the years from Harvard Shop Managers and the Vend API itself.

With our helper functions, we did our best to limit the number of queries to save time - an example of this would be the nested functions within the functions themselves, so the same query was not repeated anywhere in the function.

Functions
Before getting into the implementation of our functions, one thing that applies to all of them is checking that the request method has to be POST and not GET. The POST is triggered when submitting the form.


Lookup
Lookup starts by first getting the base name the user inputted via the form. We then proceeded to run a couple checks before actually querying the data. To check that the user actually inputted a base name we compared a base name to None. If that was true then we returned an apology prompting the user to resubmit. We then check whether the base name inputted was actually correct by checking the length of a query from the products table. If the base name is incorrect there should be nothing returned and thus the length of the query will be zero. Thus, if the length was 0, we returned an apology again prompting the user to resubmit.
 If the base name passes the following check it is now time to query the information. We started by querying data from the products table using the user inputted base name. Then we got the length of this query so that we could use it in the html. After that, we get the start and end date that the user inputted, and concatenate the month, day, and year strings in the format of YYYY-MM-DD. Then we create a sold per day list and check whether the dates inputted were the same and/or are valid.and go through the product list product by product. We then call the get sold per day function implemented in helpers.py and append the return value to the solder per day list. Finally, 



