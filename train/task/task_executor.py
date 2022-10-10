import math
import os
import torch
from tqdm import tqdm
from typing import Dict, Union, Optional, List, Iterable, Tuple
from collections import OrderedDict
from torch.utils.data.dataloader import DataLoader
from torch import optim
from torch.optim import lr_scheduler
import warnings
import torch.nn as nn
from train.configs.base_config import OptimizerParams, LearningSchedule, ModelConfig
from train.metrics.base_criterion import BaseLossAndMetricCriterion
from timm.utils import AverageMeter
from numbers import Number

from train.utils import model_saver


class MetricsCollection:
    """
    Some callbacks use this class to get information about metrics
    """

    def __init__(self):
        self.stop_training = False
        self.best_loss = float('inf')
        self.best_epoch = 0
        self.train_metrics = {}
        self.val_metrics = {}


class TaskRunner:

    def __init__(self, model: nn.Module,
                 criterion: BaseLossAndMetricCriterion,
                 optimizer_config: OptimizerParams,
                 model_config: ModelConfig,
                 save_folder: str,
                 device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')):

        self.device = device
        self.model = model
        self.model_config = model_config
        self.model.to(self.device)
        self.criterion = criterion
        self.avg_meters = {}
        self.optimizer = self._create_optimizer(optimizer_config)

        self.save_folder = save_folder
        self.weights_save_path = os.path.join('results', 'weights', self.save_folder)
        self.logs_save_path = os.path.join('results', 'logs', self.save_folder)
        self.lr_scheduler = self._create_scheduler(optimizer_config.schedule)
       # self.callbacks = CallbacksCollection(self._create_basic_callbacks())
        self.lr = optimizer_config.lr
        self.separate_step = True

        self.nb_epoch = optimizer_config.epochs
        self.warmup_epoch = 0
        self.start_epoch = 0

        self.step_mode_schedule = False
        self.metrics_collection = MetricsCollection()
        self.model_input_fields = ['image', 'label']

    def _create_optimizer(self, optimizer_config: OptimizerParams) -> torch.optim.Optimizer:
        """
        available options - SGD and Adam. See pytorch documentation.
        """
        params = self.model.parameters()
        learning_rate = optimizer_config.lr
        weight_decay = optimizer_config.wd
        if optimizer_config.type == 'sgd':
            optimizer = optim.SGD(params,
                                  lr=learning_rate,
                                  weight_decay=weight_decay)
        elif optimizer_config.type == 'adam':
            optimizer = optim.Adam(params,
                                   lr=learning_rate,
                                   weight_decay=weight_decay)
        else:
            raise KeyError("unrecognized optimizer type. Please pick SGD or Adam")
        return optimizer

    def _create_scheduler(self, scheduler_config: LearningSchedule) -> lr_scheduler._LRScheduler:
        """
        see pytorch lr_scheduler section for details
        :return:
        """
        if scheduler_config.type == "step":
            scheduler = lr_scheduler.StepLR(self.optimizer, **scheduler_config.params)
        elif scheduler_config.type == "multistep":
            scheduler = lr_scheduler.MultiStepLR(self.optimizer, **scheduler_config.params)
        elif scheduler_config.type == "exponential":
            scheduler = lr_scheduler.ExponentialLR(self.optimizer, **scheduler_config.params)

        else:
            scheduler = lr_scheduler.LambdaLR(self.optimizer, lambda epoch: 1.0)

        return scheduler



    def _run_one_epoch(self, epoch: int, loaders: Dict[str, DataLoader],
                       training: bool = True):

        mode = 'train' if training else 'val'

        mode_loader = loaders[mode]
        steps_per_epoch = len(mode_loader)
        loss_meter = AverageMeter()
        self.avg_meters = {"loss": loss_meter}

        iterator = tqdm(mode_loader)
        for batch_number, tasks_data  in enumerate(iterator):
            self._make_step(tasks_data, epoch, batch_number, steps_per_epoch, training)

            avg_metrics = {k: f"{v.avg:.4f}" for k, v in self.avg_meters.items()}
            iterator.set_postfix({"lr": float(self.lr_scheduler.get_last_lr()[-1]),
                                  "epoch": epoch,
                                  **avg_metrics
                                  })
            if training:
                self.lr_scheduler.step()
        return {k: v for k, v in self.avg_meters.items()}



    def _make_step(self, data: Dict[str, torch.Tensor], epoch, batch_number,
                   steps_per_epoch, training: bool):
        """
        Make step on single batch inside of this method. In case of multitasking - just batch after batch.
        :param tasks_data: name of task and dict with batch
        """
        if training:
            self.optimizer.zero_grad()

        model_input_fields = self.model_input_fields
        input = [data[key] for key in model_input_fields]
        input = [i.to(self.device) for i in input]

        if len(input) != 1:
            warnings.warn("make sure your model has list of inputs")
        model_output = self.model(*input, training)
        assert isinstance(model_output, dict), "Model output must be dict because model exporting/serving relies on it"
        loss = self.criterion.calculate(model_output, data, training)
        self.avg_meters['loss'].update(loss.item(), input[0].size(0))
        if math.isnan(loss.item()) or math.isinf(loss.item()):
            raise ValueError("NaN loss !!")
        if training:
            loss.backward()

        if training:
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.)
            self.optimizer.step()

    def fit(self,
            loaders: Dict[str, Union[Dict[str, DataLoader], DataLoader]]):

        for epoch in range(self.start_epoch, self.nb_epoch):
            self.model.train()
            self.metrics_collection.train_metrics = self._run_one_epoch(epoch, loaders, training=True)
            model_saver._save_last(model=self.model, current_epoch=epoch,
                                   current_metrics=self.metrics_collection.train_metrics, config=self.model_config)
            if epoch >= self.warmup_epoch and not self.step_mode_schedule:
                self.lr_scheduler.step(epoch)

            self.model.eval()
            with torch.no_grad():
                self.metrics_collection.val_metrics = self._run_one_epoch(epoch, loaders, training=False)


            if self.metrics_collection.stop_training:
                break
