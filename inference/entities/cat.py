from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Cat:
    id: str
    path: str
    quadkey: str
    embeddings: List
    additional_info: Dict[str, Any]
