import os
import torch

from train.configs.base_config import ModelConfig


def _save_last(model, current_epoch, current_metrics, config: ModelConfig):
    model = model.eval()
    torch.save({
        'epoch': current_epoch,
        'state_dict': model.state_dict(),
        'metrics': current_metrics,

    }, os.path.join(config.path_to_save, config.model_name + "_last"))

