import unittest

from extract_transform.basic_types.raw import Raw
from extract_transform.data_manipulation.pivot import Pivot


class TestPivot(unittest.TestCase):
    def test_normal_pivot_operation(self):
        extractor = Pivot("group", Raw())
        data = [
            {"group": "A", "value": "10"},
            {"group": "B", "value": "20"},
            {"group": "A", "value": "30"},
        ]
        result = extractor.extract(data)
        self.assertEqual(
            result, {"A": [{"value": "10"}, {"value": "30"}], "B": [{"value": "20"}]}
        )

    def test_exclude_key_behavior(self):
        extractor = Pivot("group", Raw(), exclude_key=True)
        data = [
            {"group": "A", "value": "10"},
            {"group": "B", "value": "20"},
            {"group": "A", "value": "30"},
        ]
        result = extractor.extract(data)
        self.assertEqual(
            result, {"A": [{"value": "10"}, {"value": "30"}], "B": [{"value": "20"}]}
        )

    def test_single_item_per_key_behavior(self):
        extractor = Pivot("group", Raw(), single_item_per_key=True)
        data = [{"group": "A", "value": "10"}, {"group": "B", "value": "20"}]
        result = extractor.extract(data)
        self.assertEqual(result, {"A": {"value": "10"}, "B": {"value": "20"}})
