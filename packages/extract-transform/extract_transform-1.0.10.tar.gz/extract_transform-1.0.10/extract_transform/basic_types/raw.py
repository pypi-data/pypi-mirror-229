from typing import Any

from extract_transform.extractor import Extractor


class Raw(Extractor):
    """
    Returns the provided data as-is without any processing or conversion.

    Expected Input:
        Any data value, e.g., 12345, "Hello", or {"key": "value"}.

    Expected Output:
        The input data is returned as-is, without any alterations. The Raw extractor does not process or change the data in any way.
    """

    def extract(self, data: Any) -> Any:
        return data
