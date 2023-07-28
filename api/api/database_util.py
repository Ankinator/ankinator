import os

from pymongo import MongoClient


def get_mongo_db_database():
    mongo_url = os.getenv('MONGO_URL')
    client = MongoClient(mongo_url)
    database = client["ankinator_database"]
    return database
