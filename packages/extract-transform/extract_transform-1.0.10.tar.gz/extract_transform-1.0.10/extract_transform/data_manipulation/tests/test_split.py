import unittest

from extract_transform.basic_types.string import String
from extract_transform.data_manipulation.split import Split


class TestSplit(unittest.TestCase):
    def setUp(self):
        self.extractor = Split(sep=",", result_extractor=String())

    def test_split(self):
        data = "apple,banana,grape"
        result = self.extractor.extract(data)
        expected_result = ["apple", "banana", "grape"]
        self.assertEqual(result, expected_result)
