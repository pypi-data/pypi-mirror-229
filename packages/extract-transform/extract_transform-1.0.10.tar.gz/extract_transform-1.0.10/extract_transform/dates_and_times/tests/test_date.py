import unittest
from datetime import date

from extract_transform.dates_and_times.date import Date


class TestDateExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = Date()

    def test_date_extraction(self):
        data_date = "2023-05-15"
        expected_date = date(2023, 5, 15)
        self.assertEqual(self.extractor.extract(data_date), expected_date)

    def test_invalid_date_data(self):
        data_invalid = "2023/05/15"
        with self.assertRaises(ValueError):
            self.extractor.extract(data_invalid)
