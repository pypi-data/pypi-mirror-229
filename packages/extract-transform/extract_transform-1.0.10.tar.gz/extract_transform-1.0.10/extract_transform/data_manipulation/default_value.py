from typing import Any

from extract_transform.extractor import Extractor


class DefaultValue(Extractor):
    """
    Returns the input data if it's not None, otherwise returns a default value.

    Args:
        default_value (Any): The default value to be returned if the input data is None.
        **kwargs: Additional keyword arguments for the base extractor.

    Expected Input:
        Any data type or None.

    Expected Output:
        The input data if it's not None. If the input is None, the default value is returned.
    """

    def __init__(self, default_value: Any, **kwargs):
        super().__init__(**kwargs)
        self.default_value = default_value

    def extract(self, data: Any) -> Any:
        return data if data is not None else self.default_value
