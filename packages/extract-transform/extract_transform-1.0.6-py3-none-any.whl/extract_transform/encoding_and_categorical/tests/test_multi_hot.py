import unittest

from extract_transform.encoding_and_categorical.multi_hot import MultiHot


class TestMultiHot(unittest.TestCase):
    def setUp(self):
        self.extractor = MultiHot(["cat", "dog", "bird"], raise_on_warning=True)

    def test_valid_extraction(self):
        data = ["cat", "bird"]
        result = self.extractor.extract(data)
        self.assertEqual(result, [1, 0, 1])

    def test_no_category_extraction(self):
        data = []
        result = self.extractor.extract(data)
        self.assertEqual(result, [0, 0, 0])

    def test_invalid_category_extraction(self):
        data = ["cat", "elephant"]
        with self.assertRaises(RuntimeError):
            self.extractor.extract(data)
