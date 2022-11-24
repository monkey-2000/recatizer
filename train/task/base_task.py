import time
from abc import abstractmethod, ABC
from datetime import datetime
from train.configs.base_config import Config, DatasetConfig, TaskConfig
from torch import nn
from torch.utils.data.dataloader import DataLoader
from torch.utils.data.dataset import Dataset

from train.optimizers.base_criterion import BaseLossAndMetricCriterion
from train.task.task_executor import TaskRunner


class BaseTask(ABC):
    """
    Task is an abstraction to create dataset, loader, estimator, calculators and so on -
    all the things needed to run training or services. Also it's responsible on saving results to s3.
    """

    def __init__(self, task_name: str, config: Config):
        self.task_name = task_name
        self.starttime = time.time()
        self.startdate = datetime.now().strftime("%Y-%m-%d")
        self.config = config
        self.image_size = config.image_size
        self._lh = None
        self.task_config: TaskConfig = None
        self.dataset_config: DatasetConfig = None

        self.save_folder = self.config.save_folder

    @abstractmethod
    def get_train_dataset(self) -> Dataset:
        raise NotImplementedError

    @abstractmethod
    def get_val_dataset(self) -> Dataset:
        raise NotImplementedError


    def get_train_loaders(self):
        dataset = self.get_train_dataset()
        return DataLoader(dataset, num_workers=0, shuffle=True, drop_last=True, batch_size=self.dataset_config.batch_size)

    def get_val_loaders(self):
        dataset = self.get_val_dataset()
        return DataLoader(dataset, num_workers=0, shuffle=False, drop_last=True, batch_size=self.dataset_config.batch_size)


    def get_model(self) -> nn.Module:
        raise NotImplementedError

    @abstractmethod
    def build_criterion(self) -> BaseLossAndMetricCriterion:
        """This method should build calculator for all tasks."""
        raise NotImplementedError

    def get_runner(self, model: nn.Module) -> TaskRunner:
        criterion = self.build_criterion()
        return TaskRunner(
            model,
            criterion,
            self.config.optimizer,
            self.config.model_config,
            self.config.save_folder
        )

    def fit(self):
        """
        run training using selected config
        """
        model = self.get_model()
        train_loaders = self.get_train_loaders()
        val_loaders = self.get_val_loaders()

        loaders = {"train": train_loaders, "val": val_loaders}
        self.get_runner(model).fit(loaders)


