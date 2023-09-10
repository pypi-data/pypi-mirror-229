import datetime
import unittest

from libexcs import _utils


class FormatKwargsTestCase(unittest.TestCase):

    def test_empty(self):
        expected = ""

        result = _utils.format_kwargs()

        self.assertEqual(result, expected)

    def test_simple(self):
        expected = "a=42"

        result = _utils.format_kwargs(a=42)

        self.assertEqual(result, expected)

    def test_complex(self):
        dt = datetime.datetime.utcnow()
        expected = f"timestamp={repr(dt)}"

        result = _utils.format_kwargs(timestamp=dt)

        self.assertEqual(result, expected)

    def test_multi(self):
        count = 42
        owner = "somebody"
        dt = datetime.datetime.utcnow()
        expected = f"timestamp={dt!r}, {owner=!r}, {count=!r}"

        result = _utils.format_kwargs(timestamp=dt,
                                      owner=owner,
                                      count=count)

        self.assertEqual(result, expected)
