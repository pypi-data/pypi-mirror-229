from typing import Any, Dict

from extract_transform.extractor import Extractor


class MapValue(Extractor):
    """
    Generic extractor to map input values to a custom representation based on a provided mapping.

    Args:
        mapping (dict): Dictionary mapping input values to desired output.
        default (Any): Default value if input doesn't match any key in the mapping.
                      If not set, it will return the input value unchanged.

    Expected Input:
        A value that might exist in the mapping.
        E.g., 1 or "apple".

    Expected Output:
        The corresponding mapped value if exists or the default value otherwise.
        E.g., for the mapping {1: "TypeA", "apple": "fruit"}:
        - Input: 1 -> Output: "TypeA"
        - Input: "orange" -> Output: "UnknownType" (if default is set to "UnknownType")

    """

    def __init__(self, mapping: Dict[Any, Any], default: Any = None):
        super().__init__()
        self.mapping = mapping
        self.default = default

    def extract(self, data: Any) -> Any:
        if data not in self.mapping:
            self.warn(
                f"Value '{data}' not found in mapping. Using default value '{self.default}'."
            )
        return self.mapping.get(data, self.default or data)
