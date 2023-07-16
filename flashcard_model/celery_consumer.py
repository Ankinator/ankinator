from celery import Celery

from constants import DEMO_MODEL_KEY, CHAT_GPT_MODEL_KEY, T5_MODEL_KEY, MODEL_KEYS
from flashcard_model.T5Model import T5Model
from flashcard_model.database_functions import load_extracted_pages, set_document_to_failed
from flashcard_model.ChatGPTModel import ChatGPTModel
from flashcard_model.DemoModel import DemoModel

app = Celery('flashcard_model')
app.conf.task_default_queue = "flashcard_model"
app.conf.task_default_routing_key = "flashcard_model.task"
app.conf.accept_content = ["json", "pickle"]


@app.task(name="generate_flashcards")
def generate_flashcard(extraction_result):
    extracted_pages = load_extracted_pages(extraction_result["document_id"])
    model_name = extraction_result["model"]

    if model_name is None:  # Use Demo model if no model name is provided
        model_name = DEMO_MODEL_KEY
        print(f"Document {extraction_result['document_id']} No model name provided. Demo model will be used")

    model_functions = {
        DEMO_MODEL_KEY: DemoModel,
        CHAT_GPT_MODEL_KEY: ChatGPTModel,
        T5_MODEL_KEY: T5Model
    }

    if model_name in MODEL_KEYS:
        print(f"Document {extraction_result['document_id']} {model_name} model used")
        model_function = model_functions.get(model_name)
        if model_function:
            model_instance = model_function()
            model_instance(extraction_result['document_id'], model_name, extracted_pages)
            print(f"Document {extraction_result['document_id']} flashcard generation finished")
        else:
            set_document_to_failed(extraction_result['document_id'])
            print(
                f"Document {extraction_result['document_id']} flashcard generation failed: {model_name} model not "
                f"implemented")
    else:
        set_document_to_failed(extraction_result['document_id'])
        print(f"Document {extraction_result['document_id']} flashcard generation failed: Model name not in MODEL_KEYS "
              f"list")
