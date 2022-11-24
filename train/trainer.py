import argparse
import warnings
from configs.utils import load
import wandb

from train.configs.base_config import Config
from train.task.cats_task import CatsTask


def parse():
    parser = argparse.ArgumentParser(description="Training for Finding cats")
    parser.add_argument("--out_base_dir", default="result")
    parser.add_argument("--in_base_dir", default="input")
    parser.add_argument("--save_checkpoint", action="store_true")
    parser.add_argument("--wandb_logger", action="store_true")
    parser.add_argument("--config_name", default="tf_efficientnet_b0")
    parser.add_argument("--action", default="train")
    return parser.parse_args()


def process(wandb_run, action: str, cfg: Config):
    task = CatsTask(wandb_run, cfg)

    if action == "train":
        task.fit()
    elif action == "vis_data":
        loader = task.get_train_loaders()
        data = []
        columns=["image", "label"]
        for i, batch in enumerate(loader, 0):
            inputs, labels = batch['image'], batch['label']
            for j, image in enumerate(inputs, 0):
                data.append([wandb.Image(image), labels[j].item()])
            break

        table = wandb.Table(data=data, columns=columns)
        wandb_run.log({"cats_images": table})

def main():
    args = parse()
    warnings.filterwarnings("ignore", ".*does not have many workers.*")
    cfg: Config = load(args.config_name)
    run = wandb.init(project='recatizer_proj2', entity='recatizer')

    if not cfg:
        raise RuntimeError(f"not found config_name: {args.config_name}")
    process(run, args.action, cfg)


if __name__ == "__main__":
    main()