from typing import Any, Optional

from extract_transform.extractor import Extractor


class Union(Extractor):
    """
    Extractor that sequentially tries multiple conditions and returns the result of the first successful one.

    Args:
        conditions (Extractor): Extractors to try in order.
        default (Optional[Extractor]): Extractor to use if none of the conditions match.

    Expected Input:
        Any data that at least one of the extractors can process.

    Expected Output:
        Result of the first successful extractor or the default if provided.
    """

    def __init__(self, *conditions: Extractor, default: Optional[Extractor] = None):
        super().__init__()
        self.conditions = conditions
        self.default = default

    def extract(self, data: Any) -> Any:
        for condition in self.conditions:
            try:
                return condition.extract(data)
            except Exception:
                continue
        # If none of the conditions match and a default extractor is provided, use it
        if self.default:
            return self.default.extract(data)

        raise ValueError(f"No extractors matched the provided data: {data}")
