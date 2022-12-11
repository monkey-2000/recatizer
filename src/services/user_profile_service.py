from bson import ObjectId
from pymongo import MongoClient


from src.services.mongo_service import CatsMongoClient, PeopleMongoClient, AnswersMongoClient


class UserProfileClient():

    def __init__(self, mongoDB_url: str):
        client = MongoClient(mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)
        self.answers_db = AnswersMongoClient(client.main)

    def find_all_user_cats(self, chat_id: int):
        query = {"chat_id": chat_id, "is_active": True}
        user_cats = {}
        user_cats["saw_cats"] = self.cats_db.find(query)
        user_cats["find_cats"] = self.people_db.find(query)
        return user_cats


    def find_all_cat_matches(self, cat_id):
        pass

    def set_subscription_status(self, cat_id: str, set_status: bool):
        cat_mongo_id = ObjectId(cat_id)

        cat_saw = self.cats_db.find( {"_id": cat_mongo_id})
        if cat_saw:
            cat_saw = cat_saw[0]
            cat_saw.is_active = set_status
            self.cats_db.update(cat_saw)
            return True
        cat_find = self.people_db.find({"_id": cat_mongo_id})
        if cat_find:
            cat_find = cat_find[0]
            cat_find.is_active = set_status
            self.people_db.update(cat_find)
            return True







