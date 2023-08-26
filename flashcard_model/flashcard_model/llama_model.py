from typing import List, Tuple

import torch
from PIL.Image import Image
from transformers import AutoTokenizer, AutoModelForCausalLM

from constants import LLAMA_HUGGINGFACE_MODEL_NAME, TORCH_DEVICE
from flashcard_model.Model import Model


def prompt_gen(text):
    prompt = f"""### Instruction:
    Use the Input below to create a question, which could be asked in an exam.

    ### Input:
    {text}

    ### Response:
    """

    return prompt


class LLAMAModel(Model):

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(LLAMA_HUGGINGFACE_MODEL_NAME)
        self.model = AutoModelForCausalLM.from_pretrained(LLAMA_HUGGINGFACE_MODEL_NAME)
        self.model = self.model.to(TORCH_DEVICE)
        self.model = self.model.eval()

    def model_forward(self, extracted_pages: List[Tuple[int, str, str, Image]]) -> List[Tuple[int, List[str]]]:
        result = []
        for page_number, pdf_text, ocr_text, extracted_image in extracted_pages:
            generated_question = self.generate_question(pdf_text)
            result.append((page_number, [generated_question]))
        return result

    def generate_question(self, text):
        text = prompt_gen(text)
        input_ids = self.tokenizer(text, return_tensors="pt", max_length=512, padding=True, truncation=True).input_ids
        input_ids = torch.tensor(input_ids)
        input_ids = input_ids.to(TORCH_DEVICE)

        with torch.no_grad():
            output = self.model.generate(input_ids=input_ids, max_new_tokens=50, do_sample=True, top_p=0.9,
                                         temperature=0.9)
            question = self.tokenizer.batch_decode(output.detach(), skip_special_tokens=True)[0][len(text):]

        return question
