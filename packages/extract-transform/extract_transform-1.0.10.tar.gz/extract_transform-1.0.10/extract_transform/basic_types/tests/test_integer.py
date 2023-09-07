import unittest

from extract_transform.basic_types.integer import Integer


class TestInteger(unittest.TestCase):
    def setUp(self):
        self.integer_extractor = Integer()

    def test_validinteger_conversion(self):
        # Test integer data
        data = 42
        result = self.integer_extractor.extract(data)
        self.assertEqual(result, data)

        # Test float data
        data = 42.56
        result = self.integer_extractor.extract(data)
        self.assertEqual(result, 42)  # float should be truncated

        # Test valid string data
        data = "42"
        result = self.integer_extractor.extract(data)
        self.assertEqual(result, 42)

    def test_invalidinteger_conversion(self):
        # Test invalid string data
        data = "invalidinteger"
        with self.assertRaises(ValueError):
            self.integer_extractor.extract(data)
