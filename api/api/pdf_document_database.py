import uuid

from pypdfium2 import PdfDocument

from api.database_util import get_mongo_db_database

database = get_mongo_db_database()


def save_pdf_file(pdf_file: bytes, pdf_document_name: str, username: str):
    pdf_document_id = str(uuid.uuid4())
    try:
        existing_document = database["pdf_document"].find_one({'pdf_document_name': pdf_document_name})
        if existing_document:
            if existing_document["username"] == username:
                print(f"Document with file name '{pdf_document_name}' already exists.")
                return {f"Document with file name '{pdf_document_name}' already exists."}

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

#faee0e7b-4e7c-4ed8-85e1-51011e3f6941
def load_pdf_file(pdf_document_id: str) -> (bytes, str):
    pdf_document = database["pdf_document"].find_one({'pdf_document_id': pdf_document_id})
    return pdf_document["pdf_document_file"], pdf_document["pdf_document_name"]
