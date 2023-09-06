from typing import Any, Dict

from extract_transform.extractor import Extractor


class Flatten(Extractor):
    """
    Flattens a nested dictionary into a single-level dictionary with compound keys formed by joining nested keys.

    Args:
        extractor (Extractor): The extractor to process the input data before flattening.
        sep (str, optional): The separator used to join compound keys. Defaults to '.'.

    Expected Input:
        A possibly nested dictionary, e.g., {"a": {"b": 1, "c": {"d": 2}}}

    Expected Output:
        A single-level dictionary with compound keys, e.g., {"a.b": 1, "a.c.d": 2}
    """

    def __init__(self, extractor: Extractor, sep: str = "."):
        super().__init__()
        self.extractor = extractor
        self.sep = sep

    def extract(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data = self.extractor.extract(data)

        def _flatten(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
            items = {}
            for k, v in d.items():
                key = f"{prefix}{self.sep}{k}" if prefix else k
                items.update({key: v} if not isinstance(v, dict) else _flatten(v, key))
            return items

        return _flatten(data)
