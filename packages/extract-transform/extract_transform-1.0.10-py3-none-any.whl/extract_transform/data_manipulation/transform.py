from typing import Any, Callable, Optional

from extract_transform.extractor import Extractor


class Transform(Extractor):
    """
    Extractor that applies a given transformation function to the data. If an extractor is provided,
    the transformed data is then further processed using this extractor.

    This extractor is particularly useful when you want to preprocess or modify the raw data before
    applying the main extraction logic. If no subsequent extractor is provided, the transformation
    result is directly returned.

    Args:
        func (Callable[..., Any]):
            The transformation function to apply to the data. This function should take one or
            optionally two arguments (data and context). If it requires two arguments, it will be
            provided with both the data and the extraction context.
        extractor (Optional[Extractor]):
            An optional extractor to be used on the transformed data. If not provided, the transformation
            result is directly returned.

    Expected Input:
        Any data type that is compatible with the provided transformation function.

    Expected Output:
        If an extractor is provided: The output would be the result of the `extractor` applied to the transformed data.
        If no extractor is provided: The transformed data is returned directly.

    Example:
        If `func` is a function that capitalizes strings and no `extractor` is provided, given the input
        'apple', the extractor would output 'APPLE'. If an `extractor` that reverses the string is provided,
        the output would be 'ELPPA'.
    """

    def __init__(
        self, func: Callable[..., Any], extractor: Optional[Extractor] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.func = func
        self.extractor = extractor

    def extract(self, data: Any) -> Any:
        try:
            transformed_data = self.func(data)
        except Exception as e:
            self.warn(f"An exception occurred during transformation: {e}")
            transformed_data = None

        if self.extractor:
            return self.extractor.extract(transformed_data)
        else:
            return transformed_data
