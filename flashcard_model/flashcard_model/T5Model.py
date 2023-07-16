from typing import List, Tuple

import torch
from PIL.Image import Image
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from constants import T5_HUGGINGFACE_MODEL_NAME, TORCH_DEVICE
from flashcard_model.Model import Model


class T5Model(Model):

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(T5_HUGGINGFACE_MODEL_NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(T5_HUGGINGFACE_MODEL_NAME)

    def model_forward(self, extracted_pages: List[Tuple[int, str, str, Image]]) -> List[Tuple[int, List[str]]]:
        result = []
        for page_number, pdf_text, ocr_text, extracted_image in extracted_pages:
            generated_question = self.generate_question(pdf_text)
            result.append((page_number, [generated_question]))
        return result

    def generate_question(self, text):
        text = "Generate a question for this text: " + text
        tokenized_input = self.tokenizer.encode(text, return_tensors="pt", truncation=True, padding=True)
        tokenized_input = tokenized_input.to(TORCH_DEVICE)

        with torch.no_grad():
            output = self.model.generate(tokenized_input)
            question = self.tokenizer.decode(output[0], skip_special_tokens=True)

        return question
