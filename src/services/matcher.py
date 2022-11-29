from itertools import groupby
from typing import List
import cv2
import faiss
from sklearn.preprocessing import normalize
import numpy as np
from tqdm import tqdm

from src.entities.base import Entity
from src.entities.cat import Cat, ClosestCats
from src.ir_models.ir_cats_cls import CatIrClassificator
from src.telegram_bot.configs.bot_base_configs import S3ClientConfig
from src.utils.s3_client import YandexS3Client

from train.configs.tf_efficientnet_b0_config import tf_efficientnet_b0_config
from train.utils.image_utils import resize_image_if_needed


class Predictor:
    def __init__(
        self, s3_config: S3ClientConfig, models_path: str, local_model_path: str
    ):
        self.image_size = tf_efficientnet_b0_config.image_size
        self.s3_client = YandexS3Client(
            s3_config.aws_access_key_id, s3_config.aws_secret_access_key
        )
        # TODO decomment this
        # self.s3_client.download_file(models_path, local_model_path)
        # self.model = CatIrClassificator(local_model_path)

    def _images_to_tensor(self, img):
        """As input is image, img always comes in channels_last format"""
        shape = img.shape
        assert len(shape) == 3 or len(shape) == 4, "Expecting tensor with dims 3 or 4"
        image = resize_image_if_needed(
            img, self.image_size[0], self.image_size[1], interpolation=cv2.INTER_LINEAR
        )

        # Update single image to batch of size 1
        if len(shape) == 3:
            image = np.expand_dims(image, axis=0)
        image = np.moveaxis(image, -1, 1).astype(np.float32)
        image = np.expand_dims(image, axis=0)
        return image

    # TODO deccomment
    def predict(self, path: str):
        # data = self.s3_client.load_image(path)
        # data = self._images_to_tensor(data)
        # pred = self.model.predict(data)
        # return pred[0]
        return np.array([0] * 512)


class CatsMatcher:
    def __init__(self):
        self.D, self.I = None, None

    def create_and_search_index(
        self,
        embedding_size: int,
        train_embeddings: np.ndarray,
        val_embeddings: np.ndarray,
        k: int,
    ):
        index = faiss.IndexFlatL2(embedding_size)
        index.add(train_embeddings)
        D, I = index.search(val_embeddings, k=k)  # noqa: E741
        return D, I

    def __get_by_idx(self, l: List, idxs: List[int]):
        return [l[idx] for idx in idxs if idx >= 0]

    def create_distances_df(
        self,
        for_check: List[Entity],
        stored_cats: List[Cat],
        D: np.ndarray,
        I: np.ndarray,
    ):
        closest_cats = []
        for i, entity in tqdm(enumerate(for_check)):
            closest = self.__get_by_idx(stored_cats, list(I[i]))
            distances = list(D[i])[: len(closest)]
            closest_cats.append(ClosestCats(entity, closest, distances))
        return closest_cats

    def _get_embeddings(self, entities: List[Entity]):
        all_embeddings = []
        embeddings_belonging = []

        for entity_id, entity in enumerate(entities):
            for embedding in entity.embeddings:
                all_embeddings.append(embedding)
                embeddings_belonging.append(entity)

        all_embeddings = np.float32(np.vstack(all_embeddings))
        all_embeddings = normalize(all_embeddings, axis=1, norm="l2")
        return all_embeddings, embeddings_belonging

    def filter_by_thr(self, closest: List[ClosestCats], thr: float):
        for cl in closest:
            filtered = [(c, d) for c, d in zip(cl.cats, cl.distances) if d < thr]
            cl.cats = [f for f, _ in filtered]
            cl.distances = [f for _, f in filtered]
            yield cl

    @staticmethod
    def reduce_closest_cats(closest_cats):
        """deletes duplicates"""
        reduced_closest_cats = {}
        for cat in closest_cats:
            if id(cat) not in reduced_closest_cats:
                reduced_closest_cats[id(cat)] = cat

        return reduced_closest_cats.values()



    def find_n_closest(
        self,
        for_check: List[Entity],
        stored_cats: List[Cat],
        max_n: int = 5,
        thr: float = 1,
    ):
        emb_for_check, _ = self._get_embeddings(for_check)
        stored_emb, stored_emb_belonging = self._get_embeddings(stored_cats)
        D, I = self.create_and_search_index(
            stored_emb[0].size, stored_emb, emb_for_check, k=max_n
        )
        persons_and_matched_cats = self.create_distances_df(
            for_check, stored_emb_belonging, D, I
        )
        for person_id, person in enumerate(persons_and_matched_cats):
            person.cats = self.reduce_closest_cats(person.cats)
            #person.cats = [g[0] for _, g in groupby(person.cats, lambda l: l[0])]
            persons_and_matched_cats[person_id] = person
        res = list(self.filter_by_thr(persons_and_matched_cats, thr))
        return res
