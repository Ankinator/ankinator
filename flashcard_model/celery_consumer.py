from celery import Celery

from flashcard_model.DemoModel import DemoModel
from flashcard_model.database_functions import load_extracted_pages
from flashcard_model.ChatGPTModel import ChatGPTModel

app = Celery('flashcard_model')
app.conf.task_default_queue = "flashcard_model"
app.conf.task_default_routing_key = "flashcard_model.task"
app.conf.accept_content = ["json", "pickle"]


@app.task(name="generate_flashcards")
def generate_flashcard(extraction_result):
    extracted_pages = load_extracted_pages(extraction_result["document_id"])
    demo_model = ChatGPTModel()
    demo_model(extraction_result['document_id'], extracted_pages)
    print(f"Document {extraction_result['document_id']} flashcard generation finished")
