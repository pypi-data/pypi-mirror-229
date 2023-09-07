import unittest

from extract_transform.basic_types.integer import Integer
from extract_transform.basic_types.string import String
from extract_transform.complex_types.record import Record
from extract_transform.data_manipulation.flatten import Flatten


class TestFlattenExtractor(unittest.TestCase):
    def setUp(self):
        record_extractor = Record({"age": Integer(), "name": String()})
        self.flatten_extractor = Flatten(record_extractor)

    def test_extract(self):
        data = {"age": 30, "name": "John"}
        result = self.flatten_extractor.extract(data)
        self.assertEqual(result, {"age": 30, "name": "John"})

    def test_extract_with_nested_record(self):
        nested_record_extractor = Record({"first": Record({"second": Integer()})})
        flatten_extractor = Flatten(nested_record_extractor)

        data = {"first": {"second": 10}}
        result = flatten_extractor.extract(data)
        expected_result = {"first.second": 10}
        self.assertEqual(result, expected_result)
