import logging
from typing import List
import time

from pymongo import MongoClient

from src.telegram_bot.bot_loader import DataUploader
from src.services.cats_service_base import CatsServiceBase
from src.configs.service_config import ServiceConfig, default_service_config
from src.entities.cat import Cat
from src.entities.person import Person
from src.services.matcher import CatsMatcher, Predictor
from src.services.mongo_service import CatsMongoClient, PeopleMongoClient


class CatsService(CatsServiceBase):

    cash = {}
    def __init__(self, config: ServiceConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.matcher = CatsMatcher()
        self.predictor = Predictor(
            config.s3_client_config, config.models_path, config.local_models_path
        )
        self.bot_loader = DataUploader(
            config.bot_token, config.s3_client_config
        )
        self.ansver_time_dely = config.answer_time_dely

    def save_new_cat(self, cat: Cat) -> bool:
        cat.embeddings = self.get_embs(cat.paths)
        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        # TODO start checking all people who searching their cats min(5 min, 5 new cats)
        self.__recheck_cats_in_search(cat.quadkey)
        return True

    def __find_similar_cats(self, people: List[Person]):
        qudkeys = list({person.quadkey for person in people})

        query = {"quadkey": {"$in": qudkeys}}
        if None in qudkeys:
            query = {}

        cats = self.cats_db.find(query)

        if not cats:
            return
        closest_cats = self.matcher.find_n_closest(people, cats)
        # TODO write metod which delete cats that have already been sent

        for cl in closest_cats:

            self.bot_loader.upload(cl)
            # TODO add cash for answers
            # what_time_now = time.time()
            # if (cl.person.last_ans - what_time_now) > self.ansver_time_dely:
            #     self.bot_loader.upload(cl)
            #     # self.__ans_to_cash(closest_cats, not_send=False)
            # else:
            #     self.__ans_to_cash(closest_cats, not_send=True)

    def __recheck_cats_in_search(self, quadkey: str):
        people = self.people_db.find({"quadkey": quadkey})
        self.__find_similar_cats(people)

    def delete_user(self, chat_id: str):
        self.people_db.delete({"chat_id": id})

    def get_embs(self, paths):
        embs = []
        for path in paths:
            # if self.emb_in_cach(path):
            #     emb = self
            emb = self.predictor.predict(path)
            embs.append(emb.tolist())
        return embs


    # TODO
    def emb_in_cach(self, img_hash_name):
        return False

    # TODO check answers in cash
    def check_answer(self, person):
        return False

    # TODO save answers in cash
    def __ans_to_cash(self, people_closest_cats, not_send=False):
        pass

    def add_user(self, person: Person):
        answer = self.check_answer(person)
        if answer:
            person.embeddings = answer.embeddings
        else:
            person.embeddings = self.get_embs(person.paths)

        person = self.people_db.save(person)
        self.__find_similar_cats([person])


if __name__ == "__main__":
    service = CatsService(default_service_config)
    service.save_new_cat(
        Cat(
            path="recatizer-bucket/users_data/004a9fe6-2820-4273-8a3e-59f67898cee5_0.jpg",
            additional_info={},
            quadkey="",
            id=None,
            embeddings=None,
        )
    )
