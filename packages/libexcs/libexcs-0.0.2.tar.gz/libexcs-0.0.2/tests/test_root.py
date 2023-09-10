import unittest

from libexcs import root


class DerivedException(root.RootException):
    _template_ = "Having count={count} for owner={owner}"

    count: int
    owner: str
    extra: int


class RootExceptionTestCase(unittest.TestCase):

    def test_empty(self):
        root.RootException()

    def test_extra(self):
        root.RootException(count=42, owner="somebody")

    def test_enough(self):
        DerivedException(count=42, owner="somebody")

    def test_missing(self):
        with self.assertRaises(TypeError):
            DerivedException(count=42, extra=100500)

    def test_attrs(self):
        result = DerivedException(count=42, owner="somebody", extra=100500)

        self.assertTrue(result.count)
        self.assertTrue(result.owner)
        self.assertTrue(result.extra)

    def test_repr(self):
        expected = "DerivedException(count=42, owner='somebody')"

        result = repr(DerivedException(count=42, owner="somebody"))

        self.assertEqual(result, expected)

    def test_str(self):
        expected = "DerivedException: Having count=42 for owner=somebody"

        result = str(DerivedException(count=42, owner="somebody"))

        self.assertEqual(result, expected)
