import logging
import os
import json
from typing import List


class Callback(object):
    """
    Abstract base class used to build new callbacks.
    """
    def on_batch_begin(self, batch):
        pass

    def on_batch_end(self, batch):
        pass

    def on_epoch_begin(self, epoch):
        pass

    def on_epoch_end(self, epoch):
        pass

    def on_train_begin(self):
        pass

    def on_train_end(self):
        pass


class CallbacksCollection(Callback):
    def __init__(self, callbacks: List[Callback]):
        super().__init__()
        if isinstance(callbacks, CallbacksCollection):
            callbacks = callbacks.callbacks
        self.callbacks = callbacks
        if callbacks is None:
            self.callbacks = []

    def on_batch_begin(self, batch):
        for callback in self.callbacks:
            callback.on_batch_begin(batch)

    def on_batch_end(self, batch):
        for callback in self.callbacks:
            callback.on_batch_end(batch)

    def on_epoch_begin(self, epoch):
        for callback in self.callbacks:
            callback.on_epoch_begin(epoch)

    def on_epoch_end(self, epoch):
        for callback in self.callbacks:
            callback.on_epoch_end(epoch)

    def on_train_begin(self):
        for callback in self.callbacks:
            callback.on_train_begin()

    def on_train_end(self):
        for callback in self.callbacks:
            callback.on_train_end()


class EarlyStopper(Callback):
    def __init__(self, patience, loss_terms, metrics_collection):
        Callback.__init__(self)
        self.patience = patience
        self.loss_terms =loss_terms
        self.metrics_collection = metrics_collection


    def get_loss(self):
        loss = 0.0
        for term, weight in self.loss_terms.items():
            loss += weight * self.metrics_collection.val_metrics.get(term, 0.)

        message = "Your loss is 0. All items in loss_term should match metrics to watch, loss_terms: {}, val_metrics: {}"
        if not loss:
            logging.info(message.format(self.loss_terms, self.metrics_collection.val_metrics))

        return loss
    def on_epoch_end(self, epoch):
        loss = self.get_loss()
        if loss < self.metrics_collection.best_loss:
            self.metrics_collection.best_loss = loss
            self.metrics_collection.best_epoch = epoch
        if epoch - self.metrics_collection.best_epoch >= self.patience:
            self.metrics_collection.stop_training = True