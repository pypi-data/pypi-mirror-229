from typing import List, Optional, Union

from extract_transform.extractor import Extractor


class Sum(Extractor):
    """
    Computes the sum of a list of numeric values.

    Args:
        None

    Expected Input:
        A list of numeric values (either float or int), e.g., [1.0, 2.0, 3.0].

    Expected Output:
        A float representing the sum of the input list. For the example input [1.0, 2.0, 3.0], the output will be 6.0.
    """

    def extract(self, data: Union[List[float], List[int]]) -> Optional[float]:
        # Check if input data is a list
        if not isinstance(data, list):
            self.warn(f"Input data is not a list. Received: {type(data)}")
            return None

        # Check if the list is empty
        if not data:
            self.warn("Empty list provided for sum calculation.")
            return None

        # Check if all elements in the list are numeric
        if not all(isinstance(item, (float, int)) for item in data):
            self.warn(
                "The list contains non-numeric values. A sum can't be calculated."
            )
            return None

        return sum(data)
