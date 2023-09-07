from typing import Any, Dict, List

from extract_transform.extractor import Extractor


class OneHot(Extractor):
    """
    Encodes input data into a one-hot representation based on predefined categories.

    Args:
        categories (List[str]): A list containing valid category strings for encoding.
        **kwargs: Additional keyword arguments for the base extractor.

    Expected Input:
        A string representing a category, e.g., "category_A".

    Expected Output:
        A dictionary where keys are the predefined categories and values are either 1 or 0, indicating the presence or absence of the input category. For example, if `categories` is ["category_A", "category_B", "category_C"] and the input is "category_A", the output will be {"category_A": 1, "category_B": 0, "category_C": 0}.
    """

    def __init__(self, categories: List[str], **kwargs):
        super().__init__(**kwargs)
        self.categories = categories

    def extract(self, data: Any) -> Dict[str, int]:
        one_hot_vector = {}
        for category in self.categories:
            one_hot_vector[category] = 1 if data == category else 0
        return one_hot_vector
