import unittest

from extract_transform.data_manipulation.default_value import DefaultValue


class TestDefaultValueExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = DefaultValue(default_value="Default String")

    def test_default_value(self):
        self.assertEqual(self.extractor.extract(None), "Default String")
        self.assertEqual(self.extractor.extract("Test String"), "Test String")
