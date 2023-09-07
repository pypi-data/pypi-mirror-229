import unittest

from extract_transform.data_manipulation.sort_dict_list import SortDictList


class TestSortDictList(unittest.TestCase):
    def test_basic_sort(self):
        extractor = SortDictList(sort_key="age")
        data = [
            {"name": "Alice", "age": 28},
            {"name": "Bob", "age": 22},
            {"name": "Charlie", "age": 24},
        ]
        result = extractor.extract(data)
        expected = [
            {"name": "Bob", "age": 22},
            {"name": "Charlie", "age": 24},
            {"name": "Alice", "age": 28},
        ]
        self.assertEqual(result, expected)

    def test_missing_sort_key(self):
        extractor = SortDictList(sort_key="age")
        data = [
            {"name": "Alice"},
            {"name": "Bob", "age": 22},
            {"name": "Charlie", "age": 24},
        ]
        result = extractor.extract(data)
        expected = [
            {"name": "Alice"},
            {"name": "Bob", "age": 22},
            {"name": "Charlie", "age": 24},
        ]
        self.assertEqual(result, expected)

    def test_invalid_data_type(self):
        extractor = SortDictList(sort_key="age")
        data = {"name": "Alice", "age": 28}
        result = extractor.extract(data)  # type: ignore
        self.assertEqual(result, None)
