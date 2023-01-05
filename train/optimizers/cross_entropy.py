from typing import Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn
from timm.utils import AverageMeter

from train.optimizers.base_criterion import BaseLossAndMetricCriterion
from train.optimizers.losses import FocalLoss
from train.optimizers.metrics import BaseMetric


class ClsLossAndMetricCriterion(BaseLossAndMetricCriterion):
    def __init__(
        self,
        device: torch.device,
        metrics: Optional[List[BaseMetric]] = None,
        loss="focal_loss",
    ):
        super().__init__()
        self.loss = (
            FocalLoss(gamma=2) if loss == "focal_loss" else torch.nn.CrossEntropyLoss()
        )
        self.device = device
        self.metrics = metrics or []

    def calculate(
        self,
        output: Dict[str, torch.Tensor],
        target: Dict[str, torch.Tensor],
        avg_meter: Dict[str, AverageMeter],
        training: bool,
    ) -> torch.Tensor:
        loss = self.loss(output["logits_margin"], target["label"].to(self.device))
        avg_meter["loss"].update(loss.item(), target["image"].size(0))
        self.__calc_metrics(output, target, avg_meter)
        return loss

    def __calc_metrics(
        self,
        output: Dict[str, torch.Tensor],
        target: Dict[str, torch.Tensor],
        avg_meter: Dict[str, AverageMeter],
    ):
        labels = target["label"].data.cpu().numpy().tolist()
        pred_logits = output["logits_margin"].data.cpu().numpy()
        pred_labels = np.argmax(pred_logits, axis=1).tolist()
        for idx, meter in enumerate(self.metrics):
            meter.update(labels, pred_labels)
            metric = meter.compute()
            for metric_name, value in metric.items():
                avg_meter[metric_name].update(value)

    def on_epoch_start(self):
        for meter in self.metrics:
            meter.reset()
