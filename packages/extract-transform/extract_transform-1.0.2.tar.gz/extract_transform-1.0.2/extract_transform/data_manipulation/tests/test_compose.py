import unittest

from extract_transform import String
from extract_transform.basic_types.integer import Integer
from extract_transform.data_manipulation.compose import Compose


class TestCompose(unittest.TestCase):
    def test_compose(self):
        data = "10"
        extractors = [String(), Integer()]

        compose = Compose(*extractors)
        result = compose.extract(data)

        self.assertEqual(result, 10)
