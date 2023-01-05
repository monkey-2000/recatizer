import logging
from time import time
from typing import List

import redis
from pymongo import MongoClient

from src.entities.answer import Answer
from src.services.redis_service import CacheClient
from src.telegram_bot.bot_loader import DataUploader
from src.services.cats_service_base import CatsServiceBase
from src.configs.service_config import ServiceConfig, default_service_config
from src.entities.cat import Cat, ClosestCats
from src.entities.person import Person
from src.services.matcher import CatsMatcher, Predictor
from src.services.mongo_service import (
    CatsMongoClient,
    PeopleMongoClient,
    AnswersMongoClient,
)


class CatsService(CatsServiceBase):
    def __init__(self, config: ServiceConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.answers_db = AnswersMongoClient(client.main)

        self.cache = CacheClient(config.redis_client_config)


        self.bot_loader = DataUploader(config.bot_token, config.s3_client_config)
        self.answer_time_delay = config.answer_time_delay
        self.cats_in_answer = config.cats_in_answer

    #  self.cash = CatsCash(config.answer_time_delay)
        self.matcher = CatsMatcher(dim=config.embedding_size)
        self.predictor = Predictor(config.s3_client_config, config.models_path, config.local_models_path)


    def get_embs(self, paths):
        embs = []
        for path in paths:
            emb = self.predictor.predict(path)
            embs.append(emb.tolist())
        return embs

    def save_new_cat(self, cat: Cat) -> bool:

        cat.embeddings = self.get_embs(cat.paths)

        if cat.quadkey not in self.matcher.quadkey_index:
            cats = self.cats_db.find({'quadkey': cat.quadkey})
            if cats:
                self.matcher.init_index(cat.quadkey, cats)

        self.matcher.add_items(cat.quadkey, [cat])
        # cat.embeddings = emb.tolist()
        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        #TODO start checking all people who searching their cats min(5 min, 5 new cats)
        self.recheck_cats_in_search(cat.quadkey)
        return True

    def find_similar_cats(self, people: List[Person]):
        quadkeys = set({person.quadkey for person in people})
        for quadkey in quadkeys:
            # TODO case with no quad
            # qudkeys = list({person.quadkey for person in people})
            # last_aswer_time = list({person.dt for person in people})
            # query = self.__get_query(qudkeys, last_aswer_time)  # TODO new method in Mongo Service
            query = {'quadkey': quadkey}
            cats = self.cats_db.find(query)

            if cats:
                self.matcher.init_index(quadkey, cats)
                closest_cats = self.matcher.find_top_closest(quadkey, people)
                for cl in closest_cats:
                    if cl.cats:
                        cl.person.dt = time()
                        self.people_db.update(cl.person)
                        # cl.cats = self.answers_db.drop_sended_cats(cl.person._id, cl.cats)
                        self.cache.set(cl.person.chat_id, cl.cats)
                        self.bot_loader.upload(cats=cl.cats,
                                               chat_id=cl.person.chat_id)



    # def __get_query(self, qudkeys: list, t_last_aswers=[-float("inf")]):
    #
    #     query = {"quadkey": {"$in": qudkeys.append("no_quad")}}
    #     if "no_quad" in qudkeys:
    #         query = {}
    #     query["dt"] = {"$gte": min(t_last_aswers)}
    #     query["is_active"] = True
    #     return query



    def recheck_cats_in_search(self, quadkey: str):
        quadkeys = [quadkey, "no_quad"]
        query =    {
                "quadkey": {"$in": quadkeys},
             #   "dt": {"$lte": time() - self.answer_time_delay},
                "is_active": True,
            }# TODO new method in Mongo Service
        people = self.people_db.find(query)
        if len(people) == 0:
            return
        self.find_similar_cats(people)

    def delete_user(self, chat_id: str):
        self.people_db.delete({"chat_id": id})



    def add_user(self, person: Person):
        emb = self.predictor.predict(person.path)
        person.embeddings = emb.tolist()
        person = self.people_db.save(person)

        self.find_similar_cats([person])


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
