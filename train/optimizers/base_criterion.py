import torch
from abc import ABC, abstractmethod
from typing import Dict

from timm.utils import AverageMeter


class BaseLossAndMetricCriterion(ABC):
    def __init__(self):
        self.device = torch.device('cuda')  # Estimator is responsible of setting correct value to this thing

    @abstractmethod
    def calculate(self, output: Dict[str, torch.Tensor], target: Dict[str, torch.Tensor], avg_meter: Dict[str, AverageMeter],
                  training: bool) -> torch.Tensor:
        pass

    def on_epoch_start(self):
        """
        Before each epoch you can do some actions (mostly reset internal optimizers calculators)
        :return:
        """
        pass

    def to(self, device: torch.device):
        self.device = device

    @property
    def monitor_loss_terms(self):
        """
        names and coefficients of loss terms to get final loss in monitoring
        :return:
        """
        return {'loss': 1.}