import unittest

from extract_transform.basic_types.integer import Integer
from extract_transform.data_manipulation.select import Select


class TestSelect(unittest.TestCase):
    def test_extract_key(self):
        extractor = Select(key="age")
        data = {"name": "John", "age": 25}
        result = extractor.extract(data)
        self.assertEqual(result, 25)

    def test_default_extractor(self):
        extractor = Select(key="age")
        data = {"name": "John", "age": "25 years"}
        result = extractor.extract(data)
        self.assertEqual(result, "25 years")

    def test_specified_extractor(self):
        extractor = Select(key="age", extractor=Integer())
        data = {"name": "John", "age": "25"}
        result = extractor.extract(data)
        self.assertEqual(result, 25)

    def test_missing_key(self):
        extractor = Select(key="salary")
        data = {"name": "John", "age": 25}
        result = extractor.extract(data)
        self.assertIsNone(result)
