from typing import List, Tuple, Union
from pydantic import BaseModel
import uuid
import time
from api.database_util import get_mongo_db_database

database = get_mongo_db_database()

demo_user = {
    "username": "ankinator",
    "full_name": "Test User",
    "email": "testuser@example.com",
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
    # dict[document_id, dict[model_name, List[Tuple[page_number, list of questions]] | model_name | list of pages]]
    model_results: dict[
        str, Union[dict[str, Union[List[Tuple[int, List[str]]] | str | List[int] | None]] | None | str]] = {}


class UserInDB(User):
    hashed_password: str


def get_user(username: str):
    user = database["user"].find_one({"username": username})
    if user is not None:
        return UserInDB(**user)


def create_model_result_placeholder_for_user(username: str, pdf_document_id: str) -> str:
    user = database["user"].find_one({"username": username})
    if user is not None:
        user = UserInDB(**user)
        result_id = str(uuid.uuid4())
        user.model_results[result_id] = {
            "model_name": None,
            "pdf_document_id": pdf_document_id,
            "pages": None,
            "timestamp": None,
            "model_result": None
        }
        save_user(user)
        return result_id


def save_user(user: UserInDB):
    database["user"].update_one(filter={"username": user.username}, update={"$set": user.dict()}, upsert=True)


def update_user_result(result_id: str, pages: List[int] = None, model_result=None):
    user = database["user"].find_one({"model_results." + result_id: {"$exists": True}})
    if user is not None:
        if pages:
            user["model_results"][result_id]["pages"] = pages
        if model_result:
            user["model_results"][result_id]["model_result"] = model_result
        database["user"].update_one({"username": user["username"]}, {"$set": user})
