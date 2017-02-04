import onedrivesdk
import asyncio
from .async import force_async
from .helpers import is_dir, children

Item = onedrivesdk.Item
Client = onedrivesdk.OneDriveClient

class Downloader:
    class Job:

        def __init__(self, item: onedrivesdk.Item, to: str):
            self.item = item
            self.to = to

    def __init__(self,
                 client: Client,
                 concurrency: int):
        self.concurrency = concurrency
        self.client = client

        self.queue = asyncio.Queue()
        self.workers = [asyncio.ensure_future(
            self._do_worker(i)) for i in range(concurrency)]

    async def _add(self, job: Job):
        await self.queue.put(job)
        print('queue size {}'.format(self.queue.qsize()))

    async def _do_worker(self, ith: int):
        while True:
            job = await self.queue.get()
            if job is None:
                break
            print('worker {} got a job {}'.format(ith, job.item.name))
            assert isinstance(job, Downloader.Job)
            await self._process(job)
            print('worker {} done, {} jobs self'.format(ith, self.queue.qsize()))

    async def _process(self, job: Job):
        import os.path
        if os.path.exists(job.to):
            item_hash = job.item.file.hashes.sha1_hash
            target_hash = await Downloader._sha1(job.to)

            if item_hash == target_hash:
                print('file {} is the same'.format(job.item.name))
                return
        await self._download(job.item, job.to)

    async def _download(self, item: Item, to):
        print('downloading:', item.name, 'to:', to)
        while True:
            try:
                return await self.client.item(drive='me', id=item.id).download_async(to)
            except Exception as e:
                print('error:', e)
                print('retrying ...')
                asyncio.sleep(1000)

    @staticmethod
    @force_async
    def _sha1(file_path: str):
        import hashlib
        sha1 = hashlib.sha1()
        BUF_SIZE = 1 * 1024 * 1024
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest().upper()

    async def download(self, item: Item, to: str):
        await self._add(Downloader.Job(item, to))

    async def download_dir(self, item: Item, to: str):
        import os
        if not is_dir(item):
            return await self.download(item, os.path.join(to, item.name))

        files = await children(item.id, self.client)
        for file in files:
            path = os.path.join(to, item.name)
            if not os.path.exists(path):
                os.makedirs(path)
            await self.download_dir(file, path)

    async def join(self):
        for _ in self.workers:
            await self.queue.put(None)

        await asyncio.wait(self.workers)
        print('finished!')
