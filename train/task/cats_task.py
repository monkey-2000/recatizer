import timm
from train.task.base_task import BaseTask
from train.configs.base_config import Config
from train.dataset.cat_dataset import CatsDataset
from train.dataset.transforms import get_transforms_train


class CatsTask(BaseTask):
    def __init__(self, config: Config):
        super().__init__("classificator", config)
        self.task_config = self.config.task_config
        self.dataset_config = self.config.dataset_config



    def get_train_dataset(self):
        return CatsDataset(self.dataset_config.train_path, get_transforms_train(self.image_size))

    def get_val_dataset(self):
        return CatsDataset(self.dataset_config.train_path, get_transforms_train(self.image_size))


    def get_model(self):
        model  = timm.create_model(self.task_config.model_name, pretrained=True, drop_rate=0.0)
        return model
