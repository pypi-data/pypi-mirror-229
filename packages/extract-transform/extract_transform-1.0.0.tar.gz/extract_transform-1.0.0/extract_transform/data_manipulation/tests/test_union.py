import unittest

from extract_transform.basic_types.raw import Raw
from extract_transform.data_manipulation.union import Union
from extract_transform.extractor import Extractor


class TestUnion(unittest.TestCase):
    def test_successful_condition(self):
        # Using Raw as a trivial extractor for demonstration
        union_extractor = Union(Raw(), Raw())
        data = "test"
        result = union_extractor.extract(data)
        self.assertEqual(result, "test")

    def test_exception_move_to_next_condition(self):
        class FailingExtractor(Extractor):
            def extract(self, data):
                raise ValueError("This extractor always fails")

        union_extractor = Union(FailingExtractor(), Raw())
        data = "test"
        result = union_extractor.extract(data)
        self.assertEqual(result, "test")

    def test_use_default_extractor(self):
        class FailingExtractor(Extractor):
            def extract(self, data):
                raise ValueError("This extractor always fails")

        union_extractor = Union(FailingExtractor(), default=Raw())
        data = "test"
        result = union_extractor.extract(data)
        self.assertEqual(result, "test")

    def test_no_matching_extractor(self):
        class FailingExtractor(Extractor):
            def extract(self, data):
                raise ValueError("This extractor always fails")

        union_extractor = Union(FailingExtractor())

        with self.assertRaises(ValueError):
            union_extractor.extract("test")
