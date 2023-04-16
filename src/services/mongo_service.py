from abc import ABC, abstractmethod
from typing import Optional

from src.entities.base import Entity
from src.entities.cat import Cat, ClosestCats
from src.entities.answer import Answer
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
        query = {"_id": cat._id}
        updated_person = {"$set": cat.as_json_wo_none()}
        ans = self.cats_collection.update_one(query, updated_person)
        if not ans.acknowledged:
            return None

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

    def update(self, person: Person):
        query = {"_id": person._id}
        updated_person = {"$set": person.as_json_wo_none()}
        ans = self.people_collection.update_one(query, updated_person)
        if not ans.acknowledged:
            return None



class AnswersMongoClient(MongoClientBase):
    def __init__(self, db):
        self.answers_collection = db.answers
        # self.cache = CacheClient(cache_client_config)

    def save(self, answer: Answer):
        ans = self.answers_collection.insert_one(answer.as_json_wo_none())
        if not ans.acknowledged:
            return None
        else:
            return ans.inserted_id

    def find(self, query: dict):
        cursor = self.answers_collection.find(query)
        answers = list(cursor)
        answers = [Answer.from_bson(p) for p in answers]
        return answers

    def save_correct_answer(self, wanted_cat: str, cat_id: str):
        answer = Answer(
            _id=None, wanted_cat_id=wanted_cat, match_cat_id=cat_id, user_answer=1)
        return self.save(answer)


    def drop_sended_cats(self, person_id: str, match_cats: list[Cat]):
        """delete matches wich in answers yet (dont send same answers)"""
        filtered_matches = []
        for cat in match_cats:
            # query = {"wanted_cat_id": person_id, "match_cat_id": cat._id, "user_answer": -1}
            query = {"wanted_cat_id": person_id, "match_cat_id": cat._id}
            if not list(self.answers_collection.find(query)):
                filtered_matches.append(cat)

        return filtered_matches

    def add_matches(self, closest_cat: ClosestCats):
        person_id = closest_cat.person._id
        match_ids = []
        for cat in closest_cat.cats:
            answer = Answer(
                _id=None, wanted_cat_id=person_id, match_cat_id=cat._id, user_answer=-1
            )
            match_id = self.save(answer)
            match_ids.append(match_id)
        return match_ids

    def delete(self, query: dict):
        self.answers_collection.delete_one(query)

    def update(self, answer: Answer):
        """set answer value 0 - no; 1 - yes; -1 - user not answered yet"""
        query = {"_id": answer._id}
        updated_answer = {"$set": answer.as_json_wo_none()}
        ans = self.answers_collection.update_one(query, updated_answer)
        if not ans.acknowledged:
            return None