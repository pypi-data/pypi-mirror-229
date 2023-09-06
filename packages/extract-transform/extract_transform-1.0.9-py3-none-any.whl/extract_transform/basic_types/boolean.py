from typing import Any, List, Union

from extract_transform.extractor import Extractor


class Boolean(Extractor):
    """
    Converts input data to a boolean value based on provided truthy and falsy values.

    This extractor evaluates the input data against a list of truthy and falsy values to determine its boolean equivalent. If the data doesn't match any of these predefined values, Python's standard boolean conversion is used.

    Args:
        truthy_values (List[Union[str, int]], optional): A list of values that should be interpreted as `True`. Defaults to ["true", 1].
        falsy_values (List[Union[str, int]], optional): A list of values that should be interpreted as `False`. Defaults to ["false", 0].

    Expected Input:
        Any type of data, e.g., "true", "false", 1, 0, "yes", "no", etc.

    Expected Output:
        A boolean value (`True` or `False`).

    Notes:
        - Input data is first converted to string and then compared with truthy and falsy values in a case-insensitive manner.
        - If input data doesn't match any of the predefined truthy or falsy values, Python's default boolean conversion (`bool()`) is applied to the data.
    """

    def __init__(
        self,
        truthy_values: List[Union[str, int]] = ["true", 1],
        falsy_values: List[Union[str, int]] = ["false", 0],
    ):
        super().__init__()
        self.truthy_values = truthy_values
        self.falsy_values = falsy_values

    def extract(self, data: Any) -> bool:
        if str(data).lower() in [str(v).lower() for v in self.truthy_values]:
            return True
        elif str(data).lower() in [str(v).lower() for v in self.falsy_values]:
            return False
        return bool(data)
