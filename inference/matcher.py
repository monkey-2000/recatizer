import glob
from typing import List

import cv2
import faiss

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
    def create_and_search_index(self, embedding_size: int, train_embeddings: np.ndarray, val_embeddings: np.ndarray, k: int):
        index = faiss.IndexFlatIP(embedding_size)
        index.add(train_embeddings)
        D, I = index.search(val_embeddings, k=k)  # noqa: E741

        return D, I

    def __get_by_idx(self, l: List, idxs: List[int]):
        return [l[idx] for idx in idxs if idx >= 0]
    def create_distances_df(self,
            check_cats: List[Cat], stored_cats: List[Cat], D: np.ndarray, I: np.ndarray):
        distances_df = []
        for i, cat in tqdm(enumerate(check_cats)):
            target = self.__get_by_idx(stored_cats, list(I[i]))
            distances = list(D[i])[:len(target)]
            subset_preds = pd.DataFrame(np.stack([target, distances], axis=1), columns=["target", "distances"])

        return []

    def _get_embeddings(self, cats: List[Cat]):
        all_embeddings = [c.embeddings for c in cats]
        all_embeddings = np.vstack(all_embeddings)
        all_embeddings = normalize(all_embeddings, axis=1, norm="l2")
        return all_embeddings

    def find_n_closest(self, check_cats: List[Cat], stored_cats: List[Cat], max_n: int = 2):
        emb_for_check = self._get_embeddings(check_cats)
        stored_emb = self._get_embeddings(stored_cats)
        D, I = self.create_and_search_index(stored_emb[0].size, stored_emb, emb_for_check, k=max_n)
        self.create_distances_df(check_cats, stored_cats, D, I)
        return stored_cats


if __name__ == '__main__':
    from train.configs.tf_efficientnet_b0_config import tf_efficientnet_b0_config
    from sklearn.preprocessing import normalize

    config = tf_efficientnet_b0_config.model_config
    df = pd.read_csv(tf_efficientnet_b0_config.dataset_config.train_path)
    id_class_nums = df.cat_id.value_counts().sort_index().values
    image_size = tf_efficientnet_b0_config.image_size

    model = HappyWhaleModel(config, torch.device('cpu'), id_class_nums=id_class_nums)
   # model.load_state_dict(torch.load(""))
    model.eval()

    transform = transforms.Compose([
            transforms.Resize([128, 128]),
            transforms.ToTensor()
        ])


    data = torchvision.datasets.ImageFolder(root="/Users/alinatamkevich/dev/recatizer/app/", transform=transform)

    data_loader = torch.utils.data.DataLoader(dataset=data, batch_size=1, shuffle=True, num_workers=0)
    all_embeddings = []
    cats = []
    for data, l in iter(data_loader):
        pred = model(data, None)
        emb = pred['embedding'].detach().numpy()
        cats.append(Cat(_id= None, path="", quadkey="", embeddings=emb, additional_info=dict()))

    matcher = CatsMatcher()
    res = matcher.find_n_closest(cats[:2], cats)

    # for file in files:
    #     img = cv2.imread(file, 0)
    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     img = cv2.resize(img, dsize=image_size)

