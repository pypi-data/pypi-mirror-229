from datetime import date, datetime
from typing import Any, Optional

from extract_transform.extractor import Extractor


class Date(Extractor):
    """
    Extracts date values from string representations based on the provided date format.

    Args:
        date_format (str, optional): The format to interpret the date string. Defaults to "%Y-%m-%d".

    Expected Input:
        A string representation of a date that matches the provided date format, e.g., "2023-05-01" for default format.

    Expected Output:
        A date object representing the provided date, e.g., date(2023, 5, 1)."""

    def __init__(self, date_format: str = "%Y-%m-%d"):
        super().__init__()
        self.date_format = date_format

    def extract(self, data: Any) -> Optional[date]:
        if data is None:
            return None
        if not isinstance(data, str):
            raise ValueError(
                f"Invalid data type for Date extractor: {type(data).__name__}"
            )

        dt = datetime.strptime(data, self.date_format)
        return dt.date()
