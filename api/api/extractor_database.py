import os
import pickle
from typing import List, Tuple
import fpdf
from pymongo import MongoClient
from gridfs import GridFS
from fpdf import FPDF
import PIL

mongo_url = os.getenv('MONGO_URL')
client = MongoClient(mongo_url)
database = client["ankinator_database"]

grid_fs = GridFS(database)


def load_processed_pdf_document(document_id: str) -> fpdf.FPDF:
    file_object = grid_fs.get_last_version(filename=document_id)
    result = file_object.read()
    extracted_pages: List[Tuple[int, str, str, PIL.Image]] = pickle.loads(result)

    pdf = FPDF()
    for page_number, pdf_text, ocr_text, extracted_image in extracted_pages:
        pdf.add_page(format=(extracted_image.width, extracted_image.height))
        pdf.image(extracted_image, 0, 0, pdf.w, pdf.h)

    return pdf
