from typing import Callable
from typing import Dict
from typing import Optional

import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset


class CatsDataset(Dataset):
    def __init__(self, dir_path: str, path_to_csv: str, transform: Optional[Callable] = None):
        self.df = self.__load_df__(dir_path, path_to_csv)
        self.transform = transform

        self.image_names = self.df["image"].values
        self.image_paths = self.df["image_path"].values
        self.targets = self.df["id"].values

    def __load_df__(self, dir_path: str, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        df["path"] = dir_path + df["image"]
        return df

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        image_name = self.image_names[index]

        image_path = self.image_paths[index]

        image = Image.open(image_path)

        if self.transform:
            image = self.transform(image)

        target = self.targets[index]
        target = torch.tensor(target, dtype=torch.long)

        return {"image_name": image_name, "image": image, "target": target}

    def __len__(self) -> int:
        return self.df.shape[0]
