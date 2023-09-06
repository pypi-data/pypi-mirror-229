import decimal
from typing import Any, Dict, Optional, Union

from extract_transform.basic_types.decimal import Decimal
from extract_transform.basic_types.float import Float
from extract_transform.basic_types.integer import Integer
from extract_transform.extractor import Extractor


class NumericWithCodes(Extractor):
    """
    Extracts numeric values from the input data and categorizes them based on specified boundaries.
    If the extracted value lies within the boundaries, it is returned as-is. Otherwise, it is returned as a string.

    Args:
        base_extractor (Extractor): An extractor to retrieve the numeric value. Should be of type Integer, Float, or Decimal.
        min_val (float): The minimum boundary for numeric categorization.
        max_val (float): The maximum boundary for numeric categorization.

    Expected Input:
        A numeric value or representation, e.g., 5, 5.0, "5.0", or Decimal('5.0').

    Expected Output:
        A dictionary with 'value' and 'categorical' keys.
        For a value of 5 and boundaries of 1 and 10: {"value": 5, "categorical": None}.
        For a value of 15 and boundaries of 1 and 10: {"value": None, "categorical": "15"}.
    """

    def __init__(self, base_extractor: Extractor, min_val: float, max_val: float):
        super().__init__()
        assert isinstance(
            base_extractor, (Integer, Float, Decimal)
        ), "Base extractor should be of numeric type"
        self.base_extractor = base_extractor
        self.min_val = min_val
        self.max_val = max_val

    def extract(
        self, data: Any
    ) -> Dict[str, Optional[Union[int, float, decimal.Decimal, str]]]:
        value = self.base_extractor.extract(data)

        if value is None:
            return {"value": None, "categorical": None}

        if self.min_val <= value <= self.max_val:
            return {"value": value, "categorical": None}

        return {"value": None, "categorical": str(value)}
