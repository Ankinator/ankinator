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


# Add results to document with passed document_id
# Results is as list of tuples. Each tuple contains the page number (int) and the generated questions (List[str])
def add_model_result_to_document(document_id: str, result: List[Tuple[int, List[str]]]):
    user = database["user"].find_one({"model_results." + document_id: {"$exists": True}})
    if user is not None:
        user["model_results"][document_id] = result
        database["user"].update_one({"username": user["username"]}, {"$set": user})


def load_extracted_pages(document_id: str) -> List[Tuple[int, str, str, Image]]:
    file_object = grid_fs.get_last_version(filename=document_id)
    result = file_object.read()
    extracted_pages: List[Tuple[int, str, str, Image]] = pickle.loads(result)
    return extracted_pages