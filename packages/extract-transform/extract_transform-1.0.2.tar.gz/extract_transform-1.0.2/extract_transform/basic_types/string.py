from typing import Any

from extract_transform.extractor import Extractor


class String(Extractor):
    """
    Converts the provided data into its string representation.

    Expected Input:
        Any data value, e.g., 12345, True, or [1, 2, 3].

    Expected Output:
        A string representation of the input data, e.g., "12345", "True", or "[1, 2, 3]".
    """

    def extract(self, data: Any) -> str:
        return str(data)
