import decimal
import unittest

from extract_transform.basic_types.decimal import Decimal


class TestDecimalExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = Decimal(precision=38, scale=2)

    def test_decimal_extraction(self):
        data = "10.12"
        expected_result = decimal.Decimal("10.12")
        result = self.extractor.extract(data)
        self.assertEqual(result, expected_result)

    def test_decimal_precision_and_scale(self):
        extractor = Decimal(precision=5, scale=2)
        data = "123.45"
        expected_result = decimal.Decimal(
            "123.45"
        )  # Note: It truncates and doesn't round off
        result = extractor.extract(data)
        self.assertEqual(result, expected_result)
