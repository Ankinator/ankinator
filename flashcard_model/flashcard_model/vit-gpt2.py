from PIL import Image
from typing import List, Tuple

from flashcard_model.Model import Model
from constants import TORCH_DEVICE
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer


class VitGPT2Model(Model):

    def __init__(self, max_length=16, num_beams=4):
        # TODO: Use Fine-Tuned Weights
        self.model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        self.max_length = max_length
        self.num_beams = num_beams
        self.device = TORCH_DEVICE

    def model_forward(self, extracted_pages: List[Tuple[int, str, str, Image]]) -> List[Tuple[int, List[str]]]:
        gen_kwargs = {"max_length": self.max_length, "num_beams": self.num_beams}

        images = [image for _, _, _, image in extracted_pages]
        pixel_values = self.feature_extractor(images=images, return_tensor="pt").pixel_values
        pixel_values = pixel_values.to(self.device)

        output_ids = self.model.generate(pixel_values, **gen_kwargs)

        preds = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        preds = [(extracted_pages[i][0], [pred]) for i, pred in enumerate(preds)]

        return preds
