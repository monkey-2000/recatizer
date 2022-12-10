import dataclasses
from dataclasses import dataclass
from typing import List, Dict, Any

from src.entities.base import Entity
from src.entities.person import Person


@dataclass
class Cat(Entity):
    person_name: str
    def as_json_wo_none(self):

        return {
            key: value
            for key, value in dataclasses.asdict(self).items()
            if value is not None
        }

    @staticmethod
    def from_bson(bson):
        return Cat(
            _id=bson["_id"],
            paths=bson["paths"],
            quadkey=bson["quadkey"],
            embeddings=bson["embeddings"],
            is_active=bson["is_active"],
            additional_info=bson["additional_info"],
            chat_id=bson["chat_id"],
            person_name=bson["person_name"],
            dt=bson["dt"]
        )


@dataclass
class ClosestCats:
    person: Person
    cats: List[Cat]
    distances: List[float]
