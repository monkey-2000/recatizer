from typing import List
import cv2
import faiss
from sklearn.preprocessing import normalize
import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

from inference.entities.base import Entity
from inference.entities.cat import Cat, ClosestCats
from inference.ir_models.ir_cats_cls import CatIrClassificator
from telegram_bot.configs.bot_base_configs import S3ClientConfig
from telegram_bot.s3_client import YandexS3Client
from train.model.cats_model import HappyWhaleModel
from train.configs.tf_efficientnet_b0_config import tf_efficientnet_b0_config
from train.utils.image_utils import read_image, resize_image_if_needed


class Predictor:
    def __init__(self, s3_config: S3ClientConfig, models_pth: str):
        config = tf_efficientnet_b0_config.model_config
        self.image_size = tf_efficientnet_b0_config.image_size
        self.model = CatIrClassificator(models_pth)
        self.s3_client = YandexS3Client(s3_config.aws_access_key_id, s3_config.aws_secret_access_key)

    def _images_to_tensor(self, img):
        """ As input is image, img always comes in channels_last format """
        shape = img.shape
        assert len(shape) == 3 or len(shape) == 4, "Expecting tensor with dims 3 or 4"

        # Update single image to batch of size 1
        if len(shape) == 3:
            img = np.expand_dims(img, axis=0)

        image = resize_image_if_needed(img, self.image_size[0], self.image_size[1], interpolation=cv2.INTER_LINEAR)
        img = np.expand_dims(image, axis=0)
        return img

    def predict(self, path: str):
        data = self.s3_client.load_image(path)
        data = self._images_to_tensor(data)
        pred = self.model.predict(data)
        pred_np = pred.detach().numpy()
        return pred_np

class CatsMatcher:
    def __init__(self):
        self.D, self.I = None, None
    def create_and_search_index(self, embedding_size: int, train_embeddings: np.ndarray, val_embeddings: np.ndarray, k: int):
        index = faiss.IndexFlatL2(embedding_size)
        index.add(train_embeddings)
        D, I = index.search(val_embeddings, k=k)  # noqa: E741
        return D, I

    def __get_by_idx(self, l: List, idxs: List[int]):
        return [l[idx] for idx in idxs if idx >= 0]
    def create_distances_df(self,
            for_check: List[Entity], stored_cats: List[Cat], D: np.ndarray, I: np.ndarray):
        closest_cats = []
        for i, entity in tqdm(enumerate(for_check)):
            closest = self.__get_by_idx(stored_cats, list(I[i]))
            distances = list(D[i])[:len(closest)]
            closest_cats.append(ClosestCats(entity, closest, distances))
        return closest_cats

    def _get_embeddings(self, entities: List[Entity]):
        all_embeddings = [c.embeddings for c in entities]
        all_embeddings = np.float32(np.vstack(all_embeddings))
        all_embeddings = normalize(all_embeddings, axis=1, norm="l2")
        return all_embeddings

    def filter_by_thr(self, closest: List[ClosestCats], thr: float):
        for cl in closest:
            filtered = [(c, d) for c, d in zip(cl.cats, cl.distances) if d < thr]
            cl.cats = [f for f, _ in filtered]
            cl.distances = [f for _, f in filtered]
            yield cl
    def find_n_closest(self, for_check: List[Entity], stored_cats: List[Cat], max_n: int = 5, thr: float = 1):
        emb_for_check = self._get_embeddings(for_check)
        stored_emb = self._get_embeddings(stored_cats)
        D, I = self.create_and_search_index(stored_emb[0].size, stored_emb, emb_for_check, k=max_n)
        closest = self.create_distances_df(for_check, stored_cats, D, I)
        res = list(self.filter_by_thr(closest, thr))
        return res
