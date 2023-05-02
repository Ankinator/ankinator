from typing import List, Tuple

from PIL.Image import Image

from flashcard_model.Model import Model


class ChatGPTModel(Model):
    def model_forward(self, extracted_pages: List[Tuple[int, str, str, Image]]) -> List[Tuple[int, List[str]]]:
        # Implement chatgpt model here
        pass
