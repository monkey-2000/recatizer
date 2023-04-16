import abc
from dataclasses import dataclass
from typing import Optional, List

import numpy as np


@dataclass
class Entity(abc.ABC):
    _id: Optional[str]
    paths: str
    quadkey: str
    embeddings: Optional[List[float]]
    is_active: True  # Unsubscribed or not
    additional_info: dict
    dt: float
    chat_id: int
