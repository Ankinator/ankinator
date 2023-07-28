import os
import pickle
from typing import List, Tuple

from PIL.Image import Image
from pymongo import MongoClient
from gridfs import GridFS

mongo_url = os.getenv('MONGO_URL')
client = MongoClient(mongo_url)
database = client["ankinator_database"]
grid_fs = GridFS(database)


def add_extraction_classification_to_document(result_id: str, relevant_pages: List):
    user = database["user"].find_one({"model_results." + result_id: {"$exists": True}})
    if user is not None:
        user["model_results"][result_id]["pages"] = relevant_pages
        database["user"].update_one({"username": user["username"]}, {"$set": user})


def save_extraction_results(result_id: str, extracted_pages: List[Tuple[int, str, str, Image]]):
    serialized_object = pickle.dumps(extracted_pages)
    grid_fs.put(serialized_object, filename=result_id)
