from abc import ABC, abstractmethod
from typing import List, Optional

from inference.entities.base import Entity
from inference.entities.cat import Cat
from inference.entities.person import Person


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

class PeopleMongoClient(MongoClientBase):
    def __init__(self, db):
        self.people_collection = db.people

    def delete(self, query: dict):
        self.people_collection.delete_one(dict)

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