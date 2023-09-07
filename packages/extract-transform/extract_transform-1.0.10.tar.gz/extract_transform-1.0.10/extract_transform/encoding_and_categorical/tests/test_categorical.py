import unittest

from extract_transform.encoding_and_categorical.categorical import Categorical


class TestCategorical(unittest.TestCase):
    def setUp(self):
        self.valid_categories = {"apple", "banana", "cherry"}

    def test_valid_category_extraction(self):
        extractor = Categorical(self.valid_categories)
        extracted = extractor.extract("apple")
        self.assertEqual(extracted, "apple")

    def test_invalid_category_extraction(self):
        extractor = Categorical(self.valid_categories, raise_on_warning=True)
        with self.assertRaises(RuntimeError):
            extractor.extract("pineapple")
