from typing import Any, Dict, Optional, Union

from extract_transform.extractor import Extractor


class Record(Extractor):
    """
    Processes a dictionary of data by extracting and potentially transforming values based on provided field mappings.

    Args:
        field_mapping (Dict[Union[str, tuple], Extractor]): A mapping of field keys to their respective extractors.
        The key can either be a string (used for both source and destination) or a tuple (source_key, destination_key).

    Expected Input:
        A dictionary with fields that match the keys provided in the field mapping.
        E.g., {"name": "Alice", "age": 30} if field mapping contains keys "name" and "age".

    Expected Output:
        A new dictionary with fields mapped and potentially transformed according to the provided field mappings.
        E.g., for a field mapping of {"name": Raw(), "age": ToInt()}: {"name": "Alice", "age": 30}.
    """

    def __init__(self, field_mapping: Dict[Union[str, tuple], Extractor]):
        super().__init__()
        self.field_mapping = field_mapping

    def extract(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if data is None:
            return None

        output = {}
        for field, extractor in self.field_mapping.items():
            key = field if isinstance(field, str) else field[1]
            data_key = field if isinstance(field, str) else field[0]

            if extractor is None:
                continue

            value = data.get(data_key, None)

            if value is None:
                output[key] = None
            else:
                output[key] = extractor.extract(value)

        return output
