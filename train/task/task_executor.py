import math
import os
import torch
import wandb
from tqdm import tqdm
from typing import Dict, Union, List
from torch.utils.data.dataloader import DataLoader
import torchmetrics
import torch.nn as nn
from train.configs.base_config import OptimizerParams, ModelConfig
from train.optimizers.base_criterion import BaseLossAndMetricCriterion
from timm.utils import AverageMeter
from collections import defaultdict
from train.optimizers.optimizer_builder import OptimizerBuilder
from train.task.callbacks.base import CallbacksCollection, Callback
from train.task.callbacks.callbacks import TensorBoard, JsonMetricSaver, WanDBMetricSaver, WanDBModelSaver
from train.utils.checkpoint_utils import CheckpointHandler


class MetricsCollection:
    """
    Some callbacks use this class to get information about optimizers
    """

    def __init__(self):
        self.best_loss = float('inf')
        self.best_epoch = 0
        self.train_metrics = {}
        self.val_metrics = {}


class TaskRunner:

    def __init__(self, wandb_run, model: nn.Module,
                 criterion: BaseLossAndMetricCriterion,
                 optimizer_config: OptimizerParams,
                 model_config: ModelConfig,
                 save_folder: str,
                 test_every: int = 5,
                 device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')):

        self.wandb_run = wandb_run
        self.device = device
        self.test_every = test_every
        self.checkpoint_handler = CheckpointHandler(model_config)
        self.model = self._init_model(model)
        wandb.watch(self.model, criterion, log="all")
        self.model_config = model_config
        self.model.to(self.device)
        self.criterion = criterion
        self.avg_meters = defaultdict(AverageMeter)
        self.optimizer, self.lr_scheduler = OptimizerBuilder(optimizer_config).build(model)
        self.save_folder = save_folder
        self.weights_save_path = os.path.join('results', 'weights', self.save_folder)
        self.logs_save_path = os.path.join('results', 'logs', self.save_folder)
        self.metrics_collection = MetricsCollection()
        self.callbacks = CallbacksCollection(self._create_basic_callbacks())
        self.lr = optimizer_config.lr
        self.separate_step = True
        self.metric = torchmetrics.Accuracy()
        self.nb_epoch = optimizer_config.epochs
        self.warmup_epoch = 0
        self.start_epoch = 0

        self.step_mode_schedule = False
        self.model_input_fields = ['image', 'label']

    def _init_model(self, model: nn.Module):
        self.checkpoint_handler.load_checkpoint(model)
        return model

    def _create_basic_callbacks(self) -> List[Callback]:
        """
        model and checkpoint savers, tensorboard logs saver
        """
        callbacks = [
            TensorBoard(self.logs_save_path,
                        self.optimizer,
                        self.metrics_collection),
            JsonMetricSaver(self.logs_save_path,
                            self.optimizer,
                            self.metrics_collection),
            WanDBMetricSaver(self.wandb_run, self.optimizer,
                            self.metrics_collection),
            WanDBModelSaver(self.wandb_run, self.model)
        ]
        return callbacks

    def _run_one_epoch(self, epoch: int, loaders: Dict[str, DataLoader],
                       training: bool = True):

        mode = 'train' if training else 'val'

        mode_loader = loaders[mode]
        steps_per_epoch = len(mode_loader)

        iterator = tqdm(mode_loader)
        for batch_number, tasks_data  in enumerate(iterator):
            self.callbacks.on_batch_begin(batch_number)

            self._make_step(tasks_data, epoch, batch_number, steps_per_epoch, training)
            avg_metrics = {k: f"{v.avg:.4f}" for k, v in self.avg_meters.items()}
            iterator.set_postfix({"lr": float(self.lr_scheduler.get_last_lr()[-1]),
                                  "epoch": epoch,
                                  "mode": mode,
                                  **avg_metrics
                                  })
            if training:
                self.lr_scheduler.step()


            self.callbacks.on_batch_end(batch_number)
        return {k: v for k, v in self.avg_meters.items()}



    def _make_step(self, data: Dict[str, torch.Tensor], epoch, batch_number,
                   steps_per_epoch, training: bool):

        if training:
            self.optimizer.zero_grad()

        model_input_fields = self.model_input_fields
        input = [data[key] for key in model_input_fields]
        input = [i.to(self.device) for i in input]

        model_output = self.model(input)

        loss = self.criterion.calculate(model_output, data, self.avg_meters, training)

        if math.isnan(loss.item()) or math.isinf(loss.item()):
            raise ValueError("NaN loss !!")
        if training:
            loss.backward()

        if training:
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.)
            self.optimizer.step()

    def fit(self,
            loaders: Dict[str, Union[Dict[str, DataLoader], DataLoader]]):
        self.callbacks.on_train_begin()
        for epoch in range(self.start_epoch, self.nb_epoch):
            self.callbacks.on_epoch_begin(epoch)


            self.model.train()
            self.metrics_collection.train_metrics = self._run_one_epoch(epoch, loaders, training=True)
            self.checkpoint_handler.save_last(model=self.model, current_epoch=epoch,
                                              current_metrics=self.metrics_collection.train_metrics)
            self.lr_scheduler.step(epoch)

            if (epoch + 1) % self.test_every == 0:
                self.model.eval()
                with torch.no_grad():
                    self.metrics_collection.val_metrics = self._run_one_epoch(epoch, loaders, training=False)

            self.callbacks.on_epoch_end(epoch)
        self.callbacks.on_train_end()