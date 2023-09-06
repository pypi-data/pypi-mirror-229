from typing import Any, Callable, List

from extract_transform.extractor import Extractor


class Count(Extractor):
    """
    Counts the number of items in a list based on a given predicate.

    Expected Input:
        A list of items.

    Expected Output:
        An integer representing the count of items satisfying the given predicate.
    """

    def __init__(self, predicate: Callable[[Any], bool] = lambda x: True):
        super().__init__()
        self.predicate = predicate

    def extract(self, data: List[Any]) -> int:
        return len([item for item in data if self.predicate(item)])
