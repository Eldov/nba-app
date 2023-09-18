#!/usr/bin/env python
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from helpers import convertDate, testId, groupGame, cleanId, teamsStats
from nba_api.stats.endpoints import leaguegamefinder
from flask import Flask, redirect, url_for, request, render_template, make_response


app = Flask(__name__)

load_dotenv() # Load environment variables

client = MongoClient("mongo:27017")
db = client.nbadb
dategames = db.dategames # Collection where we will insert data from games by specific date request
idgames = db.idgames # Collection where we will insert data from games by specific ID request
teams = db.teams # Collection where we will insert data from team stats by date request
rapidAPI_key = os.environ.get('RAPID_API_KEY') # Load RAPID_API_KEY

try: # Test connection with DB
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

global_dict = {

} # Created a global_dict to share data between routes




@app.route('/') # Landing page
def home():
    return render_template('index.html')



@app.route('/getByDate', methods=['GET']) # First button landing page
def get_by_date():
    
    game_date = global_dict.get('game_date') # Gets data from global_dict to apply filter in the DB

    item_doc = pd.DataFrame(dategames.find({'GAME_DATE': game_date}, {'_id': False})) # Extract result from DB and transform into DF

    return render_template('gamedate.html', tables=[item_doc.to_html(classes='data', header="true")]) # Send DF to page as table



@app.route('/postByDate', methods=['POST']) # First button POST
def post_by_date():

    global_dict["game_date"] = request.form['date'] # Request and insert date in the global_dict
    try:
        game_date = convertDate(global_dict["game_date"]) # Convert date from YYYY-MM-DD to MM/DD/YYYY

        df = leaguegamefinder.LeagueGameFinder(
            date_from_nullable=game_date, date_to_nullable=game_date
            ).get_data_frames()[0] # Insert dates. Because of specific date, start=end. Library requires MM/DD/YYYY format
    except:
        return "Please enter a date in the following format: YYYY-MM-DD"
    
    item_doc = groupGame(df).to_dict(orient='records') # Apply transformations (check helpers.py), transform to dict (Mongo requirement)

    for record in item_doc: # For loop to insert data into DB. Updates based on GAME_ID so it won't repeat entries
        filter_condition = {'GAME_ID': record['GAME_ID']}
        update_operation = {'$set': record}
        dategames.update_one(filter_condition, update_operation, upsert=True)

    return redirect(url_for('get_by_date'))


    
@app.route('/getById', methods=['GET']) # Second button landing page
def get_by_id():
    
    game_id = global_dict.get('game_id') # Request and insert date in the global_dict
    if game_id:                          # Checks if game_id is a string of ints, no letters are allowed in the request
        idgames_df = idgames.find({'GAME_ID': int(game_id)}, {'_id': False})
    else:
        idgames_df = {}
    item_doc = pd.DataFrame(idgames_df)

    return render_template('gameid.html', tables=[item_doc.to_html(classes='data', header="true")]) # Send DF to page as table



@app.route('/postById', methods=['POST']) # Second button POST
def post_by_id():

    global_dict["game_id"] = request.form['id']

    headers = {
    	    "X-RapidAPI-Key": rapidAPI_key,
    	    "X-RapidAPI-Host": "free-nba.p.rapidapi.com"
        }
    
    try:
        game_id = testId(global_dict["game_id"])

        url = f"https://free-nba.p.rapidapi.com/games/{game_id}"

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except TypeError:
        return "Please enter an integer ID"
    except:
        return "A game by the given ID is not available"
    
    item_doc = cleanId(data)

    for record in item_doc:
        filter_condition = {'GAME_ID': record['GAME_ID']}
        update_operation = {'$set': record}
        idgames.update_one(filter_condition, update_operation, upsert=True)

    return redirect(url_for('get_by_id'))



@app.route('/getTeams', methods=['GET']) # Third button landing page
def download_csv():
    return render_template('teamcsv.html')




@app.route('/postTeams', methods=['POST']) # Third button POST
def post_teams():

    teams.drop() # Drops the collection every new POST.
                 # Decided that it was for the best to make this collection ephemeral, it is cleaned every use

    try:
        start_filter = request.form['start_date']
        end_filter = request.form['end_date']
        start_date = convertDate(start_filter)
        end_date = convertDate(end_filter)

        df = leaguegamefinder.LeagueGameFinder(
                date_from_nullable=start_date, date_to_nullable=end_date
                ).get_data_frames()[0]
    
    except:
        return "Please enter a date in the following format: YYYY-MM-DD"

    item_doc = teamsStats(df).to_dict(orient='records')

    teams.insert_many(item_doc)

    df = pd.DataFrame(teams.find({}, {'_id': False}))


    df_csv = df.to_csv(None, sep=",")
    output = make_response(df_csv)
    output.headers["Content-Disposition"] = f"attachment; filename={start_filter}_to_{end_filter}_report.csv"
    output.headers["Content-type"] = "text/csv"
    return output



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("FLASK_SERVER_PORT", 9090), debug=True)