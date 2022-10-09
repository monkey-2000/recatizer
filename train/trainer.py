import argparse
import os
import warnings
from typing import Dict, List, Tuple
from configs.utils import load
from dataset.loader import load_df
import numpy as np
import pandas as pd
import timm
import torch
import wandb

from train.task.cats_task import CatsTask


def parse():
    parser = argparse.ArgumentParser(description="Training for Finding cats")
    parser.add_argument("--out_base_dir", default="result")
    parser.add_argument("--in_base_dir", default="input")
    parser.add_argument("--save_checkpoint", action="store_true")
    parser.add_argument("--wandb_logger", action="store_true")
    parser.add_argument("--config_name", default="resnet18")
    return parser.parse_args()


def main():
    args = parse()
    warnings.filterwarnings("ignore", ".*does not have many workers.*")
    cfg = load(args.config_name)
    CatsTask(cfg).fit()

if __name__ == "__main__":
    main()