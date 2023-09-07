from typing import Any, Dict, List, Union

from extract_transform.extractor import Extractor


class Ordinal(Extractor):
    """
    Encodes input data into an ordinal representation based on predefined ordered categories or an explicit mapping.

    Args:
        ordered_categories (Union[List[str], Dict[str, int]]):
            - If provided a list of category strings, it will be treated in their respective ordinal order.
            - If provided a dictionary, it will map category strings to their respective ordinal positions.
        **kwargs: Additional keyword arguments for the base extractor.

    Attributes:
        ordered_categories (List[str]): A list of category strings.
        ordinal_map (Dict[str, int]): A mapping of category strings to their respective ordinal positions.

    Expected Input:
        A string representing a category, e.g., "medium".

    Expected Output:
        An integer representing the ordinal position of the input category.
        For example:
        - If `ordered_categories` is ["low", "medium", "high"] and the input is "medium", the output will be 1.
        - If `ordered_categories` is {"low": 0, "medium": 5, "high": 10} and the input is "medium", the output will be 5.
    """

    def __init__(self, ordered_categories: Union[List[str], Dict[str, int]], **kwargs):
        super().__init__(**kwargs)

        if isinstance(ordered_categories, dict):
            self.ordinal_map = ordered_categories
            self.ordered_categories = list(ordered_categories.keys())
        else:
            self.ordered_categories = ordered_categories
            self.ordinal_map: Dict[str, int] = {
                category: idx for idx, category in enumerate(self.ordered_categories)
            }

    def extract(self, data: Any) -> int:
        if data not in self.ordinal_map:
            self.warn(
                f"Unexpected ordinal value: '{data}'. Expected one of {self.ordered_categories}."
            )
            return -1  # or you can choose a more appropriate default value
        return self.ordinal_map[data]
