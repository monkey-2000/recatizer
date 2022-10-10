from typing import Callable
from typing import Dict
from typing import Optional
import os
import pandas as pd
import torch
from torch.utils.data import Dataset
from typing import Any
from train.utils import image_utils


class CatsDataset(Dataset):
    def __init__(self, dir_path: str, path_to_csv: str, transforms: Optional[Callable] = None):
        self.df = self.__load_df__(dir_path, path_to_csv)
        self.transforms = transforms

        self.image_names = self.df["img"].values
        self.image_paths = self.df["path"].values
        self.targets = self.df["cat_id"].values

    def __load_df__(self, dir_path: str, path: str) -> pd.DataFrame:
        df = pd.read_csv(path)
        df["path"] = df["path"].apply(lambda img_path: os.path.join(dir_path, img_path))
        df = df[df.format == 'jpg']
        return df

    @classmethod
    def _read_image(cls, path: str) -> Dict[str, Any]:
        """Read single image from disk as a numpy array and add useful information as the image name, path and shape."""
        image = image_utils.read_image(path)
        return {"image": image, "name": os.path.basename(path), "path": path}


    def _apply_transforms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply custom transformations for a single sample"""
        return data if self.transforms is None else self.transforms(**data)


    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        image_path = self.image_paths[index]
        data = self._read_image(image_path)
        data.update(label=self.targets[index])
        data = self._apply_transforms(data)
        return data

    def __len__(self) -> int:
        return self.df.shape[0]
