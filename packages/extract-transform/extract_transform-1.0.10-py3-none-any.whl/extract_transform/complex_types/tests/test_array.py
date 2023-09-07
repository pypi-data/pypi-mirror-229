import unittest

from extract_transform.basic_types.integer import Integer
from extract_transform.complex_types.array import Array


class TestArray(unittest.TestCase):
    def setUp(self):
        self.array_extractor = Array(Integer())

    def test_normal_list(self):
        data = [1, 2, 3]
        result = self.array_extractor.extract(data)
        self.assertEqual(result, [1, 2, 3])

    def test_none_data(self):
        data = None
        result = self.array_extractor.extract(data)
        self.assertEqual(result, [])

    def test_single_item(self):
        data = 5
        result = self.array_extractor.extract(data)
        self.assertEqual(result, [5])
