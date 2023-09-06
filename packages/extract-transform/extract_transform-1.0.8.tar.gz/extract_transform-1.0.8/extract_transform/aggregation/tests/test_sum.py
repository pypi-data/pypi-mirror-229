import unittest

from extract_transform.aggregation.sum import Sum


class TestSum(unittest.TestCase):
    def setUp(self):
        self.extractor = Sum()

    def test_sum(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = self.extractor.extract(data)
        self.assertEqual(result, 15.0)

    def test_non_list_input(self):
        data = "string"
        result = self.extractor.extract(data)  # type: ignore
        self.assertIsNone(result)

    def test_non_numeric_list(self):
        data = [1, 2, "three"]
        result = self.extractor.extract(data)
        self.assertIsNone(result)

    def test_empty_list(self):
        data = []
        result = self.extractor.extract(data)
        self.assertIsNone(result)
