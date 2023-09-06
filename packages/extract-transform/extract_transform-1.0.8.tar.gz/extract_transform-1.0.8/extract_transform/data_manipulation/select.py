from typing import Any, Dict, Optional

from extract_transform.basic_types.raw import Raw
from extract_transform.extractor import Extractor


class Select(Extractor):
    """
    Retrieves a value from a dictionary based on a specified key and optionally processes it with another extractor.

    Args:
        key (str): The dictionary key for which value is to be retrieved.
        extractor (Extractor, optional): The extractor to process the selected value. Defaults to Raw() which returns the value as-is.

    Expected Input:
        A dictionary, e.g., {"name": "Alice", "age": 30}.

    Expected Output:
        Based on the key and optional extractor provided, e.g., for key "name": "Alice".
    """

    def __init__(self, key: str, extractor: Optional[Extractor] = None):
        super().__init__()
        self.key = key
        self.extractor = extractor if extractor is not None else Raw()

    def extract(self, data: Dict[str, Any]) -> Any:
        selected_data = data.get(self.key, None)
        return self.extractor.extract(selected_data)
