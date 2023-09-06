import decimal
from typing import Any

from extract_transform.extractor import Extractor


class Decimal(Extractor):
    """
    Extracts and converts input data to a decimal value with the specified precision and scale.

    This extractor parses the input data into a decimal value and rounds it according to the provided precision and scale.

    Args:
        precision (int, optional): The total number of significant digits in the decimal number, both before and after the decimal point. Defaults to 38.
        scale (int, optional): The number of digits to the right of the decimal point. Defaults to 0.

    Expected Input:
        Any type of numeric data that can be converted to a decimal, e.g., "123.456", 123.456, "123", 123, etc.

    Expected Output:
        A decimal.Decimal value, rounded according to the specified precision and scale.
    """

    def __init__(self, precision: int = 38, scale: int = 0):
        super().__init__()
        self.precision = precision
        self.scale = scale

    def extract(self, data: Any) -> decimal.Decimal:
        d = decimal.Decimal(data)

        # Adjusting the decimal value to match the provided precision and scale
        return round(d, self.scale)
