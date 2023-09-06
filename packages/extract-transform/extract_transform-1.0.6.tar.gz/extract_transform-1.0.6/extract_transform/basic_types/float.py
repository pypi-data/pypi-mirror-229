from typing import Any

from extract_transform.extractor import Extractor


class Float(Extractor):
    """Extracts and converts input data to a float value.

    This extractor is designed to parse various input data types and convert them into a float value. The goal is to provide a unified method to extract floating-point numbers from various input sources, regardless of their initial format.

    Expected Input:
        Any type of data that can be converted to a float, e.g., "123.456", 123.456, "123", 123, etc.

    Expected Output:
        A float value parsed from the input data.
    """

    def extract(self, data: Any) -> float:
        return float(data)
