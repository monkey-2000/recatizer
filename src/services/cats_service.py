import logging
from typing import List

from pymongo import MongoClient

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
        self.matcher = CatsMatcher(dim=config.embedding_size)
        self.predictor = Predictor(config.s3_client_config, config.models_path, config.local_models_path)
        self.bot_loader = DataUploader(config.bot_token)



    def save_new_cat(self, cat: Cat) -> bool:
        emb = self.predictor.predict(cat.path)
        if cat.quadkey not in self.matcher.quadkey_index:
            cats = self.cats_db.find({'quadkey': cat.quadkey})
            if cats:
                self.matcher.init_index(cat.quadkey, cats)

        self.matcher.add_items(cat.quadkey, [cat])
        cat.embeddings = emb.tolist()
        ans = self.cats_db.save(cat)
        if not ans:
            logging.error("Cat wasn't saved!!!")

        #TODO start checking all people who searching their cats min(5 min, 5 new cats)
        self.__recheck_cats_in_search(cat.quadkey)
        return True

    def __find_similar_cats(self, people: List[Person]):
        quadkeys = set({person.quadkey for person in people})
        for quadkey in quadkeys:

            cats = self.cats_db.find({'quadkey': quadkey})
            if cats:
                self.matcher.init_index(quadkey, cats)
                closest_cats = self.matcher.find_top_closest(quadkey, people)
                for cl in closest_cats:
                    if cl.cats:
                        self.bot_loader.upload(cl)

    def __recheck_cats_in_search(self, quadkey: str):
        people = self.people_db.find({'quadkey': quadkey})
        self.__find_similar_cats(people)

    def delete_user(self, chat_id: str):
        self.people_db.delete({'chat_id': id})

    def add_user(self, person: Person):
        emb = self.predictor.predict(person.path)
        person.embeddings = emb.tolist()
        person = self.people_db.save(person)
        self.__find_similar_cats([person])



