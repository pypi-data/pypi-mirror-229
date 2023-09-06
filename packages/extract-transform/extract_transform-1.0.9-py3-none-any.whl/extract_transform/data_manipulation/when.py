from typing import Any

from extract_transform.extractor import Extractor


class When(Extractor):
    """
    Applies an extractor based on a given condition.

    Args:
        condition_func (Callable): A function that takes data and context as arguments
                                   and returns a boolean value.
        extractor (Extractor): The extractor to be applied if the condition_func returns True.

    Expected Input:
        Any data that can be evaluated by the condition_func.

    Expected Output:
        If condition_func returns True, it's the extracted data; otherwise, None.
    """

    def __init__(self, condition_func, extractor: Extractor):
        super().__init__()
        self.condition_func = condition_func
        self.extractor = extractor

    def extract(self, data: Any) -> Any:
        if self.condition_func(data):
            return self.extractor.extract(data)
        return None
