from celery import Celery

from flashcard_model.database_functions import load_extracted_pages
from flashcard_model.ChatGPTModel import ChatGPTModel
from flashcard_model.DemoModel import DemoModel

app = Celery('flashcard_model')
app.conf.task_default_queue = "flashcard_model"
app.conf.task_default_routing_key = "flashcard_model.task"
app.conf.accept_content = ["json", "pickle"]

CHAT_GPT_MODEL_KEY = "CHAT_GPT"
DEMO_MODEL_KEY = "DEMO"
T5_MODEL_KEY = "T5"
MODEL_KEYS = [CHAT_GPT_MODEL_KEY, DEMO_MODEL_KEY, T5_MODEL_KEY]


@app.task(name="generate_flashcards")
def generate_flashcard(extraction_result):
    extracted_pages = load_extracted_pages(extraction_result["document_id"])
    model_name = extraction_result["model"]

    if model_name is None:  # Use Demo model if no model name is provided
        model_name = DEMO_MODEL_KEY
        print(f"Document {extraction_result['document_id']} No model name provided. Demo model will be used")

    if model_name in MODEL_KEYS:
        print(f"Document {extraction_result['document_id']} {model_name} model used")
        if model_name == DEMO_MODEL_KEY:
            demo_model = DemoModel()
            demo_model(extraction_result['document_id'], extracted_pages)
        elif model_name == CHAT_GPT_MODEL_KEY:
            gpt_model = ChatGPTModel()
            gpt_model(extraction_result['document_id'], extracted_pages)
        elif model_name == T5_MODEL_KEY:
            # t5_model = T5Model()
            # t5_model(extraction_result['document_id'], extracted_pages)
            print(f"Document {extraction_result['document_id']} T5 model not implemented")

        print(f"Document {extraction_result['document_id']} flashcard generation finished")
    else:
        print(f"Document {extraction_result['document_id']} flashcard generation failed: Model name not in MODEL_KEYS "
              f"list")
