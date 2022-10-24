import dataclasses
from dataclasses import dataclass
from inference.entities.base import Entity


@dataclass
class Person(Entity):
    chat_id: str

    def as_json_wo_none(self):
        return {key: value for key, value in dataclasses.asdict(self).items() if value is not None}