import unittest

from extract_transform.basic_types.float import Float
from extract_transform.basic_types.integer import Integer
from extract_transform.complex_types.numeric_with_codes import NumericWithCodes


class TestNumericWithCodes(unittest.TestCase):
    def testinteger_extractor_in_range(self):
        extractor = NumericWithCodes(Integer(), 0, 100)
        data = 50
        result = extractor.extract(data)
        self.assertEqual(result, {"value": 50, "categorical": None})

    def testinteger_extractor_out_of_range(self):
        extractor = NumericWithCodes(Integer(), 0, 100)
        data = 150
        result = extractor.extract(data)
        self.assertEqual(result, {"value": None, "categorical": "150"})

    def test_float_extractor_in_range(self):
        extractor = NumericWithCodes(Float(), 0.0, 100.0)
        data = 50.5
        result = extractor.extract(data)
        self.assertEqual(result, {"value": 50.5, "categorical": None})

    def test_float_extractor_out_of_range(self):
        extractor = NumericWithCodes(Float(), 0.0, 100.0)
        data = 150.5
        result = extractor.extract(data)
        self.assertEqual(result, {"value": None, "categorical": "150.5"})
