"""Interfaces."""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cyberfusion.ClusterSupport import ClusterSupport


class APIObjectInterface(metaclass=ABCMeta):
    """Interface for API object."""

    def __init__(self, support: "ClusterSupport") -> None:
        """Set attributes."""
        self.support = support

    @abstractmethod
    def _set_attributes_from_model(
        self,
        obj: dict,
    ) -> None:
        """Set class attributes from API output."""
        pass

    @classmethod
    def _build(
        cls,
        support: "ClusterSupport",
        obj: dict,
    ) -> "APIObjectInterface":
        """Build class from dict with object attributes."""
        class_ = cls(support)

        class_._set_attributes_from_model(obj)

        return class_
