from typing import Any

from extract_transform.extractor import Extractor


class Integer(Extractor):
    """
    Converts a given data to its integer representation.

    Expected Input:
        A value that can be converted to an integer, e.g., "12345" or 12345.

    Expected Output:
        An integer representation of the input. Raises a ValueError if the conversion is not possible.
    """

    def extract(self, data: Any) -> int:
        return int(data)
