import logging
from collections import defaultdict
from typing import List
from time import time

from bson import ObjectId
from pymongo import MongoClient

from src.services.redis_service import CacheClient
from src.telegram_bot.bot_loader import DataUploader
from src.services.cats_service_base import CatsServiceBase
from src.configs.service_config import ServiceConfig, default_service_config
from src.entities.cat import Cat
from src.entities.person import Person
from src.services.matcher import CatsMatcher, Predictor
from src.services.mongo_service import CatsMongoClient, PeopleMongoClient, AnswersMongoClient


class CatsService(CatsServiceBase):

    def __init__(self, config: ServiceConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.answers_db = AnswersMongoClient(client.main)
        self.cache = CacheClient(config.redis_client_config)
        self.matcher = CatsMatcher(dim=config.embedding_size)
        self.predictor = Predictor(config.s3_client_config, config.models_path, config.local_models_path)
        self.bot_loader = DataUploader(config.bot_token, config.s3_client_config)

    def get_predictions(self, paths):
        embs = []
        for path in paths:
            emb = self.predictor.predict(path)
            embs.append(emb.tolist())
        return embs

    def save_new_cat(self, cat: Cat) -> bool:
        # emb = self.predictor.predict(cat.paths)
        cat.embeddings = self.get_predictions(cat.paths)

        if cat.quadkey not in self.matcher.quadkey_index:
            cats = self.cats_db.find({'quadkey': cat.quadkey})
            if cats:
                self.matcher.init_index(cat.quadkey, cats)

        self.matcher.add_items(cat.quadkey, [cat])

        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        #TODO start checking all people who searching their cats min(5 min, 5 new cats)
        self.__recheck_cats_in_search(cat.quadkey)
        return True

    def find_similar_cats(self, people: List[Person]):
        quadkeys = defaultdict(int)
        for person in people:
            quadkeys[person.quadkey] = min(quadkeys[person.quadkey], person.dt)

        # quadkeys = set({(person.quadkey, person.dt) for person in people})

        for quadkey, ans_time in quadkeys.items():
            query = {"is_active": True,
                     "quadkey": quadkey,
                     "dt": {"$gte": max(ans_time, 0)}}

            cats = self.cats_db.find(query)
            if not cats:
                return

            self.matcher.init_index(quadkey, cats)
            closest_cats = self.matcher.find_top_closest(quadkey, people)


            ## TODO Add cache
            for cl in closest_cats:
                cl.cats = self.answers_db.drop_sended_cats(cl.person._id, cl.cats)# we can filter it. But it this case
                if cl.cats:
                    cl.person.dt = time()
                    self.people_db.update(cl.person)
                    _ = self.answers_db.add_matches(cl)
                    self.cache.set(cl.person.chat_id, cl.cats)
                    self.bot_loader.upload(
                        chat_id=cl.person.chat_id,
                        cats=cl.cats
                    )

    def __recheck_cats_in_search(self, quadkey: str):
        people = self.people_db.find({'quadkey': quadkey})
        self.find_similar_cats(people)

    def delete_user(self, chat_id: str):
        self.people_db.delete({'chat_id': id})

    def add_user(self, person: Person):
        # emb = self.predictor.predict(person.path)
        # person.embeddings = emb.tolist()

        person.embeddings = self.get_predictions(person.paths)
        person = self.people_db.save(person)
        self.find_similar_cats([person])

    def mark_user_answer(self, message):
        wanted_cat= self.people_db.find({"chat_id": message["chat_id"],
                                             "is_active": True})
        if wanted_cat:
            wanted_cat = wanted_cat[0]
            answer = self.answers_db.find({"wanted_cat_id": wanted_cat._id,
                                           "match_cat_id": ObjectId(message["match_cat_id"])})
            answer = answer[0]
            answer.user_answer = message["user_answer"]
            self.answers_db.update(answer)


if __name__ == '__main__':
    cs = CatsService(default_service_config)
    # people = cs.people_db.find({})
    # cs.find_similar_cats(people)

    cat = Cat( _id=None,
            paths=['/home/art/PycharmProjects/recatizer_23/src/telegram_bot/tmp_local_storage/3d99afc6-ee26-458c-906d-bb540b5a4e79.jpg'],
            quadkey='no_quad',
            embeddings=None,
            is_active=True,
            additional_info="This is test cat",
            chat_id='450390623',
            person_name="Test name",
            dt=time())
    cs.save_new_cat(cat)


