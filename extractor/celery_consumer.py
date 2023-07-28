from celery import Celery

from extractor.extractor_database import save_extraction_results, add_extraction_classification_to_document

from extractor.extractor_classifier import ExtractorClassifier
from extractor.pdf_extractor import extract_text

app = Celery('extractor')
app.conf.task_default_queue = "extractor"
app.conf.task_default_routing_key = "extract.task"
app.conf.accept_content = ["json", "pickle"]


@app.task(name="extract_text_from_pdf")
def task_extract_text_from_pdf(document):
    extracted_pages = extract_text(pdf_file=document["pdf_file"], pages_to_extract=document["pages"])
    save_extraction_results(document["result_id"], extracted_pages)
    extraction_result = {
        "result_id": document["result_id"],
        "pdf_document_id": document["pdf_document_id"],
        "model": document["model"],
        "domain": document["domain"]
    }
    app.send_task("generate_flashcards", queue="flashcard_model", routing_key="flashcard_model.task",
                  kwargs={"extraction_result": extraction_result}, serializer="pickle")
    print(f"Document result -{document['result_id']}- extraction finished")


@app.task(name="classify_pdf_document_page_relevance")
def task_classify_pdf_document_page_relevance(document):
    extractor_classifier = ExtractorClassifier()
    relevant_pages = extractor_classifier.classify_document(document["pdf_file"])
    add_extraction_classification_to_document(document["result_id"], relevant_pages)
    print(f"Document result -{document['result_id']}- extractor classifier finished")
