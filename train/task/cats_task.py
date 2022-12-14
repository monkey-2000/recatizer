import timm
import torch
import pandas as pd
from train.optimizers.base_criterion import BaseLossAndMetricCriterion
from train.optimizers.cross_entropy import ClsLossAndMetricCriterion
from train.model.cats_model import HappyWhaleModel
from train.optimizers.metrics import PRMetric, AccuracyMetric, F1Score
from train.task.base_task import BaseTask
from train.configs.base_config import Config
from train.dataset.cat_dataset import CatsDataset
from train.dataset.transforms import get_transforms_train


class CatsTask(BaseTask):
    def __init__(self, wandb_run, config: Config):
        super().__init__(wandb_run, "classificator", config)
        self.task_config = self.config.task_config
        self.dataset_config = self.config.dataset_config
        self.model_config = self.config.model_config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def get_train_dataset(self):
        return CatsDataset(self.dataset_config.base_path, self.dataset_config.train_path, get_transforms_train(self.image_size))

    def get_val_dataset(self):
        return CatsDataset(self.dataset_config.base_path, self.dataset_config.train_path, get_transforms_train(self.image_size))

    def build_criterion(self) -> BaseLossAndMetricCriterion:
        metrics = [PRMetric(self.model_config.num_classes), AccuracyMetric(), F1Score(self.model_config.num_classes)]
        return ClsLossAndMetricCriterion(device=self.device, metrics=metrics)

    def get_model(self):
        df = pd.read_csv(self.dataset_config.train_path)
        id_class_nums = df.cat_id.value_counts().sort_index().values
        model = HappyWhaleModel(self.model_config, self.device, is_train_stage=True, id_class_nums=id_class_nums)
        return model
