from datetime import datetime, timezone
from typing import Any, Optional

from extract_transform.dates_and_times.datetime import DateTime
from extract_transform.extractor import Extractor


class RelativeDatetime(Extractor):
    """
    Calculates the number of seconds difference between a provided datetime and a reference datetime specified in the context.

    Args:
        date_format (str, optional): The format string to use for parsing the input datetime string. Defaults to "%Y-%m-%dT%H:%M:%S".
        tz (Optional[timezone], optional): Timezone information for the datetime. If provided, the extracted datetime will have this timezone set.

    Expected Input:
        A string representation of a datetime, e.g., "2023-04-30T15:30:00".

    Expected Output:
        A float representing the number of seconds difference between the provided datetime and the context's reference datetime. If the input datetime or context's reference datetime is not provided or invalid, returns None.
    """

    def __init__(
        self,
        date_format: str = "%Y-%m-%dT%H:%M:%S",
        ref_datetime: datetime = datetime.now(),
        tz: Optional[timezone] = None,
    ):
        super().__init__()
        self.datetime_extractor = DateTime(date_format, tz)
        self.ref_datetime = ref_datetime

    def extract(self, data: Any) -> Optional[float]:
        extracted_datetime = self.datetime_extractor.extract(data)

        if extracted_datetime is None or self.ref_datetime is None:
            return None

        # Make sure both datetimes are offset-aware or offset-naive
        if self.ref_datetime.tzinfo is None and extracted_datetime.tzinfo is not None:
            extracted_datetime = extracted_datetime.replace(tzinfo=None)
        elif self.ref_datetime.tzinfo is not None and extracted_datetime.tzinfo is None:
            extracted_datetime = extracted_datetime.replace(tzinfo=timezone.utc)

        delta = self.ref_datetime - extracted_datetime
        return delta.total_seconds()  # Returns the difference in seconds as a float
