# Import dependencies

from flask import Flask, render_template, redirect
import pymongo
import scrape_mars

# Create instance of Flask app
app = Flask(__name__)

# Create mongo connection
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Create the mars data database and a collection to store scraped data
db = client.mars_data.db
collection = db.marsdata

# Create route that renders index.html template
@app.route("/")
def home():
    
    # if there is no document, scrape and insert scraped data into collection
    if db.collection.count() == 0:
        mars_data = scrape_mars.scrape()
        db.collection.insert_one(mars_data)
        mars_data_entry = db.collection.find_one()
    else:
    # locate data to use with webpage
        mars_data_entry = db.collection.find_one()
    
    return render_template('index.html', mars=mars_data_entry)

# Scrape Route to Import `scrape_mars.py` Script & Call `scrape` Function
@app.route("/scrape")
def scrape():
    # overwriting data as needed
    if db.collection.count() > 0:
        # delete existing data
        db.collection.remove({})
        # scrape new data
        mars_data = scrape_mars.scrape()
        # insert new scraped data
        db.collection.insert_one(mars_data)
    else:
        # scrape data
        mars_data = scrape_mars.scrape()
        # insert data into database
        db.collection.insert_one(mars_data)

    return redirect("/")

# Define Main Behavior
if __name__ == "__main__":
    app.run(debug=True)
