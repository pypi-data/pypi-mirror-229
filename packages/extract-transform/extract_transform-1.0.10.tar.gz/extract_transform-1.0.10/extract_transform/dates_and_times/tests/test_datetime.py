import unittest
from datetime import datetime, timezone

from extract_transform.dates_and_times.datetime import DateTime


class TestDateTimeExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor_default = DateTime()
        self.extractor_with_tz = DateTime(tz=timezone.utc)

    def test_datetime_extraction_default(self):
        data_datetime = "2023-05-15T15:30:00"
        expected_datetime = datetime(2023, 5, 15, 15, 30, 0)
        self.assertEqual(
            self.extractor_default.extract(data_datetime),
            expected_datetime,
        )

    def test_datetime_extraction_with_tz(self):
        data_datetime = "2023-05-15T15:30:00"
        expected_datetime = datetime(2023, 5, 15, 15, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(
            self.extractor_with_tz.extract(data_datetime),
            expected_datetime,
        )

    def test_invalid_datetime_data(self):
        data_invalid = "2023-05-15 15:30:00"
        result = self.extractor_default.extract(data_invalid)
        self.assertIsNone(result)
