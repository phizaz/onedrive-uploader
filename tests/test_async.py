import unittest
from onedrive.timer import measure_time
from onedrive.async import *


class AsyncCanTurnAsyncIntoSyncFunction(unittest.TestCase):
    def test_turn_async_to_sync(self):
        @force_sync
        async def test():
            import asyncio
            await asyncio.sleep(0.1)
            return 1 + 2

        self.assertEqual(test(), 3)

    def test_turn_sync_to_sync(self):
        @force_sync
        def test():
            return 1 + 2

        self.assertEqual(test(), 3)


class AsyncCanTurnSyncIntoAsyncFunction(unittest.TestCase):
    def test_turn_sync_to_async(self):
        @force_async
        def test():
            import time
            time.sleep(0.1)
            return True

        @measure_time
        @force_sync
        async def main():
            import asyncio
            futures = list(map(lambda x: test(),
                               range(10)))
            return await asyncio.gather(*futures)

        res, time = main()
        self.assertEqual(len(res), 10)
        self.assertLess(time, 0.2)
