from collections import defaultdict
from typing import List, Optional
import cv2
from bson import ObjectId
from sklearn.preprocessing import normalize
import numpy as np
from tqdm import tqdm
import hnswlib

from src.configs.service_config import default_service_config
from src.entities.answer import Answer
from src.entities.base import Entity
from src.entities.cat import Cat, ClosestCats
from src.ir_models.ir_cats_cls import CatIrClassificator
from src.telegram_bot.configs.bot_base_configs import S3ClientConfig
from src.utils.local_storage import LocalStorage
from src.utils.s3_client import YandexS3Client

from train.configs.tf_efficientnet_b0_config import tf_efficientnet_b0_config
from train.utils.image_utils import  resize_image_if_needed


class Predictor:
    def __init__(self, s3_config: S3ClientConfig, models_path: str, local_model_path: str):
        self.image_size = tf_efficientnet_b0_config.image_size
        if s3_config.local_path:
            self.s3_client = LocalStorage(s3_config.local_path)
        else:
            self.s3_client = YandexS3Client(s3_config.aws_access_key_id, s3_config.aws_secret_access_key)
        self.s3_client.download_file(models_path, local_model_path)
        self.model = CatIrClassificator(local_model_path)

    def _images_to_tensor(self, img):
        """ As input is image, img always comes in channels_last format """
        shape = img.shape
        assert len(shape) == 3 or len(shape) == 4, "Expecting tensor with dims 3 or 4"
        image = resize_image_if_needed(img, self.image_size[0], self.image_size[1], interpolation=cv2.INTER_LINEAR)

        # Update single image to batch of size 1
        if len(shape) == 3:
            image = np.expand_dims(image, axis=0)
        image = np.moveaxis(image, -1, 1).astype(np.float32)
        image = np.expand_dims(image, axis=0)
        return image

    def predict(self, path: str):
        data = self.s3_client.load_image(path)
        data = self._images_to_tensor(data)
        pred = self.model.predict(data)
        return pred[0]

class CatsMatcher:
    def __init__(self, dim: int, max_elements: int = 10000):
        self.max_elements = max_elements
        self.dim = dim
        self.quadkey_index = dict()
        self.mapping = defaultdict(dict)

    def init_index(self, quadkey: Optional[str], stored_cats: List[Cat]):
        embeddings, emb_owners = self._get_embeddings(stored_cats)
        if quadkey not in self.quadkey_index:
            self.quadkey_index[quadkey] = hnswlib.Index(space='l2', dim=self.dim)
            self.quadkey_index[quadkey].init_index(max_elements=self.max_elements, ef_construction=200, M=16)
            ids = np.arange(embeddings.shape[0])
            self.quadkey_index[quadkey].add_items(embeddings, ids)
            self.mapping[quadkey] = {id: cat for cat, id in zip(emb_owners, list(ids))} # TODO it doesn t work case
            self.quadkey_index[quadkey].set_ef(50)

    def add_items(self, quadkey: Optional[str], items: List[Cat]):
        embeddings, emb_owners = self._get_embeddings(items)
        if quadkey not in self.quadkey_index:
            self.init_index(quadkey, items)
        max_id = max(self.mapping[quadkey].keys())
        # TODO
        ids = np.arange(max_id+1, embeddings.shape[0] + max_id+1)
        self.quadkey_index[quadkey].add_items(embeddings, ids)
        self.mapping[quadkey] = {**self.mapping[quadkey], **{id: cat for cat, id in zip(emb_owners, list(ids))}}

    # def __get_by_idx(self, quadkey:str, idxs: List[int]):
    #     ids = [idx for idx in idxs if idx >= 0]
    #     return [self.mapping[quadkey][id] for id in ids]
    # def create_distances_df(self, quadkey: str, for_check: List[Entity], labels: np.ndarray, distances: np.ndarray):
    #     closest_cats = []
    #     for i, entity in tqdm(enumerate(for_check)):
    #         closest = self.__get_by_idx(quadkey, list(labels[i]))
    #         i_distances = list(distances[i])[:len(closest)]
    #         closest_cats.append(ClosestCats(entity, closest, i_distances))
    #     return closest_cats

    def _get_embeddings(self, entities: List[Entity]):
        all_embeddings = []
        owners = []
        for owner in entities:
            all_embeddings.append(owner.embeddings)
            owners.extend([owner] * len(owner.embeddings))

        # all_embeddings = [c.embeddings for c in entities]
        all_embeddings = np.float32(np.vstack(all_embeddings))
        all_embeddings = normalize(all_embeddings, axis=1, norm="l2")
        return all_embeddings, owners

    def filter_by_thr(self, closest: List[ClosestCats], thr: float):
        for cl in closest:
            filtered = [(c, d) for c, d in zip(cl.cats, cl.distances) if d < thr]
            cl.cats = [f for f, _ in filtered]
            cl.distances = [f for _, f in filtered]
            yield cl

    # TODO fix case with two embeddings
    def find_top_closest(self,
                         quadkey: Optional[str],
                         for_check: List[Entity],
                         answers: dict[Answer],
                         max_n: int = 5,
                         thr: float = 100):
        embs_for_check, emb_owners = self._get_embeddings(for_check)
        index = self.quadkey_index[quadkey]
        # max_possible_k = min(index.element_count, max_n)
        labels, distances = index.knn_query(embs_for_check, k=index.element_count)
        # labels, distances = index.knn_query(embs_for_check, k=index.element_count)
    ## TODO add owner for every owner drop send, and get best
        closest = self.create_closest_cats(quadkey,
                                          emb_owners,
                                          labels,
                                          distances,
                                          answers)
        # closest = self.create_distances_df(quadkey, for_check, labels, distances)
        res = list(self.filter_by_thr(closest, thr))
        return res

    def __get_by_idx(self, quadkey:str, idxs: List[int]):
        ids = [idx for idx in idxs if idx >= 0]
        return [self.mapping[quadkey][id] for id in ids]

    # def __get_reduced_cats(self, closest: List[Cat], i_distances: List[float]):
    #     cats_freq = defaultdict(int)
    #     cats_min_dist = defaultdict(int)
    #     for
    def __drop_sended(self,
                      matches: List[Cat],
                      dists: List[float],
                      answers: dict):
        filtered_matches = {}
        correct_cats = []
        not_marked_cats = []
        for cat, dist in zip(matches, dists):
            answer = answers[cat._id] if cat._id in answers else None
            if answer == None:
                if not cat._id in filtered_matches:
                    filtered_matches[cat._id] = {"cat": cat, "min_dist": dist}
                else:
                    filtered_matches[cat._id]["min_dist"] = min(filtered_matches[cat._id]["min_dist"], dist)
            else:
                if answer == 1:
                    correct_cats.append(cat)
                if answer == -1:
                    not_marked_cats.append(cat)
        return filtered_matches, correct_cats, not_marked_cats

    def create_closest_cats(self,
                            quadkey: str,
                            for_check: List[Entity],
                            labels: np.ndarray,
                            distances: np.ndarray,
                            answers: dict[Answer]):

        entities_closest_cats = defaultdict(list)
        i_distances = defaultdict(list)
        #check each embs
        for i, entity in tqdm(enumerate(for_check)):
            closest = self.__get_by_idx(quadkey, list(labels[i]))
            old_matches = answers[entity._id] if entity._id in answers else None
            new_matches, correct_cats, not_marked_cats = self.__drop_sended(matches=closest,
                                                                            dists=distances[i],
                                                                            answers= old_matches)
            #TODO What should we do with correct_cats and not_marked_cats?
            if new_matches:

                for cat_id in new_matches:
                    cat = new_matches[cat_id]["cat"]
                    dist = new_matches[cat_id]["min_dist"]
                    entities_closest_cats[entity._id].append(cat)
                    i_distances[entity._id].append(dist)

                #     _cats.append(new_matches[cat_id]["cat"])
                #     _dists.append(new_matches[cat_id]["min_dist"])
                #     print(type(_cats))
                # entities_closest_cats[entity._id].extend(_cats)
                # i_distances[entity._id].extend(_dists)

        closest_cats = []
        for entity in for_check:
            # i_distances = list(distances[i])[:len(closest)]
            closest_cats.append(ClosestCats(entity, entities_closest_cats[entity._id], i_distances[entity._id]))
        return closest_cats



