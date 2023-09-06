import unittest

from extract_transform.basic_types.string import String


class TestString(unittest.TestCase):
    def setUp(self):
        self.string_extractor = String()

    def test_string_conversion(self):
        data = 12345
        result = self.string_extractor.extract(data)
        self.assertEqual(result, "12345")

    def test_string_from_complex_type(self):
        data = [1, 2, 3]
        result = self.string_extractor.extract(data)
        self.assertEqual(result, "[1, 2, 3]")

    def test_string_from_none(self):
        data = None
        result = self.string_extractor.extract(data)
        self.assertEqual(result, "None")
