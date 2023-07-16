from torchvision.models import resnet50
import torch
import torch.nn as nn
import PIL
import torch.nn.functional as F
from torchvision import transforms

from extractor.constants import EXTRACTOR_CLASSIFIER_MODEL_PATH


class ExtractorClassifier:
    def __init__(self):
        self.model = Resnet50Model()
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
        print(output_probabilities)
        _, prediction = torch.max(output_probabilities.data, 1)
        return prediction


# Use ResNet50 model for now
class Resnet50Model(nn.Module):
    def __init__(self):
        super(Resnet50Model, self).__init__()
        self.resnet_model = resnet50()
        num_features = self.resnet_model.fc.in_features
        self.resnet_model.fc = nn.Linear(num_features, 2)

    def forward(self, x):
        output_logits = self.resnet_model(x)
        output_probabilities = F.softmax(output_logits, dim=1)
        return output_probabilities
