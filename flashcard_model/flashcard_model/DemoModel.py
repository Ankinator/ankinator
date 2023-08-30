from typing import List, Tuple

from PIL.Image import Image

from flashcard_model.Model import Model


class DemoModel(Model):
    def model_forward(self, extracted_pages: List[Tuple[int, str, str, Image]]) -> List[Tuple[int, List[str]]]:
        # Just save some data for testing purposes
        return [(item[0], [item[1]]) for item in extracted_pages]
