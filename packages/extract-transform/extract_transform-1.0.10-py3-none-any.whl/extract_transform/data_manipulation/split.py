from typing import Any, List

from extract_transform.extractor import Extractor


class Split(Extractor):
    """
    Extracts substrings by splitting a string at every occurrence of the specified separator
    and then applies a given extractor to each split substring.

    Args:
        sep (str): The separator/delimiter on which to split the string.
        result_extractor (Extractor): An extractor that will be applied to each split substring.

    Expected Input:
        A string that contains one or more occurrences of the `sep`, e.g., "Apple,Banana,Cherry".

    Expected Output:
        A list containing the extracted values from the substrings after applying the `result_extractor`,
        e.g., for `sep=","` and a basic string extractor, the output would be: ["Apple", "Banana", "Cherry"].
    """

    def __init__(self, sep: str, result_extractor: Extractor, **kwargs):
        super().__init__(**kwargs)
        self.sep = sep
        self.result_extractor = result_extractor

    def extract(self, data: Any) -> List[Any]:
        # First, ensure the data is a string
        string_data = str(data)

        # Split the string
        split_strings = string_data.split(self.sep)

        # Apply the result_extractor to each split string
        return [self.result_extractor.extract(item) for item in split_strings]
