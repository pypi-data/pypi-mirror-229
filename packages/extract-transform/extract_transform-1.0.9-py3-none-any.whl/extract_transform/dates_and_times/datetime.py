from datetime import datetime, timezone
from typing import Any, Optional

from extract_transform.extractor import Extractor


class DateTime(Extractor):
    """
    Parses a string representation of a date-time into a datetime object. Optionally adjusts for the provided timezone.

    Args:
        date_format (str, optional): The format string to use for parsing the date-time string. Defaults to "%Y-%m-%dT%H:%M:%S".
        tz (timezone, optional): The timezone to which the datetime object should be adjusted. If not provided, the datetime remains naive.

    Expected Input:
        A string representation of a date-time, e.g., "2023-04-30T17:00:00".

    Expected Output:
        A datetime object parsed from the provided string, optionally adjusted for the given timezone. If parsing fails, returns None.
    """

    def __init__(
        self, date_format: str = "%Y-%m-%dT%H:%M:%S", tz: Optional[timezone] = None
    ):
        super().__init__()
        self.date_format = date_format
        self.tz = tz

    def extract(self, data: Any) -> Optional[datetime]:
        try:
            dt = datetime.strptime(data, self.date_format)
            if self.tz:
                dt = dt.replace(tzinfo=self.tz)
            return dt
        except Exception:
            return None
