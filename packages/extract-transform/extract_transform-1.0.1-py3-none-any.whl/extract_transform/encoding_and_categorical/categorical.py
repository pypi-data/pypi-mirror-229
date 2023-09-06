from typing import Any, Set

from extract_transform.extractor import Extractor


class Categorical(Extractor):
    """
    Validates and extracts data based on a predefined set of valid categories.

    Args:
        valid_categories (Set[str]): A set containing valid category strings.
        **kwargs: Additional keyword arguments for the base extractor.

    Expected Input:
        A string representing a category, e.g., "category_A".

    Expected Output:
        If the provided category string is in the `valid_categories` set, the input is returned as-is. Otherwise, a warning is generated and the input is still returned without alteration. The purpose of this extractor is to validate and not to modify the input.
    """

    def __init__(self, valid_categories: Set[str], **kwargs):
        super().__init__(**kwargs)
        self.valid_categories = valid_categories

    def extract(self, data: Any) -> Any:
        if data not in self.valid_categories:
            self.warn(
                f"Extracted data '{data}' is not a valid category. Valid categories are {self.valid_categories}."
            )
        return data
