import unittest

from extract_transform.basic_types.float import Float


class TestFloat(unittest.TestCase):
    def setUp(self):
        self.float_extractor = Float()

    def test_valid_float_conversion(self):
        # Test float data
        data = 42.56
        result = self.float_extractor.extract(data)
        self.assertEqual(result, data)

        # Test integer data
        data = 42
        result = self.float_extractor.extract(data)
        self.assertEqual(result, 42.0)  # integer should be converted to float

        # Test valid string data
        data = "42.56"
        result = self.float_extractor.extract(data)
        self.assertEqual(result, 42.56)

    def test_invalid_float_conversion(self):
        # Test invalid string data
        data = "invalid_float"
        with self.assertRaises(ValueError):
            self.float_extractor.extract(data)
