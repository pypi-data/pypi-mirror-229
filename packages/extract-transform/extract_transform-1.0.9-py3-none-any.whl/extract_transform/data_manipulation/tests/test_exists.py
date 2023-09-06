import unittest

from extract_transform.data_manipulation.exists import Exists


class TestExists(unittest.TestCase):
    def setUp(self):
        self.key_to_check = "cat"
        self.extractor = Exists(self.key_to_check)

    def test_key_exists(self):
        data = {"cat": "meow", "dog": "bark"}
        result = self.extractor.extract(data)
        self.assertTrue(result)

    def test_key_not_exists(self):
        data = {"dog": "bark", "bird": "tweet"}
        result = self.extractor.extract(data)
        self.assertFalse(result)
