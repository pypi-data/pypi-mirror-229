from typing import Any, Dict, Optional

from extract_transform.extractor import Extractor


class DictMap(Extractor):
    """
    Processes each value of a dictionary through a specified extractor and returns the processed dictionary.

    Args:
        extractor (Extractor): The extractor to process each value in the dictionary.

    Expected Input:
        A dictionary with arbitrary keys and values.
        E.g., {"name": "Alice", "age": "30"}.

    Expected Output:
        A dictionary with the same keys but processed values based on the provided extractor.
        E.g., for an integer extractor on the input above: {"name": "Alice", "age": 30}.
    """

    def __init__(self, extractor: Extractor, **kwargs):
        super().__init__(**kwargs)
        self.extractor = extractor

    def extract(self, data: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
        if not isinstance(data, dict):
            self.warn("Passed data is not a dict")
            return None

        return {k: self.extractor.extract(v) for k, v in data.items()}
