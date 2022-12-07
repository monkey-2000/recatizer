from pymongo import MongoClient


from src.services.mongo_service import CatsMongoClient, PeopleMongoClient


class UserProfileClient():

    def __init__(self, mongoDB_url: str):
        client = MongoClient(mongoDB_url)
        self.cats_db = CatsMongoClient(client.main)
        self.people_db = PeopleMongoClient(client.main)


    def find_all_user_cats(self, chat_id: int):
        query = {"chat_id": chat_id}
        user_cats = {}
        user_cats["saw_cats"] = self.cats_db.find(query)
        user_cats["find_cats"] = self.people_db.find(query)
        return user_cats





