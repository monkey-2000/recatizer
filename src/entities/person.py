import dataclasses
from dataclasses import dataclass
from src.entities.base import Entity


@dataclass
class Person(Entity):

    def as_json_wo_none(self):
        return {
            key: value
            for key, value in dataclasses.asdict(self).items()
            if value is not None
        }

    @classmethod
    @staticmethod
    def from_bson(bson):
        return Person(
            _id=bson["_id"],
            paths=bson["paths"],
            quadkey=bson["quadkey"],
            embeddings=bson["embeddings"],
            is_active=bson["is_active"],
            additional_info=bson["additional_info"],
            chat_id=bson["chat_id"],
            dt=bson["dt"]
        )
