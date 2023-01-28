import abc
import dataclasses
from dataclasses import dataclass
from typing import Optional


@dataclass
class AnswerEntity(abc.ABC):
    _id: Optional[str]
    wanted_cat_id: str
    match_cat_id: str
    user_answer: int


class Answer(AnswerEntity):
    def as_json_wo_none(self):
        return {
            key: value
            for key, value in dataclasses.asdict(self).items()
            if value is not None
        }

    @classmethod
    @staticmethod
    def from_bson(bson):
        return Answer(
            _id=bson["_id"],
            wanted_cat_id=bson["wanted_cat_id"],
            match_cat_id=bson["match_cat_id"],
            user_answer=bson["user_answer"],
        )
