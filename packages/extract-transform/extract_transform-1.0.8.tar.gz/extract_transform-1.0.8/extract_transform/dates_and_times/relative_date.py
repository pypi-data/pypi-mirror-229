from datetime import date
from typing import Any, Optional

from extract_transform.dates_and_times.date import Date
from extract_transform.extractor import Extractor


class RelativeDate(Extractor):
    """
    Calculates the number of days difference between a provided date and a reference date specified in the context.

    Args:
        date_format (str, optional): The format string to use for parsing the input date string. Defaults to "%Y-%m-%d".

    Expected Input:
        A string representation of a date, e.g., "2023-04-30".

    Expected Output:
        A float representing the number of days difference between the provided date and the context's reference date. If the input date or context's reference date is not provided or invalid, returns None.
    """

    def __init__(
        self, date_format: str = "%Y-%m-%d", ref_date: date = date.today(), **kwargs
    ):
        super().__init__(**kwargs)
        self.date_extractor = Date(date_format)
        self.ref_date = ref_date

    def extract(self, data: Any) -> Optional[float]:
        try:
            extracted_date = self.date_extractor.extract(data)
            if extracted_date is None or self.ref_date is None:
                return None
            delta = self.ref_date - extracted_date
            return delta.days  # Returns the difference in days as a float
        except ValueError:
            self.warn(f"Invalid date format provided: {data}")
            return None
