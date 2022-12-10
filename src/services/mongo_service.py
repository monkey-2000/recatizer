from abc import ABC, abstractmethod
from typing import Optional

from src.entities.base import Entity
from src.entities.cat import Cat
from src.entities.person import Person


class MongoClientBase(ABC):
    @abstractmethod
    def delete(self, query: dict):
        pass

    @abstractmethod
    def find(self, query: dict):
        pass

    @abstractmethod
    def save(self, entity: Entity) -> Optional[Entity]:
        pass


class CatsMongoClient(MongoClientBase):
    def __init__(self, db):
        self.cats_collection = db.cats

    def delete(self, query: dict):
        self.cats_collection.delete_one(dict)

    def find(self, query: dict):
        cursor = self.cats_collection.find(query)
        cats = list(cursor)
        cats = [Cat.from_bson(cat) for cat in cats]
        return cats

    def save(self, cat: Cat) -> Optional[Cat]:
        ans = self.cats_collection.insert_one(cat.as_json_wo_none())
        cat._id = ans.inserted_id
        if not ans.acknowledged:
            return None
        return cat

    def update(self, cat: Cat):
       query = {'_id': cat._id}
       updated_person = {"$set": cat.as_json_wo_none()}
       ans = self.cats_collection.update_one(query, updated_person)
       if not ans.acknowledged:
           return None

class PeopleMongoClient(MongoClientBase):
    def __init__(self, db):
        self.people_collection = db.people

    def delete(self, query: dict):
        self.people_collection.delete_one(query)

    def save(self, person: Person) -> Optional[Person]:
        ans = self.people_collection.insert_one(person.as_json_wo_none())
        person._id = ans.inserted_id
        if not ans.acknowledged:
            return None
        return person

    def find(self, query: dict):
        cursor = self.people_collection.find(query)
        people = list(cursor)
        people = [Person.from_bson(p) for p in people]
        return people

    def update(self, person: Person):
        query = {'_id': person._id}
        updated_person = {"$set": person.as_json_wo_none()}
        ans = self.people_collection.update_one(query, updated_person)
        if not ans.acknowledged:
            return None
