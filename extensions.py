from flask_bcrypt import Bcrypt
from pymongo import MongoClient

bcrypt = Bcrypt()
uri = "mongodb://id:pw@3.39.11.17/"
mongo_client = MongoClient(uri, 27017)
db = mongo_client["user_db"]
users_collection = db["users"]