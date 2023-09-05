from typing import Tuple
from dataclasses import dataclass


@dataclass
class Dataset(object):
    id: int
    key: str
    shape: Tuple[int]
    ndim: int
    type: str
    is_shared: bool
