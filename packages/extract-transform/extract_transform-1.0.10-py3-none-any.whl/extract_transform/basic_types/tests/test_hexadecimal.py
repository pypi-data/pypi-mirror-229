import unittest

from extract_transform.basic_types.hexadecimal import Hexadecimal


class TestHexadecimal(unittest.TestCase):
    def setUp(self):
        self.extractor = Hexadecimal()

    def test_valid_hexadecimal(self):
        data = "1a"
        result = self.extractor.extract(data)
        self.assertEqual(result, 26)

    def test_invalid_hexadecimal(self):
        extractor = Hexadecimal(raise_on_warning=True)
        data = "1g"
        with self.assertRaises(RuntimeError):
            extractor.extract(data)
