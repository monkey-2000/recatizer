import logging
from time import time
from typing import List


from pymongo import MongoClient

from src.services.cash_service import CatsCash
from src.telegram_bot.bot_loader import DataUploader
from src.services.cats_service_base import CatsServiceBase
from src.configs.service_config import ServiceConfig, default_service_config
from src.entities.cat import Cat
from src.entities.person import Person
from src.services.matcher import CatsMatcher, Predictor
from src.services.mongo_service import CatsMongoClient, PeopleMongoClient


class CatsService(CatsServiceBase):


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
       # self.ansver_time_dely = config.answer_time_dely
      #  self.cash = CatsCash(config.answer_time_dely)

    def save_new_cat(self, cat: Cat) -> bool:
        cat.embeddings = self.get_embs(cat.paths)
        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        # TODO start checking all people who searching their cats min(5 min, 5 new cats)
        self.__recheck_cats_in_search(cat.quadkey)
        return True


    def __get_query(self, people):
        qudkeys = list({person.quadkey for person in people})
        query = {"quadkey": {"$in": qudkeys}}
        if 'no_quad' in qudkeys:
            query = {}
        last_aswer_time = list({person.dt for person in people})
        query['dt'] = {'$gte':  min(last_aswer_time)}
        return query



    def __find_similar_cats(self, people: List[Person]):
        # TODO fix case with none
        query = self.__get_query(people)
        cats = self.cats_db.find(query)

        if not cats:
            return
        closest_cats = self.matcher.find_n_closest(people, cats)

        for cl in closest_cats:
          #  cl = self.cash.answer_editor(cl)
            if len(cl.cats) > 0:
                cl.person.dt = time()
                self.people_db.update(cl.person)
                self.bot_loader.upload(cl)


    def __recheck_cats_in_search(self, quadkey: str):
        people = self.people_db.find({"quadkey": quadkey})
        if len(people) == 0:
            return
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

    def add_user(self, person: Person):
        #TODO load ans from cache
        # answer = self.cash.check_answer(person)
        # if answer:
        #     person.embeddings = answer.embeddings
        # else:
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
