import unittest

from extract_transform.basic_types.integer import Integer
from extract_transform.data_manipulation.dictmap import DictMap


class TestDictMap(unittest.TestCase):
    def test_normal_dict_extraction(self):
        extractor = DictMap(Integer())
        data = {"a": "10", "b": "20", "c": "30"}
        result = extractor.extract(data)
        self.assertEqual(result, {"a": 10, "b": 20, "c": 30})

    def test_empty_dict(self):
        extractor = DictMap(Integer())
        data = {}
        result = extractor.extract(data)
        self.assertEqual(result, {})

    def test_non_dict_data(self):
        extractor = DictMap(Integer())
        data = ["10", "20", "30"]
        result = extractor.extract(data)  # type: ignore
        self.assertIsNone(result)
