import os
from typing import List, Tuple
from pymongo import MongoClient

mongo_url = os.getenv('MONGO_URL')
client = MongoClient(mongo_url)
database = client["ankinator_database"]


def add_model_result_to_document(document_id: str, result: List[Tuple[int, List[str]]]):
    user = database["user"].find_one({"model_results." + document_id: {"$exists": True}})
    if user is not None:
        user["model_results"][document_id] = result
        database["user"].update_one({"username": user["username"]}, {"$set": user})