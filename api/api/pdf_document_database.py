import uuid

from api.database_util import get_mongo_db_database

database = get_mongo_db_database()


def save_pdf_file(pdf_file: bytes, pdf_document_name: str, username: str):
    pdf_document_id = str(uuid.uuid4())
    try:
        existing_document = database["pdf_document"].find_one({'pdf_document_name': pdf_document_name})
        if existing_document:
            if existing_document["username"] == username:
                print(f"Document with file name '{pdf_document_name}' and id {existing_document['pdf_document_id']} "
                      f"already exists.")
                return {"pdf_document_id": existing_document['pdf_document_id']}

        document = {
            "pdf_document_id": pdf_document_id,
            "pdf_document_name": pdf_document_name,
            "pdf_document_file": pdf_file,
            "username": username
        }
        database["pdf_document"].insert_one(document)
        print("PDF file saved to MongoDB successfully.")
        return {"pdf_document_id": pdf_document_id}
    except Exception as e:
        print(f"Error: {e}")
        return {"PDF could not be saved"}


def load_pdf_file(pdf_document_id: str) -> (bytes, str):
    pdf_document = database["pdf_document"].find_one({'pdf_document_id': pdf_document_id})
    return pdf_document["pdf_document_file"], pdf_document["pdf_document_name"]


def get_all_documents_for_user(username: str):
    query = {"username": username}
    projection = {"pdf_document_id": 1, "pdf_document_name": 1, "_id": 0}
    result = database["pdf_document"].find(query, projection=projection)
    result_list = [pdf_document for pdf_document in result]
    return result_list
