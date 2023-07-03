from abc import ABC, abstractmethod
from typing import Union

from shapely.geometry.base import BaseGeometry


class Entity(ABC):
    @abstractmethod
    def from_shapely(self, shapely_object: 'BaseGeometry') -> 'Entity':
        pass

    @property
    @abstractmethod
    def perimeter(self) -> float:
        pass

    @property
    @abstractmethod
    def to_shapely(self) -> BaseGeometry:
        pass

    def contains(self, other: 'Entity') -> bool:
        return self.to_shapely.contains(other.to_shapely)

    def intersects(self, other: 'Entity') -> bool:
        return self.to_shapely.intersects(other.to_shapely)

    def intersection(self, other: 'Entity') -> 'Entity':
        return self.to_shapely.intersection(other.to_shapely)

    def distance_to(self, other: Union[BaseGeometry, 'Entity']) -> float:
        if isinstance(other, BaseGeometry):
            return self.to_shapely.distance(other)
        return self.to_shapely.distance(other.to_shapely)

    def __repr__(self) -> str:
        return self.__str__()

    @abstractmethod
    def plot(self):
        pass
