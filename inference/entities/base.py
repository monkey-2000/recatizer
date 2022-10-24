import abc
from dataclasses import dataclass
from typing import Optional

import numpy as np

@dataclass
class Entity(abc.ABC):
    _id: Optional[str]
    path: str
    quadkey: str
    embeddings: Optional[np.ndarray]