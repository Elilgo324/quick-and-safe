from abc import ABC, abstractmethod
from typing import Union

from shapely.geometry.base import BaseGeometry


class Entity(ABC):
    @property
    @abstractmethod
    def to_shapely(self) -> BaseGeometry:
        pass

    def distance_to(self, other: Union[BaseGeometry, 'Entity']) -> float:
        if isinstance(other, BaseGeometry):
            return self.to_shapely.distance(other)
        return self.to_shapely.distance(other.to_shapely)

    @abstractmethod
    def plot(self):
        pass
