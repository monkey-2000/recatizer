import logging
from typing import List


from pymongo import MongoClient
from inference.cats_service_base import CatsServiceBase
from inference.configs.db_config import DBConfig, default_db_config
from inference.entities.cat import Cat
from inference.entities.person import Person
from inference.matcher import CatsMatcher, Predictor
from inference.mongo_service import CatsMongoClient, PeopleMongoClient


class CatsService(CatsServiceBase):

    def __init__(self, config: DBConfig):
        client = MongoClient(config.mongoDB_url)
        self.cats_db = CatsMongoClient(client.recatinizer)
        self.people_db = PeopleMongoClient(client.recatinizer)
        self.matcher = CatsMatcher()
        self.predictor = Predictor()



    def save_new_cat(self, cat: Cat) -> bool:
        emb = self.predictor.predict(cat.path)
        cat.embeddings = emb
        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        #TODO start checking all people who searching their cats min(5 min, 5 new cats)
        self.__recheck_cats_in_search(cat.quadkey)
        return True

    def __find_similar_cats(self, people: List[Person]):
        qudkeys = list({person.quadkey for person in people})
        cats = self.cats_db.find({'quadkey': {"$in": qudkeys}})
        closest_cats = self.matcher.find_n_closest(people, cats)
        for person, cats_for_person in zip(people, closest_cats):
            if cats_for_person:
                print(cats_for_person)
                # TODO Add sending to bot message

    def __recheck_cats_in_search(self, quadkey: str):
        people = self.people_db.find({'quadkey': quadkey})
        self.__find_similar_cats(people)

    def delete_user(self, chat_id: str):
        self.people_db.delete({'chat_id': id})

    def add_user(self, person: Person):
        emb = self.predictor.predict(person.path)
        person.embeddings = emb
        person = self.people_db.save(person)
        self.__find_similar_cats([person])

if __name__ == '__main__':
    service = CatsService(default_db_config)
