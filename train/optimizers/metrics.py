from abc import ABC, abstractmethod
from typing import Iterable
from collections import defaultdict
import numpy as np


class BaseMetric(ABC):
    @abstractmethod
    def update(self, target: Iterable[int], predicted: Iterable[int]):
        raise NotImplementedError

    @abstractmethod
    def compute(self):
        raise NotImplementedError


class PRMetric(BaseMetric):
    EPS = 1e-5
    EMPTY_VAL = -1

    def __init__(self, num_classes):
        super().__init__()
        self._name = "prec", "rec"
        self.num_classes = num_classes
        self.reset()

    def reset(self):
        self.fn_classes = defaultdict(int)
        self.fp_classes = defaultdict(int)
        self.tp_classes = defaultdict(int)

    def update(self, target: Iterable[int], predicted: Iterable[int]):
        for target_class, predicted_class in zip(target, predicted):
            if target_class == predicted_class:
                self.tp_classes[target_class] += 1
            else:
                self.fp_classes[predicted_class] += 1
                self.fn_classes[target_class] += 1

    def compute(self):
        precision = np.full(
            shape=self.num_classes, fill_value=self.EMPTY_VAL, dtype=np.float32
        )
        recall = np.full(
            shape=self.num_classes, fill_value=self.EMPTY_VAL, dtype=np.float32
        )
        for i in range(self.num_classes):
            precision[i] = self.tp_classes[i] / (
                self.tp_classes[i] + self.fp_classes[i] + self.EPS
            )
            recall[i] = self.tp_classes[i] / (
                self.tp_classes[i] + self.fn_classes[i] + self.EPS
            )
            if (
                self.tp_classes[i] == 0
                and self.fn_classes[i] == 0
                and self.fp_classes[i] == 0
            ):
                precision[i] = self.EMPTY_VAL
                recall[i] = self.EMPTY_VAL

        precision_mask = precision == self.EMPTY_VAL
        recall_mask = recall == self.EMPTY_VAL
        precision_array = np.ma.array(precision, mask=precision_mask).compressed()
        recall_array = np.ma.array(recall, mask=recall_mask).compressed()

        return {
            self._name[0]: np.nan_to_num(precision_array.mean()),
            self._name[1]: np.nan_to_num(recall_array.mean()),
        }


class AccuracyMetric(BaseMetric):
    def __init__(self):
        self._name = "accuracy"
        self.reset()

    def reset(self):
        self.correct = 0
        self.total = 0

    def update(self, target: Iterable[int], predicted: Iterable[int]):
        self.correct += sum([t == p for t, p in zip(target, predicted)])
        self.total += len(target)

    def compute(self):
        return {self._name: float(self.correct) / self.total}
