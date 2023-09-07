from datetime import datetime
from typing import Any

from extract_transform.extractor import Extractor


class DatetimeUnix(Extractor):
    """
    Converts a UNIX timestamp (in seconds) into a datetime object.

    Expected Input:
        A numeric representation of a UNIX timestamp in seconds, e.g., 1619856000.

    Expected Output:
        A datetime object representing the provided UNIX timestamp, e.g., datetime(2023, 4, 30, 17, 0).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def extract(self, data: Any) -> datetime:
        try:
            return datetime.utcfromtimestamp(data)
        except Exception as e:
            self.warn(f"Invalid UNIX timestamp: {data}. Error: {e}")
            return datetime.utcfromtimestamp(0)  # Default to UNIX epoch
