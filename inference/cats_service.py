from abc import ABC, abstractmethod
from typing import List

from inference.entities.cat import Cat


class CatsServiceBase(ABC):

    @abstractmethod
    def delete_user(self, id: str):
        pass

    @abstractmethod
    def find_similar_cats(self, cat: Cat) -> List[Cat]:
        pass

    @abstractmethod
    def save_new_cat(self, cat: Cat) -> bool:
        pass