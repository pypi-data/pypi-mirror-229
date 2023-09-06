import unittest

from extract_transform.data_manipulation.count import Count


class TestCount(unittest.TestCase):
    def test_count_all_items(self):
        data = [1, 2, 3, 4, 5]
        count_extractor = Count()
        result = count_extractor.extract(data)
        self.assertEqual(result, 5)

    def test_count_with_predicate(self):
        data = [1, 2, 3, 4, 5]
        count_extractor = Count(predicate=lambda x: x > 3)
        result = count_extractor.extract(data)
        self.assertEqual(result, 2)

    def test_count_empty_list(self):
        data = []
        count_extractor = Count()
        result = count_extractor.extract(data)
        self.assertEqual(result, 0)
