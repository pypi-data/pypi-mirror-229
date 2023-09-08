from enum import Enum, unique
from typing import Union


@unique
class StreamLogID(Enum):
    OMMStream = 0.1
    RDPStream = 0.2
    OffStreamContrib = 0.3
    PrvDictionaryStream = 0.4

    def __add__(self, other: Union[int, float]) -> Union[int, float]:
        return other + self.value

    def __radd__(self, other: Union[int, float]) -> Union[int, float]:
        return self.__add__(other)
