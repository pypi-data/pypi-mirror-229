import unittest

from extract_transform.basic_types.raw import Raw
from extract_transform.data_manipulation.transform import Transform


class TestTransform(unittest.TestCase):
    def test_single_param_transformation(self):
        def multiply_by_two(value):
            return value * 2

        extractor = Transform(multiply_by_two, Raw())
        data = 5
        result = extractor.extract(data)
        self.assertEqual(result, 10)

    def test_transformation_exception(self):
        def faulty_func(value):
            return 1 / 0  # This will raise an exception

        extractor = Transform(faulty_func, Raw())
        data = 5
        result = extractor.extract(data)
        self.assertIsNone(result)

    def test_next_extractor(self):
        def multiply_by_two(value):
            return value * 2

        # Using a custom extractor for demonstration
        class DoubleRaw(Raw):
            def extract(self, data):
                return super().extract(data * 2)

        extractor = Transform(multiply_by_two, DoubleRaw())
        data = 5
        result = extractor.extract(data)
        self.assertEqual(
            result, 20
        )  # First transformation: 5 * 2 = 10. Second transformation: 10 * 2 = 20.

    def test_no_extractor(self):
        def capitalize(value):
            return value.upper()

        extractor = Transform(capitalize)
        data = "apple"
        result = extractor.extract(data)
        self.assertEqual(result, "APPLE")
