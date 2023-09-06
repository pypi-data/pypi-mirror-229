import unittest

from extract_transform.dates_and_times.datetime_unix import DatetimeUnix


class TestDatetimeUnix(unittest.TestCase):
    def setUp(self):
        self.extractor = DatetimeUnix()

    def test_valid_unix_timestamp(self):
        data = 1609459200  # Represents "2021-01-01 00:00:00"
        result = self.extractor.extract(data)
        self.assertEqual(result.year, 2021)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 1)
        self.assertEqual(result.hour, 0)
        self.assertEqual(result.minute, 0)
        self.assertEqual(result.second, 0)

    def test_invalid_unix_timestamp(self):
        extractor = DatetimeUnix(raise_on_warning=True)
        data = "invalid"
        with self.assertRaises(RuntimeError):
            extractor.extract(data)
