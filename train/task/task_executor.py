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
from torch.optim.lr_scheduler import _LRScheduler
from train.configs.base_config import OptimizerParams, LearningSchedule


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
                 optimizer_config: OptimizerParams,
                 save_folder: str,
                 device: torch.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')):

        self.device = device
        self.model = model
        self.model.to(self.device)

        self.optimizer = self._create_optimizer(optimizer_config)

        self.save_folder = save_folder
        self.weights_save_path = os.path.join('results', 'weights', self.save_folder)
        self.logs_save_path = os.path.join('results', 'logs', self.save_folder)
        self.lr_scheduler = self._create_scheduler(optimizer_config.schedule)

        self.lr = optimizer_config.lr
        self.separate_step = True

        self.nb_epoch = optimizer_config.epochs
        self.warmup_epoch = 0
        self.start_epoch = 0
        self.compression_scheduler = None


        self.step_mode_schedule = False
        self.metrics_collection = MetricsCollection()
        self.model_input_fields = ['image']  # todo

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



    def _run_one_epoch(self, epoch: int, loaders: Dict[str, Union[Dict[str, DataLoader], DataLoader]],
                       training: bool = True):

        mode = 'train' if training else 'val'

        mode_loaders = loaders[mode]
        steps_per_epoch = len(mode_loaders)
        self._run_one_epoch_for_all_loaders(mode_loaders, steps_per_epoch, epoch, mode, training)

        return {k: v for k, v in self.avg_meter.as_dict().items()}

    def _run_one_epoch_for_all_loaders(self,
                                       loader: Union[DataLoader, Iterable[Tuple[Dict[str, torch.Tensor]]]],
                                       steps_per_epoch: int,
                                       epoch: int,
                                       mode: str,
                                       training: bool):

        pbar = tqdm(enumerate(loader), total=steps_per_epoch, desc="Epoch {}{}".format(epoch, mode), ncols=0)
        for batch_number, tasks_data in pbar:
            self._make_step(tasks_data, epoch, batch_number, steps_per_epoch, training)


    def _make_step(self, tasks_data: Dict[str, torch.Tensor], epoch, batch_number,
                   steps_per_epoch, training: bool):
        """
        Make step on single batch inside of this method. In case of multitasking - just batch after batch.
        :param tasks_data: name of task and dict with batch
        """
        if training:
            self.optimizer.zero_grad()

        for task, data in tasks_data:
            model_input_fields = self.model_input_fields
            input = [data[key] for key in model_input_fields]
            input = [i.to(self.device) for i in input]

            if len(input) != 1:
                warnings.warn("make sure your model has list of inputs")
            model_output = self.model(*input)
            assert isinstance(model_output,
                              dict), "Model output must be dict because model exporting/serving relies on it"
            loss = self.loss_and_metric_calculator.calculate(model_output, data, self.avg_meter, training, task=task)
            if loss is None:
                raise Exception(
                    'Your loss is None! Please check if you return it out of your loss and metric calculator')

            if self.compression_scheduler:
                loss = self.compression_scheduler.before_backward_pass(epoch, batch_number, steps_per_epoch,
                                                                       loss, optimizer=self.optimizer)
            if training:
                loss.backward()

            if self.compression_scheduler:
                self.compression_scheduler.before_parameter_optimization(epoch, batch_number,
                                                                         steps_per_epoch, self.optimizer)

            if training and len(tasks_data) > 1 and self.separate_step:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.)
                self.optimizer.step()
                self.optimizer.zero_grad()

        if training:
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.)
            self.optimizer.step()

    def fit(self,
            loaders: Dict[str, Union[Dict[str, DataLoader], DataLoader]]):
        """
        :param loaders:
        if you have multitasking -
        {'train':
          {task_name: DataLoader,
           task_name2: DataLoader},
         'val':
          {task_name: DataLoader,
           task_name2: DataLoader}
        }
        if you don't have multitasking -
        {'train': DataLoader, 'val': DataLoader}
        :param resume_type: (continue, restart, full_restart) defines which weights to be used. Only checkpoint supports optimizer state/epochs.
        Otherwise training will start from zero epoch. Restart option will ignore any weights.
        """


        for epoch in range(self.start_epoch, self.nb_epoch):

            if self.compression_scheduler:
                self.compression_scheduler.on_epoch_begin(epoch)

            self.model.train()
            self.metrics_collection.train_metrics = self._run_one_epoch(epoch, loaders, training=True)

            if epoch >= self.warmup_epoch and not self.step_mode_schedule:
                self.lr_scheduler.step(epoch)

            self.model.eval()
            with torch.no_grad():
                self.metrics_collection.val_metrics = self._run_one_epoch(epoch, loaders, training=False)


            if self.metrics_collection.stop_training:
                break
