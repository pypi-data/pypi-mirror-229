import unittest

from extract_transform.encoding_and_categorical.one_hot import OneHot


class TestOneHot(unittest.TestCase):
    def setUp(self):
        self.categories = ["cat", "dog", "bird"]

    def test_onehot_extraction(self):
        extractor = OneHot(self.categories)
        self.assertEqual(extractor.extract("cat"), {"cat": 1, "dog": 0, "bird": 0})
        self.assertEqual(extractor.extract("dog"), {"cat": 0, "dog": 1, "bird": 0})
        self.assertEqual(extractor.extract("bird"), {"cat": 0, "dog": 0, "bird": 1})

    def test_unexpected_category(self):
        extractor = OneHot(self.categories, raise_on_warning=True)
        expected_output = {"cat": 0, "dog": 0, "bird": 0}
        self.assertEqual(extractor.extract("fish"), expected_output)
