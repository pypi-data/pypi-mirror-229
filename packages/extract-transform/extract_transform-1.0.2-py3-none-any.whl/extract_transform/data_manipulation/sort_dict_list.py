from typing import Any, Dict, List, Optional

from extract_transform.extractor import Extractor


class SortDictList(Extractor):
    """
    Sorts a list of dictionaries based on a specified key within each dictionary.

    Args:
        sort_key (str): The dictionary key by which to sort the list of dictionaries.

    Expected Input:
        A list of dictionaries with consistent keys, e.g., [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}].

    Expected Output:
        A sorted list of dictionaries based on the specified `sort_key`, e.g., for `sort_key="age"`:
        [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}].
    """

    def __init__(self, sort_key: str, **kwargs):
        super().__init__(**kwargs)
        self.sort_key = sort_key

    def extract(self, data: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        if not isinstance(data, list):
            self.warn("Passed data is not a list")
            return None

        return sorted(data, key=lambda x: int(x.get(self.sort_key, 0)))
