import dataclasses
from dataclasses import dataclass
from typing import List, Dict, Any

from src.entities.base import Entity
from src.entities.person import Person


@dataclass
class Cat(Entity):
    additional_info: Dict[str, Any]

    def as_json_wo_none(self):

        return {key: value for key, value in dataclasses.asdict(self).items() if value is not None}

    @staticmethod
    def from_bson(bson):
        return Cat(_id=bson["_id"], path=bson["path"], quadkey=bson["quadkey"],
                   embeddings=bson["embeddings"], additional_info=bson["additional_info"])


@dataclass
class ClosestCats:
    person: Person
    cats: List[Cat]
    distances: List[float]