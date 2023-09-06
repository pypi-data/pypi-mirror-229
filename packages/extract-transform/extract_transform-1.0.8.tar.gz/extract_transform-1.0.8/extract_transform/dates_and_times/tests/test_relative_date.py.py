import unittest
from datetime import date

from extract_transform.dates_and_times.relative_date import RelativeDate


class TestRelativeDateExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = RelativeDate(ref_date=date(2023, 5, 15))

    def test_relative_date_extraction(self):
        data_date = "2023-05-10"
        expected_days_difference = 5.0  # Because 2023-05-15 minus 2023-05-10
        self.assertEqual(
            self.extractor.extract(data_date),
            expected_days_difference,
        )

    def test_invalid_date_data(self):
        data_invalid = "15-May-2023"
        result = self.extractor.extract(data_invalid)
        self.assertIsNone(result)
