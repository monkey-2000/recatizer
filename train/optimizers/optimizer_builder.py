from torch.optim import lr_scheduler
from torch.optim.adamw import AdamW
from torch.optim.lr_scheduler import MultiStepLR, CyclicLR, CosineAnnealingLR
from torch.optim.rmsprop import RMSprop
from torch import optim
from train.configs.base_config import OptimizerParams


class OptimizerBuilder:
    def __init__(self, optimizer_config: OptimizerParams):
        self.optimizer_config = optimizer_config

    def build_optimizer(self, model):
        params = model.parameters()
        learning_rate = self.optimizer_config.lr
        weight_decay = self.optimizer_config.wd
        eps = self.optimizer_config.eps

        if self.optimizer_config.type == "SGD":
            optimizer = optim.SGD(params,
                                  lr=learning_rate,
                                  weight_decay=weight_decay)

        elif self.optimizer_config.type == "Adam":
            optimizer = optim.Adam(params,
                                   eps=eps,
                                   lr=learning_rate,
                                   weight_decay=weight_decay)
        elif self.optimizer_config.type == "AdamW":
            optimizer = AdamW(params,
                              eps=eps,
                              lr=learning_rate,
                              weight_decay=weight_decay)
        elif self.optimizer_config.type == "RmsProp":
            optimizer = RMSprop(params,
                                lr=learning_rate,
                                weight_decay=weight_decay)

        else:
            raise KeyError("unrecognized optimizer {}".format(self.optimizer_config.type))
        return optimizer


    def build_scheduler(self, optimizer):
        scheduler_config = self.optimizer_config.schedule
        scheduler = None
        if scheduler_config.type == "step":
            scheduler = lr_scheduler.StepLR(optimizer, **scheduler_config.params)
        elif scheduler_config.type == "clr":
            scheduler = CyclicLR(optimizer, **scheduler_config.params)
        elif scheduler_config.type == "multistep":
            scheduler = MultiStepLR(optimizer, **scheduler_config.params)
        elif scheduler_config.type == "exponential":
            scheduler = lr_scheduler.ExponentialLR(optimizer, **scheduler_config.params)
        elif scheduler_config.type == "constant":
            scheduler = lr_scheduler.LambdaLR(optimizer, lambda epoch: 1.0)
        elif scheduler_config.type == "linear":
            def linear_lr(it):
                return it * scheduler_config.params["alpha"] + scheduler_config.params[
                    "beta"]

            scheduler = lr_scheduler.LambdaLR(optimizer, linear_lr)
        return scheduler

    def build(self, model):
        optimizer = self.build_optimizer(model)
        scheduler = self.build_scheduler(optimizer)
        return optimizer, scheduler
