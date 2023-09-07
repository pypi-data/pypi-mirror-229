from typing import Any

from extract_transform.extractor import Extractor


class Hexadecimal(Extractor):
    """
    Converts a hexadecimal string to its integer representation.

    Expected Input:
        A string representing a hexadecimal value, e.g., "1a3f".

    Expected Output:
        An integer that is the conversion of the hexadecimal input. If conversion fails, returns 0 and logs a warning.
    """

    def extract(self, data: Any) -> int:
        try:
            return int(data, 16)
        except ValueError:
            self.warn(f"Invalid hexadecimal value: {data}")
            return 0
