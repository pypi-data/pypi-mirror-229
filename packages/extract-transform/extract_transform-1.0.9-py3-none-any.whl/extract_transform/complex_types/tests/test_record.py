import unittest

from extract_transform.basic_types.integer import Integer
from extract_transform.basic_types.string import String
from extract_transform.complex_types.record import Record


class TestRecordExtractor(unittest.TestCase):
    def setUp(self):
        self.record_extractor = Record({"age": Integer(), "name": String()})

    def test_extract(self):
        data = {"age": 30, "name": "John"}
        result = self.record_extractor.extract(data)
        self.assertEqual(result, {"age": 30, "name": "John"})

    def test_extract_with_missing_fields(self):
        data = {"age": 30}
        result = self.record_extractor.extract(data)
        self.assertEqual(result, {"age": 30, "name": None})

    def test_extract_with_extra_fields(self):
        data = {"age": 30, "name": "John", "extra": "field"}
        result = self.record_extractor.extract(data)
        self.assertEqual(result, {"age": 30, "name": "John"})

    def test_extract_with_none(self):
        data = None
        result = self.record_extractor.extract(data)  # type: ignore
        self.assertEqual(result, None)
