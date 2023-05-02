from abc import ABC, abstractmethod
from typing import List, Tuple
from PIL.Image import Image

from flashcard_model.database_functions import add_model_result_to_document


class Model(ABC):
    @abstractmethod
    def model_forward(self, extracted_pages: List[Tuple[int, str, str, Image]]) -> List[Tuple[int, List[str]]]:
        pass

    def __call__(self, document_id: str, extracted_pages: List[Tuple[int, str, str, Image]]):
        model_result: List[Tuple[int, List[str]]] = self.model_forward(extracted_pages)
        add_model_result_to_document(document_id, model_result)
