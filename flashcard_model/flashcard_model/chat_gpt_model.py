from typing import Tuple, List

from PIL.Image import Image

from flashcard_model.database_functions import add_model_result_to_document


# result type: List[Tuple[int, List[str]]]
def generate_chat_gpt_questions(document_id: str, extracted_pages: List[Tuple[int, str, str, Image]]):
    # Save results for demo purposes
    add_model_result_to_document(document_id, [(item[0], [item[1]]) for item in extracted_pages])
    # Real use case example:
    # chat_gpt_generated_questions: List[Tuple[int, List[str]]] = chat_gpt.forward(extracted_pages)
    # add_model_result_to_document(document_id, chat_gpt_generated_questions)