import unittest

from extract_transform.basic_types.raw import Raw
from extract_transform.data_manipulation.when import When


class TestWhen(unittest.TestCase):
    def test_condition_true(self):
        def true_condition(data):
            return True

        when_extractor = When(true_condition, Raw())
        data = "condition_true"
        result = when_extractor.extract(data)
        self.assertEqual(result, "condition_true")

    def test_condition_false(self):
        def false_condition(data):
            return False

        when_extractor = When(false_condition, Raw())
        data = "condition_false"
        result = when_extractor.extract(data)
        self.assertIsNone(result)
