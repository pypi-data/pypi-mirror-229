from typing import Any, Callable, List

from extract_transform.extractor import Extractor


class Filter(Extractor):
    """
    Filters items in a list based on a given predicate.

    Expected Input:
        A list of items.

    Expected Output:
        A list of items satisfying the given predicate.
    """

    def __init__(self, predicate: Callable[[Any], bool]):
        super().__init__()
        self.predicate = predicate

    def extract(self, data: List[Any]) -> List[Any]:
        return [item for item in data if self.predicate(item)]
