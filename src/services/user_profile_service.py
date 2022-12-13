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
# TODO need to connection via tables. The unsub, dont show matches with cat
    def get_wanted_cats(self, chat_id: int):
        query = {"chat_id": chat_id, "is_active": True}
        user_cats = self.people_db.find(query)
        return user_cats

    def get_saw_cats(self, chat_id: int):
        query = {"chat_id": chat_id, "is_active": True}
        user_cats = self.cats_db.find(query)
        return user_cats

    def get_answers(self, wanted_cat_id: str):
        wanted_cat_id = ObjectId(wanted_cat_id)
        query = {"wanted_cat_id": wanted_cat_id}
        user_cats = self.answers_db.find(query)
        return user_cats


    def cats_dbfind(self, query):
        return self.cats_db.find(query)

    # def get_matche(self, match_cat_id: ObjectId):
    #
    #     query =  {"_id": match_cat_id}
    #     match_cats = self.cats.find(query)
    #     return match_cats

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







