from typing import Any, Dict, List

from extract_transform.extractor import Extractor


class Pivot(Extractor):
    """
    Groups data items by a specified key, then applies a result extractor to each group.

    Args:
        key (str): The field to group by.
        result_extractor (Extractor): The extractor applied to each group.
        exclude_key (bool, optional): If True, removes the pivot key from each item. Defaults to True.
        single_item_per_key (bool, optional): If True and group size is 1, the item is not wrapped in a list. Defaults to False.

    Expected Input:
        List of dictionaries.

    Expected Output:
        Dictionary with keys being distinct values from the input list's 'key' field, and values
        being the result of the `result_extractor` applied to items sharing the same key.
    """

    def __init__(
        self,
        key: str,
        result_extractor: Extractor,
        exclude_key: bool = True,
        single_item_per_key: bool = False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.key = key
        self.result_extractor = result_extractor
        self.exclude_key = exclude_key
        self.single_item_per_key = single_item_per_key

    def extract(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        grouped_data = {}
        for item in data:
            key_value = item.get(self.key)
            if key_value not in grouped_data:
                grouped_data[key_value] = []
            grouped_data[key_value].append(item)

        # Remove the pivot key from each item if exclude_key is True
        if self.exclude_key:
            for group in grouped_data.values():
                for item in group:
                    if self.key in item:
                        del item[self.key]

        # Apply the result extractor to each group
        for key, group in grouped_data.items():
            if self.single_item_per_key and len(group) == 1:
                group = group[0]  # Extract single item from the list
            grouped_data[key] = self.result_extractor.extract(group)

        return grouped_data
