from pymongo import MongoClient
from config.db import MONGO_URI, MONGO_DB_NAME

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def get_db():
    return db