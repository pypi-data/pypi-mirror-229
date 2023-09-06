import unittest

from extract_transform.basic_types.boolean import Boolean


class TestBooleanExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = Boolean()

    def test_boolean_extraction(self):
        data_true = "true"
        data_false = "false"
        self.assertTrue(self.extractor.extract(data_true))
        self.assertFalse(self.extractor.extract(data_false))

    def test_custom_truthy_falsy_values(self):
        custom_extractor = Boolean(truthy_values=["yes"], falsy_values=["no"])
        data_yes = "yes"
        data_no = "no"
        self.assertTrue(custom_extractor.extract(data_yes))
        self.assertFalse(custom_extractor.extract(data_no))
