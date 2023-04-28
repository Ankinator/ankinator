from celery import Celery

from extractor.database_functions import save_extraction_results
from extractor.pdf_extractor import extract_text

app = Celery('extractor')
app.conf.task_default_queue = "extractor"
app.conf.task_default_routing_key = "extract.task"
app.conf.accept_content = ["json", "pickle"]


@app.task(name="extract_text_from_pdf")
def task_extract_text_from_pdf(document):
    pages = extract_text(document["pdf_file"])
    save_extraction_results(document["document_id"], pages)
    extraction_result = {
        "document_id": document["document_id"]
    }
    app.send_task("generate_flashcards", queue="flashcard_model", routing_key="flashcard_model.task",
                  kwargs={"extraction_result": extraction_result}, serializer="pickle")
    print(f"Document {document['document_id']} extraction finished")
