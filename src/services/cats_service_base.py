from abc import ABC, abstractmethod

from src.entities.cat import Cat
from src.entities.person import Person


class CatsServiceBase(ABC):
    @abstractmethod
    def delete_user(self, id: str):
        pass

    @abstractmethod
    def save_new_cat(self, cat: Cat) -> bool:
        pass

    @abstractmethod
    def add_user(self, person: Person) -> bool:
        pass
