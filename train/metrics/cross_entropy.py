from typing import Dict
import torch
import torch.nn as nn

from train.metrics.base_criterion import BaseLossAndMetricCriterion


class ClsLossAndMetricCriterion(BaseLossAndMetricCriterion):
    def __init__(self, device: torch.device, meters=None):
        super().__init__()
        self.loss = nn.CrossEntropyLoss()
        self.device = device
        self.meters = meters or []

    def calculate(
        self, output: Dict[str, torch.Tensor], target: Dict[str, torch.Tensor], training: bool
    ) -> torch.Tensor:

        loss = self.loss(output["out"], target["label"])
        return loss

    def on_epoch_start(self):
        for meter in self.meters:
            meter.reset()
