from typing import Any, Dict, List

from extract_transform.extractor import Extractor


class Unpivot(Extractor):
    """
    Transforms a dictionary into a list of dictionaries with specified key-value pairs.

    Args:
        key (str): The field that will be used to store the original dictionary's keys.
        result_extractor (Extractor): The extractor applied to the dictionary's values.

    Expected Input:
        Dictionary with values being lists.

    Expected Output:
        List of dictionaries with each dictionary having two keys:
        1) 'category' storing the original dictionary's key.
        2) 'value' storing the extracted value from the original dictionary's value list.
    """

    def __init__(self, key: str, result_extractor: Extractor, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.result_extractor = result_extractor

    def extract(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        unpivoted_data = []
        for key, values in data.items():
            for value in values:
                new_dict = {
                    "category": key,
                    "value": self.result_extractor.extract(value),
                }
                unpivoted_data.append(new_dict)
        return unpivoted_data
