import unittest
from datetime import datetime, timezone

from extract_transform.dates_and_times.relative_datetime import RelativeDatetime


class TestRelativeDatetime(unittest.TestCase):
    def setUp(self):
        self.extractor = RelativeDatetime(
            ref_datetime=datetime(2023, 5, 15, 10, 30, tzinfo=timezone.utc)
        )

    def test_relative_seconds(self):
        data = "2023-05-15T08:30:00"  # 2 hours or 7200 seconds behind reference
        result = self.extractor.extract(data)
        self.assertEqual(result, 7200)

    def test_invalid_datetime_data(self):
        data_invalid = "15-May-2023 10:30:00"
        result = self.extractor.extract(data_invalid)
        self.assertIsNone(result)

    def test_same_datetime(self):
        data = "2023-05-15T10:30:00"  # Same as reference datetime
        result = self.extractor.extract(data)
        self.assertEqual(result, 0)

    def test_datetime_without_tz(self):
        data = "2023-05-15T10:30:00"
        ref_datetime_no_tz = datetime(2023, 5, 15, 10, 30)
        extractor = RelativeDatetime(ref_datetime=ref_datetime_no_tz)
        result = extractor.extract(data)
        self.assertEqual(result, 0)
