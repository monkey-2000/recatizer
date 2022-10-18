from typing import List

from inference.cats_service_base import CatsServiceBase
from inference.entities.cat import Cat
from inference.entities.person import Person


class DebugCatsService(CatsServiceBase):

    def __init__(self):
        self.people = [self.__build_person()]
        self.cats = [self.__build_cat()]

    def __build_person(self):
        return Person(_id ="0", chat_id="123", path="<LOCAL_PATH>", quadkey="03311101211",
                      embeddings=[], additional_info = dict())

    def __build_cat(self):
        return Cat(_id ="0", path="/home/dataset", quadkey="03311101211",
                      embeddings=[], additional_info=dict())


    def save_new_cat(self, cat: Cat) -> bool:
        self.cats.append(cat)
        return True

    def find_similar_cats(self, cat: Cat) -> List[Cat]:
        return self.cats

    def delete_user(self, id: str):
        self.people = [p for p in self.people if p._id != id]


    def add_user(self, person: Person) -> bool:
        self.people.append(person)
        return True