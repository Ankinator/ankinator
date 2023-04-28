import os
from typing import List, Tuple

from PIL.Image import Image
from pymongo import MongoClient
import pickle
from gridfs import GridFS

mongo_url = os.getenv('MONGO_URL')
client = MongoClient(mongo_url)
database = client["ankinator_database"]
grid_fs = GridFS(database)


def save_extraction_results(document_id: str, extracted_pages: List[Tuple[int, str, str, Image]]):
    serialized_object = pickle.dumps(extracted_pages)
    grid_fs.put(serialized_object, filename=document_id)
