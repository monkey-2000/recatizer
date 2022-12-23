import logging
from time import time
from typing import List


from pymongo import MongoClient

from src.entities.answer import Answer
from src.telegram_bot.bot_loader import DataUploader
from src.services.cats_service_base import CatsServiceBase
from src.configs.service_config import ServiceConfig, default_service_config
from src.entities.cat import Cat, ClosestCats
from src.entities.person import Person
from src.services.matcher import CatsMatcher, Predictor
from src.services.mongo_service import CatsMongoClient, PeopleMongoClient, AnswersMongoClient


class CatsService(CatsServiceBase):


    def __init__(self, config: ServiceConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.answers_db = AnswersMongoClient(client.main)
        self.matcher = CatsMatcher()
        self.predictor = Predictor(
            config.s3_client_config, config.models_path, config.local_models_path
        )
        self.bot_loader = DataUploader(
            config.bot_token, config.s3_client_config
        )
        self.answer_time_delay = config.answer_time_delay
        self.cats_in_answer = config.cats_in_answer
      #  self.cash = CatsCash(config.answer_time_delay)

    def save_new_cat(self, cat: Cat) -> bool:
        cat.embeddings = self.get_embs(cat.paths)
        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        # TODO start checking all people who searching their cats min(5 min, 5 new cats)
        # it s completed but not apropriate
        self.recheck_cats_in_search(cat.quadkey)
        return True

    def __get_query(self, qudkeys: list, t_last_aswers=[-float('inf')]):

        query = {"quadkey": {"$in": qudkeys.append('no_quad')}}
        if 'no_quad' in qudkeys:
            query = {}
        query['dt'] = {'$gte': min(t_last_aswers)}
        query['is_active'] = True
        return query






    def __find_similar_cats(self, people: List[Person]):
        # TODO fix case with none
        qudkeys = list({person.quadkey for person in people})
        last_aswer_time = list({person.dt for person in people})
        query = self.__get_query(qudkeys, last_aswer_time)

        cats = self.cats_db.find(query)


        if not cats:
            return
        closest_cats = self.matcher.find_n_closest(people, cats,max_n=self.cats_in_answer)

        # TODO fix bug and dontsend not active cats
        for cl in closest_cats:

            # cl = self.throw_sent_cats(cl)
            if len(cl.cats) > 0:
                cl.person.dt = time()
                cl.cats = self.answers_db.filter_matches(cl.person._id, cl.cats)
                if cl.cats:
                    # TODO if not ans
                    self.answers_db.add_matches(cl)
                    self.people_db.update(cl.person)
                   # self.bot_loader.match_notify(cl)
                    self.bot_loader.upload(cl)
                   #  self.bot_loader.upload_one(cl)





    def recheck_cats_in_search(self, quadkey: str):
        quadkey_query = [quadkey, "no_quad"] if "no_quad" != quadkey else ["no_quad"]
        people = self.people_db.find({"quadkey": {"$in": quadkey_query},
                                      "dt": {"$lte": time() -  self.answer_time_delay},
                                      "is_active": True})
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
        # TODO load ans from cache
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
