import argparse
import warnings
from configs.utils import load
import wandb
from train.task.cats_task import CatsTask


def parse():
    parser = argparse.ArgumentParser(description="Training for Finding cats")
    parser.add_argument("--out_base_dir", default="result")
    parser.add_argument("--in_base_dir", default="input")
    parser.add_argument("--save_checkpoint", action="store_true")
    parser.add_argument("--wandb_logger", action="store_true")
    parser.add_argument("--config_name", default="tf_efficientnet_b0")
    return parser.parse_args()


def main():
    args = parse()
    warnings.filterwarnings("ignore", ".*does not have many workers.*")
    cfg = load(args.config_name)
    wandb.init(project='recatizer_proj', entity='recatizer')
    wandb.config = {
        "learning_rate": 0.001,
        "epochs": 100,
        "batch_size": 128
    }
    if not cfg:
        raise RuntimeError(f"not found config_name: {args.config_name}")
    CatsTask(cfg).fit()

if __name__ == "__main__":
    main()