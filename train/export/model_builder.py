import torch

from train.configs.utils import load
from train.model.cats_model import HappyWhaleModel


class ModelBuilder:
    def __init__(self, config_name: str, model_name: str=""):
        self.model_name = model_name
        self.config_name = config_name
        self.config = load(self.config_name).model_config
        self.model_mapping = {"classificator": HappyWhaleModel, "detection": ""}

    def build_trained_model(self):
        self.model = self.model_mapping[self.model_name](self.config, torch.device('cpu'), is_train_stage=False)
        self.model.eval()
        return self.model
