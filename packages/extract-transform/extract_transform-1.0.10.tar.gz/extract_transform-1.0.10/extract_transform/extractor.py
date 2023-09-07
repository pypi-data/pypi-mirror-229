from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Optional


class Extractor(ABC):
    """
    An abstract base class for all extractor classes. The purpose of an extractor is to validate,
    transform, and extract specific data types from a given input based on its unique logic.

    Args:
        raise_on_warning (Optional[bool]): Override the default behavior on encountering a warning.
                                           If not specified, DEFAULT_RAISE_ON_WARNING is used.
    """

    DEFAULT_RAISE_ON_WARNING = False

    def __init__(self, raise_on_warning: Optional[bool] = None):
        self.logger = getLogger(__name__)
        self.raise_on_warning = (
            raise_on_warning
            if raise_on_warning is not None
            else self.DEFAULT_RAISE_ON_WARNING
        )

    @abstractmethod
    def extract(self, data: Any) -> Any:
        ...

    def warn(self, message: str):
        if self.raise_on_warning:
            raise RuntimeError(f"Warning raised as exception: {message}")
        else:
            self.logger.warning(message)
