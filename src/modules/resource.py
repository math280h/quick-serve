import aiofiles
import diskcache

from os import path


class Resource:
    def __init__(self, config, log):
        self.config = config
        self.log = log

    async def get(self, req_resource, client=None):
        if path.isfile(req_resource):
            self.log.debug("{} {} {}".format(client, "Accessed:", req_resource))
            # Read the resource
            async with aiofiles.open(req_resource, mode='r') as resource:
                data = await resource.read()
            content_length = len(data.encode())
            return data, content_length
        else:
            return False, None
