from typing import Dict
import torch
import torch.nn as nn

from train.optimizers.base_criterion import BaseLossAndMetricCriterion


class ClsLossAndMetricCriterion(BaseLossAndMetricCriterion):
    def __init__(self, device: torch.device, meters=None):
        super().__init__()
        self.loss = nn.CrossEntropyLoss()
        self.device = device
        self.meters = meters or []
        self.mean = True

    def calculate(
        self, output: Dict[str, torch.Tensor], target: Dict[str, torch.Tensor], training: bool
    ) -> torch.Tensor:
        print(output["logits_margin"].get_device(), target["label"].get_device())
        loss = self.loss(output["logits_margin"], target["label"])
        if self.mean:
            return torch.mean(loss)
        else:
            return loss


    def on_epoch_start(self):
        for meter in self.meters:
            meter.reset()
