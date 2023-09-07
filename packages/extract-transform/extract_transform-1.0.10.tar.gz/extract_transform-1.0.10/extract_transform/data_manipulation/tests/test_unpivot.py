import unittest

from extract_transform.basic_types.string import String
from extract_transform.data_manipulation.unpivot import Unpivot


class TestUnpivot(unittest.TestCase):
    def setUp(self):
        self.extractor = Unpivot(key="category", result_extractor=String())

    def test_unpivot(self):
        data = {"Fruits": ["Apple", "Banana"], "Vegetables": ["Carrot", "Broccoli"]}
        result = self.extractor.extract(data)
        expected_result = [
            {"category": "Fruits", "value": "Apple"},
            {"category": "Fruits", "value": "Banana"},
            {"category": "Vegetables", "value": "Carrot"},
            {"category": "Vegetables", "value": "Broccoli"},
        ]
        self.assertEqual(result, expected_result)
