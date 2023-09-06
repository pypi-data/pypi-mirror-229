import unittest

from extract_transform.encoding_and_categorical.ordinal import Ordinal


class TestOrdinal(unittest.TestCase):
    def test_ordinal_extraction_with_list(self):
        extractor = Ordinal(["low", "medium", "high"])
        self.assertEqual(extractor.extract("low"), 0)
        self.assertEqual(extractor.extract("medium"), 1)
        self.assertEqual(extractor.extract("high"), 2)

    def test_ordinal_extraction_with_dict(self):
        extractor = Ordinal({"low": 0, "medium": 5, "high": 10})
        self.assertEqual(extractor.extract("low"), 0)
        self.assertEqual(extractor.extract("medium"), 5)
        self.assertEqual(extractor.extract("high"), 10)

    def test_unexpected_ordinal_value(self):
        extractor = Ordinal(["low", "medium", "high"], raise_on_warning=True)
        with self.assertRaises(RuntimeError):
            extractor.extract("ultra-high")
