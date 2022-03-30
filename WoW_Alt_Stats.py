# An application to fetch data about characters who's currently on the World of Warcraft 3v3 Arena Leaderboards.
# The data is stored on a local MongoDB, at the moment.

# API Rate Limits: 36,000 requests per hour, 100 requests per second.

import pymongo
import requests
import json
import time
from pymongo import MongoClient
from bson.objectid import ObjectId

# Database Connection & Client-handler.
connection = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
client = MongoClient(connection)
db = client.test
apiCred = client.config.api
players = db.players

# Gets the API-credentials and access token from the database.
for cred in client.config.api.find({"_id": ObjectId("62436f706bb2e62e3b8def90")}):
   CLIENT_ID = cred["clientID"]
   CLIENT_SECRET = cred["clientSecret"]

for cred in client.config.api.find({"_id": ObjectId("624390182311edb36b698ac6")}):
   CLIENT_ACCESSTOKEN = cred["accessToken"]
  

# Updates the Access Token in the Database.
def updateAccessToken(accessToken):
    updateValue = {"$set": {"accessToken": accessToken}}
    apiCred.update_one({"accessToken": ""}, updateValue)

# Generates a new Access Token from the Battle.Net API.
# An Access Token is valid for 24hrs and required to reach certain endpoints.
def generateAccessToken():
     tokenUri = "https://eu.battle.net/oauth/token"
     params = {'grant_type': 'client_credentials',}
     response = requests.post(tokenUri, data=params, auth=(CLIENT_ID, CLIENT_SECRET))
     
     # Updates if a new token could be aquirred.
     if "access_token" in response.text:
         print("Token Aquirred! Status Code: ")
         response_dict = json.loads(response.text)
         updateAccessToken(response_dict['access_token']) 
     else:
        print("Token could not be aquirred!  Status Code: ")
     
     print(response.text + "\n")

# Adds the character information to the Database.
def addCharacterInformation():
    # Calls the Leaderboard Endpoint to access the names and realms of characters currently on the leaderboard.
    response = requests.get("https://us.api.blizzard.com/data/wow/pvp-season/32/pvp-leaderboard/3v3?namespace=dynamic-us&locale=en_US&access_token={}".format(CLIENT_ACCESSTOKEN))
    response_dict = json.loads(response.text)
    
    # Calls the Character Equipment Summary endpoint for every unique character to fetch data about the characters equipment and add it to the database.
    for character in response_dict["entries"]:

        name = character["character"]["name"].lower()
        realm = character["character"]["realm"]["slug"] 
        response = requests.get("https://us.api.blizzard.com/profile/wow/character/{realm}/{name}/equipment?namespace=profile-us&locale=en_US&access_token={client_accesstoken}".format( realm = realm, 
                                                                                                                                                                                         name = name, 
                                                                                                                                                                                         client_accesstoken = CLIENT_ACCESSTOKEN))
        result = players.insert_one(json.loads(response.text))
        print("Added: " + name + " to the database!") 
        

generateAccessToken()
addCharacterInformation()