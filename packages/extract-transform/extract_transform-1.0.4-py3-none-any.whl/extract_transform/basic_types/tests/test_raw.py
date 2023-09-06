import unittest

from extract_transform.basic_types.raw import Raw


class TestRaw(unittest.TestCase):
    def setUp(self):
        self.raw_extractor = Raw()

    def test_return_same_data(self):
        data = {"key": "value"}
        result = self.raw_extractor.extract(data)
        self.assertEqual(result, data)

        data = [1, 2, 3]
        result = self.raw_extractor.extract(data)
        self.assertEqual(result, data)

        data = "a string"
        result = self.raw_extractor.extract(data)
        self.assertEqual(result, data)
