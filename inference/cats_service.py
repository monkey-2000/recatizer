import logging
from typing import List

from pymongo import MongoClient

from inference.bot_loader import DataUploader
from inference.cats_service_base import CatsServiceBase
from inference.configs.service_config import ServiceConfig, default_service_config
from inference.entities.cat import Cat
from inference.entities.person import Person
from inference.matcher import CatsMatcher, Predictor
from inference.mongo_service import CatsMongoClient, PeopleMongoClient


class CatsService(CatsServiceBase):

    def __init__(self, config: ServiceConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.matcher = CatsMatcher()
        self.predictor = Predictor(config.s3_client_config)
        self.bot_loader = DataUploader(config.bot_token)



    def save_new_cat(self, cat: Cat) -> bool:
        emb = self.predictor.predict(cat.path)
        cat.embeddings = emb.tolist()
        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        #TODO start checking all people who searching their cats min(5 min, 5 new cats)
        self.__recheck_cats_in_search(cat.quadkey)
        return True

    def __find_similar_cats(self, people: List[Person]):
        qudkeys = list({person.quadkey for person in people})
        cats = self.cats_db.find({'quadkey': {"$in": qudkeys}})
        if not cats:
            return
        closest_cats = self.matcher.find_n_closest(people, cats)
        for cl in closest_cats:
            if cl.cats:
                self.bot_loader.upload(cl)

    def __recheck_cats_in_search(self, quadkey: str):
        people = self.people_db.find({'quadkey': quadkey})
        self.__find_similar_cats(people)

    def delete_user(self, chat_id: str):
        self.people_db.delete({'chat_id': id})

    def add_user(self, person: Person):
        #for path in person.path: !!!
        emb = self.predictor.predict(person.path)
        person.embeddings = emb.tolist()
        person = self.people_db.save(person)
        self.__find_similar_cats([person])

if __name__ == '__main__':
    service = CatsService(default_service_config)


