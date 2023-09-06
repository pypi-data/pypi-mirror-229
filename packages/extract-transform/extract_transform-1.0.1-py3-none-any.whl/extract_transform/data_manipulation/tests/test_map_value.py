import unittest

from extract_transform.data_manipulation.map_value import MapValue


class TestMappingExtractor(unittest.TestCase):
    def setUp(self):
        self.mapping = {1: "TypeA", 2: "TypeB", 3: "TypeC"}
        self.extractor = MapValue(self.mapping, default="UnknownType")

    def test_known_mapping(self):
        data = 1
        result = self.extractor.extract(data)
        expected_result = "TypeA"
        self.assertEqual(result, expected_result)

    def test_unknown_mapping(self):
        data = 5
        result = self.extractor.extract(data)
        expected_result = "UnknownType"
        self.assertEqual(result, expected_result)
