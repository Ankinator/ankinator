import os
from typing import List, Tuple
from pymongo import MongoClient
from pydantic import BaseModel
import uuid
import time

mongo_url = os.getenv('MONGO_URL')
client = MongoClient(mongo_url)
database = client["ankinator_database"]

demo_user = {
    "username": "ankinator",
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
    "disabled": False,
    "model_results": {}
}

time.sleep(1)

existing_user = database["user"].find_one({"username": "ankinator"})
if existing_user is None:
    database["user"].insert_one(demo_user)

database["user"].create_index("username", unique=True)


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    model_results: dict[str, List[Tuple[int, List[str]]] | None] = {}


class UserInDB(User):
    hashed_password: str


def get_user(username: str):
    user = database["user"].find_one({"username": username})
    if user is not None:
        return UserInDB(**user)


def add_model_result_to_document(document_id: str, result: List[Tuple[int, List[str]]]):
    user = database["user"].find_one({"model_results": {"$elemMatch": {"document_id": document_id}}})
    if user is not None:
        user = UserInDB(**user)
        if document_id in user.model_results:
            user.model_results[document_id] = result
            save_user(user)


def create_model_result_placeholder_for_user(username: str) -> str:
    user = database["user"].find_one({"username": username})
    if user is not None:
        user = UserInDB(**user)
        document_id = str(uuid.uuid4())
        user.model_results[document_id] = None
        save_user(user)
        return document_id


def save_user(user: UserInDB):
    database["user"].update_one(filter={"username": user.username}, update={"$set": user.dict()}, upsert=True)
