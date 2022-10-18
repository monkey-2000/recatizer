from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Person:
    id: str
    session: str
    path: str
    quadkey: str
    embeddings: List
    additional_info: Dict[str, Any]