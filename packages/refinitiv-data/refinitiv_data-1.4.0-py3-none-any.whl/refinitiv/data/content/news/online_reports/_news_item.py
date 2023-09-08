from dataclasses import dataclass
from typing import List

from numpy import datetime64


@dataclass
class NewsItem:
    first_created: datetime64
    version_created: datetime64
    first_paragraph: str
    image_ids: List[str]
