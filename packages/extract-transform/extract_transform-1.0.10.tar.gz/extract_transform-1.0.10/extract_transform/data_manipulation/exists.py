from typing import Any

from extract_transform.extractor import Extractor


class Exists(Extractor):
    """
    Checks whether a specified key exists in the given data.

    Args:
        key (Any): The key to be checked for its existence in the data.

    Expected Input:
        Any data type that supports the "in" operation, typically a dictionary or a list.
        E.g., for dictionaries: {"name": "Alice", "age": 30}.
        And for lists: ["Alice", "Bob", "Charlie"].

    Expected Output:
        A boolean value indicating the existence of the key in the data.
        E.g., for the key "name" and the dictionary input above: True."""

    def __init__(self, key: Any, **kwargs):
        super().__init__(**kwargs)
        self.key = key

    def extract(self, data: Any) -> bool:
        return self.key in data
