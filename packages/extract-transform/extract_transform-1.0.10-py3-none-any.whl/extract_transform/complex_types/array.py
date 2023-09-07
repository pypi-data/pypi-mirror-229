from typing import Any, List

from extract_transform.extractor import Extractor


class Array(Extractor):
    """
    Processes input data into a list by extracting and potentially transforming each item based on a provided item extractor.

    Args:
        item_extractor (Extractor): The extractor to process each item in the array.

    Expected Input:
        A list or a single item. E.g., ["Alice", "Bob"] or "Alice".

    Expected Output:
        A list with each item processed according to the provided item extractor.
        E.g., for item_extractor as Raw(): ["Alice", "Bob"]."""

    def __init__(self, item_extractor: Extractor):
        super().__init__()
        self.item_extractor = item_extractor

    def extract(self, data: Any) -> List:
        if data is None:
            return []
        if not isinstance(data, list):
            data = [data]
        return [self.item_extractor.extract(item) for item in data]
