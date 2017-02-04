import unittest
from onedrive.timer import *


class TestTimer(unittest.TestCase):
    def test_timer_add_elapsed_time_to_the_response(self):
        @measure_time
        def test(a, b):
            return a + b

        res, time = test(1, 2)
        self.assertEqual(res, 3)
        self.assertIsInstance(time, float)

    def test_binder(self):
        @measure_time
        def inc(a):
            return a + 1

        res, time = bind(
            bind(unit(1), inc),
            inc
        )
        self.assertEqual(res, 3)
        self.assertIsInstance(time, float)
