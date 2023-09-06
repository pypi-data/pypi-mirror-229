from typing import Any

from extract_transform.extractor import Extractor


class Compose(Extractor):
    """
    Chains multiple extractors together, passing the output of one extractor as the input to the next.

    Args:
        *extractors (Extractor): A sequence of extractors to be applied in the given order.

    Expected Input:
        Data that is compatible with the first extractor in the sequence.
        E.g., if the first extractor expects a string, then a string should be provided.

    Expected Output:
        The processed data after all extractors in the sequence have been applied.
        The nature of the output depends on the sequence of extractors.
        E.g., if the last extractor returns an integer, the overall output will be an integer.
    """

    def __init__(self, *extractors: Extractor):
        super().__init__()
        self.extractors = extractors

    def extract(self, data: Any) -> Any:
        for extractor in self.extractors:
            data = extractor.extract(data)
        return data
