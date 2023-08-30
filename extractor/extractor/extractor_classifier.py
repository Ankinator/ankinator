from tempfile import SpooledTemporaryFile
from typing import List

from pypdfium2 import PdfDocument
from torchvision.models import efficientnet_v2_m
import torch
import torch.nn as nn
import PIL
import torch.nn.functional as F
from torchvision import transforms

from extractor.constants import EXTRACTOR_CLASSIFIER_MODEL_PATH


class ExtractorClassifier:
    def __init__(self):
        self.model = EfficientNetModel()
        self.model.load_state_dict(torch.load(EXTRACTOR_CLASSIFIER_MODEL_PATH, map_location=torch.device("cpu")))
        self.model.eval()
        self.to_tensor = transforms.ToTensor()
        self.resize_image = transforms.Resize((256, 256), antialias=True)

    def image_preprocessing(self, image: PIL.Image):
        image_tensor = self.to_tensor(image)
        image_tensor = self.resize_image(image_tensor)
        image_tensor = image_tensor / 255
        return image_tensor

    def is_page_relevant(self, image: PIL.Image) -> bool:
        image = self.image_preprocessing(image)
        image = image.unsqueeze(dim=0)
        output_probabilities = self.model(image)
        _, prediction = torch.max(output_probabilities.data, 1)
        if prediction == 0:
            return True
        else:
            return False

    def classify_document(self, pdf_file: SpooledTemporaryFile) -> List[int]:
        pdf_document = PdfDocument(pdf_file)
        pages: List[int] = []
        for page_index, page_content in enumerate(pdf_document, 1):
            bitmap = page_content.render(scale=1)
            if self.is_page_relevant(bitmap.to_pil()):
                pages.append(page_index)
        return pages


class EfficientNetModel(nn.Module):
    def __init__(self):
        super(EfficientNetModel, self).__init__()
        self.efficientnet_model = efficientnet_v2_m()
        num_features = self.efficientnet_model.classifier[1].in_features
        new_classifier_layer = torch.nn.Linear(num_features, 2)
        self.efficientnet_model.classifier[1] = new_classifier_layer

    def forward(self, x):
        output_logits = self.efficientnet_model(x)
        output_probabilities = F.softmax(output_logits, dim=1)
        print(output_probabilities)
        return output_probabilities
