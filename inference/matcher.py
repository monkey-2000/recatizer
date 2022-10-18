import glob
from typing import List

import cv2
#import faiss as faiss
import numpy as np
import torchvision.transforms as transforms

from torch.utils.data.dataloader import DataLoader
import pandas as pd
import torch
import torchvision
from tqdm import tqdm

from inference.entities.cat import Cat
from train.model.cats_model import HappyWhaleModel


class CatsMatcher:
    # def create_and_search_index(self, embedding_size: int, train_embeddings: np.ndarray, val_embeddings: np.ndarray, k: int):
    #     index = faiss.IndexFlatIP(embedding_size)
    #     index.add(train_embeddings)
    #     D, I = index.search(val_embeddings, k=k)  # noqa: E741
    #
    #     return D, I
    #
    # def create_distances_df(self,
    #         image_names: np.ndarray, targets: np.ndarray, D: np.ndarray, I: np.ndarray, stage: str  # noqa: E741
    # ) -> pd.DataFrame:
    #     distances_df = []
    #     for i, image_name in tqdm(enumerate(image_names), desc=f"Creating {stage}_df"):
    #         target = targets[I[i]]
    #         distances = D[i]
    #         subset_preds = pd.DataFrame(np.stack([target, distances], axis=1), columns=["target", "distances"])
    #         subset_preds["image"] = image_name
    #         distances_df.append(subset_preds)
    #
    #     distances_df = pd.concat(distances_df).reset_index(drop=True)
    #     distances_df = distances_df.groupby(["image", "target"]).distances.max().reset_index()
    #     distances_df = distances_df.sort_values("distances", ascending=False).reset_index(drop=True)
    #
    #     return distances_df
    #
    # def get_best_threshold(self, val_targets_df: pd.DataFrame, valid_df: pd.DataFrame) -> Tuple[float, float]:
    #     best_th = 0
    #     best_cv = 0
    #     for th in [0.1 * x for x in range(11)]:
    #         all_preds = get_predictions(valid_df, threshold=th)
    #
    #         cv = 0
    #         for i, row in val_targets_df.iterrows():
    #             target = row.target
    #             preds = all_preds[row.image]
    #             val_targets_df.loc[i, th] = map_per_image(target, preds)
    #
    #         cv = val_targets_df[th].mean()
    #
    #         print(f"th={th} cv={cv}")
    #
    #         if cv > best_cv:
    #             best_th = th
    #             best_cv = cv
    #
    #     print(f"best_th={best_th}")
    #     print(f"best_cv={best_cv}")
    #
        # val_targets_df["is_new_individual"] = val_targets_df.target == "new_individual"
        # val_scores = val_targets_df.groupby("is_new_individual").mean().T
        # val_scores["adjusted_cv"] = val_scores[True] * 0.1 + val_scores[False] * 0.9
        # best_th = val_scores["adjusted_cv"].idxmax()
        # print(f"best_th_adjusted={best_th}")
        #
        # return best_th, best_cv


    def find_n_closest(self, cat: Cat, stored_cats: List[Cat], max_n: int = 5):
        return stored_cats


if __name__ == '__main__':
    from train.configs.tf_efficientnet_b0_config import tf_efficientnet_b0_config


    matcher = CatsMatcher()
    config = tf_efficientnet_b0_config.model_config
    df = pd.read_csv(tf_efficientnet_b0_config.dataset_config.train_path)
    id_class_nums = df.cat_id.value_counts().sort_index().values
    image_size = tf_efficientnet_b0_config.image_size

    model = HappyWhaleModel(config, torch.device('cpu'), id_class_nums=id_class_nums)
   # model.load_state_dict(torch.load(""))
    model.eval()
    files = glob.glob("/Users/alinatamkevich/dev/recatizer/app/images/*")

    transform = transforms.Compose([
            transforms.Resize([128, 128]),
            transforms.ToTensor()
        ])


    data = torchvision.datasets.ImageFolder(root="/Users/alinatamkevich/dev/recatizer/app/", transform=transform)

    data_loader = torch.utils.data.DataLoader(dataset=data, batch_size=1, shuffle=True, num_workers=0)
    for data, l in iter(data_loader):
        pred = model(data, None)

    # for file in files:
    #     img = cv2.imread(file, 0)
    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     img = cv2.resize(img, dsize=image_size)

