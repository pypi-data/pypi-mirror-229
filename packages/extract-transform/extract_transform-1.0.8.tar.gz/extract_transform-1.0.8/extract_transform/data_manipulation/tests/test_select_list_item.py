import unittest

from extract_transform.data_manipulation.select_list_item import SelectListItem


class TestSelectListItem(unittest.TestCase):
    def test_extract_position(self):
        extractor = SelectListItem(position=1)
        data = [10, 20, 30]
        result = extractor.extract(data)
        self.assertEqual(result, 20)

    def test_extract_criteria(self):
        extractor = SelectListItem(criteria=lambda x: x > 15)
        data = [10, 20, 30]
        result = extractor.extract(data)
        self.assertEqual(result, 20)

    def test_position_out_of_bounds(self):
        extractor = SelectListItem(position=5)
        data = [10, 20, 30]
        result = extractor.extract(data)
        self.assertIsNone(result)

    def test_criteria_not_met(self):
        extractor = SelectListItem(criteria=lambda x: x > 50)
        data = [10, 20, 30]
        result = extractor.extract(data)
        self.assertIsNone(result)
