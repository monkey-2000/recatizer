import dataclasses
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Cat:
    _id: Optional[str]
    path: str
    quadkey: str
    embeddings: List
    additional_info: Dict[str, Any]

    def as_json_wo_none(self):
        return {key: value for key, value in dataclasses.asdict(self).items() if value is not None}

    @staticmethod
    def from_bson(bson):
        return Cat(_id=bson["_id"], path=bson["path"], quadkey=bson["quadkey"],
                   embeddings=bson["embeddings"], additional_info=bson["additional_info"])
