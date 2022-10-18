import dataclasses
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class Person:
    _id: Optional[str]
    chat_id: str
    path: str
    quadkey: str
    embeddings: List
    additional_info: Dict[str, Any]

    def as_json_wo_none(self):
        return {key: value for key, value in dataclasses.asdict(self).items() if value is not None}