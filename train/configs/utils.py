from train.configs.base_config import Config
from train.configs.resnet18_config import resnet18_config


mapping = {resnet18_config.name: resnet18_config}
def load(congig_name: str) -> Config:
    return mapping.get(congig_name)
