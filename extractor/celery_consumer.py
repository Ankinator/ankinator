from celery import Celery

from extractor.pdf_extractor import extract_text
from extractor.database_functions import add_model_result_to_document

app = Celery('extractor')
app.conf.task_default_queue = "extractor"
app.conf.task_default_routing_key = "extract.task"
app.conf.accept_content = ["json", "pickle"]


@app.task(name="extract_text_from_pdf")
def task_extract_text_from_pdf(document):
    pages = extract_text(document["pdf_file"])
    add_model_result_to_document(document["document_id"], [(1, [item[0]]) for item in pages])
    print(f"Document {document['document_id']} extraction finished")
