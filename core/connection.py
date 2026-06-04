from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config.db import MONGO_URI, MONGO_DB_NAME

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[MONGO_DB_NAME]
except ConnectionFailure as e:
    raise RuntimeError(f"No se pudo conectar a MongoDB: {e}")

def get_db():
    return db
