import torch
import os
import re
from train.configs.base_config import ModelConfig


class CheckpointHandler:
    def __init__(self, model_config: ModelConfig):
        self.model_config = model_config

    def save_last(self, model, current_epoch, current_metrics):
        model = model.eval()
        torch.save(
            {
                "epoch": current_epoch,
                "state_dict": model.state_dict(),
                "optimizers": current_metrics,
            },
            os.path.join(
                self.model_config.path_to_save, self.model_config.model_name + "_last"
            ),
        )

    def load_checkpoint(self, model: torch.nn.Module):
        checkpoint_path = self.model_config.resume_checkpoint
        if not checkpoint_path:
            print("start model from scratch")
            return
        if os.path.isfile(checkpoint_path):
            print("=> loading checkpoint '{}'".format(checkpoint_path))
            checkpoint = torch.load(checkpoint_path, map_location="cpu")
            if "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
                state_dict = {
                    re.sub("^module.", "", k): w for k, w in state_dict.items()
                }
                orig_state_dict = model.state_dict()
                mismatched_keys = []
                for k, v in state_dict.items():
                    ori_size = (
                        orig_state_dict[k].size() if k in orig_state_dict else None
                    )
                    if v.size() != ori_size:
                        print(
                            "SKIPPING!!! Shape of {} changed from {} to {}".format(
                                k, v.size(), ori_size
                            )
                        )
                        mismatched_keys.append(k)
                for k in mismatched_keys:
                    del state_dict[k]
                model.load_state_dict(state_dict, strict=False)
                print(
                    "=> loaded checkpoint '{}' (epoch {})".format(
                        checkpoint_path, checkpoint["epoch"]
                    )
                )
            else:
                model.load_state_dict(checkpoint)
                return model, checkpoint
        else:
            print("=> no checkpoint found at '{}'".format(checkpoint_path))
        return model, None
