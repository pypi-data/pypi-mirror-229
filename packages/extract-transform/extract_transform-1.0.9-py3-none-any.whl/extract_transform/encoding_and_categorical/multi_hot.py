from typing import List

from extract_transform.extractor import Extractor


class MultiHot(Extractor):
    """
    Encodes input data into a multi-hot representation based on predefined categories.

    Args:
        categories (List[str]): A list containing valid category strings for encoding.
        **kwargs: Additional keyword arguments for the base extractor.

    Expected Input:
        A list of strings, each representing a category, e.g., ["category_A", "category_B"].

    Expected Output:
        A list of integers (either 0 or 1), indicating the presence or absence of each category in the predefined `categories` list. For example, if `categories` is ["category_A", "category_B", "category_C"] and the input is ["category_A", "category_B"], the output will be [1, 1, 0].
    """

    def __init__(self, categories: List[str], **kwargs):
        super().__init__(**kwargs)
        self.categories = categories

    def extract(self, data: List[str]) -> List[int]:
        # Initialize a list with zeros
        encoding = [0] * len(self.categories)

        # Set corresponding indices to 1 based on the data
        for item in data:
            if item in self.categories:
                encoding[self.categories.index(item)] = 1
            else:
                self.warn(f"'{item}' not found in categories. Ignoring this value.")

        return encoding
