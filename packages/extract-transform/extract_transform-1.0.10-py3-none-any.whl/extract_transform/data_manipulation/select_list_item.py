from typing import Any, Callable, List, Optional

from extract_transform.extractor import Extractor


class SelectListItem(Extractor):
    """
    Retrieves a specific item from a list based on its position or a given criteria.

    Args:
        position (int, optional): Index of the desired item. Defaults to the first item.
        criteria (Callable[[Any], Any], optional): Function that identifies the desired item.

    Expected Input:
        A list, e.g., [1, 2, 3, 4].

    Expected Output:
        Based on position or criteria, e.g., for position 2: 3.
    """

    def __init__(
        self,
        position: int = 0,
        criteria: Optional[Callable[[Any], Any]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.position = position
        self.criteria = criteria

    def extract(self, data: List[Any]) -> Any:
        if not isinstance(data, list):
            return None

        if self.criteria:
            for item in data:
                if self.criteria(item):
                    return item
            return None

        if 0 <= self.position < len(data):
            return data[self.position]
        else:
            self.warn(
                f"Provided position {self.position} is out of bounds for data of length {len(data)}."
            )
            return None
