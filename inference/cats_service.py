from typing import List


from pymongo import MongoClient
from inference.cats_service_base import CatsServiceBase
from inference.configs.db_config import DBConfig
from inference.entities.cat import Cat
from inference.entities.person import Person
from inference.matcher import CatsMatcher


class CatsService(CatsServiceBase):

    def __init__(self, config: DBConfig):
        self.client = MongoClient(config.mongoDB_url)
        self.matcher = CatsMatcher()
        self.db = self.client.recatinizer
        self.cats_collection = self.db.cats
        self.people_collection = self.db.people

    def save_new_cat(self, cat: Cat) -> bool:
        ans = self.cats_collection.insert_one(cat.as_json_wo_none())
        cat._id = ans.inserted_id
        return ans.acknowledged

    def find_similar_cats(self, cat: Cat) -> List[Cat]:
        cursor = self.cats_collection.find()
        cats = list(cursor)
        cats = [Cat.from_bson(cat) for cat in cats]
        return self.matcher.find_n_closest(cat, cats)

    def delete_user(self, id: str):
        self.people_collection.delete_one({'_id': id})

    def add_user(self, person: Person) -> bool:
        ans = self.people_collection.insert_one(person.as_json_wo_none())
        person._id = ans.inserted_id
        return ans.acknowledged

if __name__ == '__main__':
    config = DBConfig(mongoDB_url="mongodb://localhost:27017/")
    service = CatsService(config)
    cat = Cat(_id =None, path="<LOCAL_PATH>", quadkey="03311101211",
                      embeddings=[], additional_info=dict())
    service.save_new_cat(cat)
    res = service.find_similar_cats(cat)

    person = Person(_id=None, chat_id="123", path="<LOCAL_PATH>", quadkey="03311101211",
           embeddings=[], additional_info=dict())

    service.add_user(person)
    res2 = service.delete_user(person.chat_id)
    print(res, res2)