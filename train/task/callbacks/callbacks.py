import os
from typing import Optional
import time
import numpy as np
from tensorboardX import SummaryWriter
import json

from train.task.callbacks.base import Callback


class TensorBoard(Callback):
    def __init__(self, logdir, optimizer, metrics_collection):
        Callback.__init__(self)

        self.logdir = logdir
        os.makedirs(self.logdir, exist_ok=True)
        self.writer = SummaryWriter(self.logdir)
        self.optimizer = optimizer
        self.metrics_collection = metrics_collection

    def on_epoch_end(self, epoch):
        for k, v in self.metrics_collection.train_metrics.items():
            self.writer.add_scalar('train/{}'.format(k.replace('@', '_')), float(v.avg), global_step=epoch)

        for k, v in self.metrics_collection.val_metrics.items():
            self.writer.add_scalar('val/{}'.format(k.replace('@', '_')), float(v.avg), global_step=epoch)

        for idx, param_group in enumerate(self.optimizer.param_groups):
            lr = param_group['lr']
            self.writer.add_scalar('group{}/lr'.format(idx), float(lr), global_step=epoch)

    def on_train_end(self):
        self.writer.close()


class JsonMetricSaver(Callback):
    def __init__(self, logdir, optimizer, metrics_collection):
        Callback.__init__(self)
        self.logdir = logdir
        os.makedirs(self.logdir, exist_ok=True)
        self.optimizer = optimizer
        self.metrics_collection = metrics_collection
        self.train_metrics_path = os.path.join(logdir, 'train_metrics.json')
        self.val_metrics_path = os.path.join(logdir, 'val_metrics.json')
        self.other_metrics_path = os.path.join(logdir, 'other_metrics.json')
        self.metrics_paths = [self.train_metrics_path, self.val_metrics_path, self.other_metrics_path]

    def on_train_begin(self):
        for filepath in self.metrics_paths:
            with open(filepath, 'w') as f:
                json.dump([], f)

    def on_epoch_end(self, epoch):
        with open(self.train_metrics_path, 'r+') as f:
            data = {k: v.avg for k,v in self.metrics_collection.train_metrics.items()}
            self._write_data(f, epoch, data)

        with open(self.val_metrics_path, 'r+') as f:
            data = {k: v.avg for k,v in self.metrics_collection.val_metrics.items()}
            self._write_data(f, epoch, data)

        with open(self.other_metrics_path, 'r+') as f:
            data = {}
            for idx, param_group in enumerate(self.optimizer.param_groups):
                lr = param_group['lr']
                data['lr{}'.format(idx)] = lr
            self._write_data(f, epoch, data)

    def _write_data(self, fp, epoch, data):
        new_data = {'epoch': epoch}
        new_data.update(data)
        old_data = fp.read()
        old_data = json.loads(old_data)
        old_data.append(new_data)
        fp.seek(0)
        fp.write(json.dumps(old_data, indent=4))
        fp.truncate()
