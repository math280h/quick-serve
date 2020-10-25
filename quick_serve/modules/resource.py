import aiofiles
import chardet

from os import path

from typing import Tuple


def match_mime_type(ext: str) -> str:
    """Tries to match Mime Type to File Extension

    :param ext: File Extension as String
    :return: Mime Type as String
    """
    return {
        '.txt': 'text/plain',
        '.png': 'image/png',
        '.pdf': 'application/pdf',
        '.php': 'application/x-httpd-php',
        '.svg': 'image/svg+xml',
        '.ttf': 'font/ttf',
        '.zip': 'application/zip',
        '.htm': 'text/html',
        '.html': 'text/html',
        '.gif': 'image/gif',
        '.js': 'text/javascript',
        '.json': 'application/json'
    }.get(ext, "text/html")


class Resource:
    """Resource Helper - Helps loading resources e.g. files from either cache or disk

    :param config: Config module instance
    :param log: Log module instance
    :param cache: Cache instance
    """

    def __init__(self, config, log, cache) -> None:
        self.config = config
        self.log = log
        self.cache = cache

    async def check_valid_resource(self, data: list) -> str or bool:
        """Check if data contains a valid resource

        :param data: Request Data
        :return: resource path || False
        """
        try:
            if data[1] == '' or data[1] == '/':  # If requested resource is empty, serve default
                resource = self.config.options.get("Server", "DefaultFile")
            else:  # Set resource to requested resource
                resource = data[1]
            return self.config.options.get("General", "WorkingDirectory") + resource
        except IndexError:  # No resource was specified, invalid request
            return False

    async def detect_encoding(self, raw_data: bytes) -> str:
        """Tries to detect the encoding for a file.

        :param raw_data: Data as Bytes or ByteArray
        :return: Encoding as string
        """
        try:
            return chardet.detect(raw_data)['encoding']
        except Exception as e:
            self.log.critical("Something went wrong with detecting encoding:" + str(e))

    async def get(self, req_resource: str, client=None) -> Tuple[any, int, str, str] or Tuple[bool, None, None, None]:
        """Tries to read the requested resource from either disk or cache

        :param req_resource: Path to requested resource as string
        :param client: Client who tried to access the resource, only used for logging.
        :return: file_contents, content_length || False, None
        """
        if path.isfile(req_resource):
            self.log.debug("{} {} {}".format(client, "Accessed:", req_resource))
            _, file_extension = path.splitext(req_resource)
            cached_resource = self.cache.get(req_resource)  # Try to read the resource from cache
            if cached_resource is None:  # If resource was not in cache
                self.log.debug("{} Loaded from disk".format(req_resource))
                async with aiofiles.open(req_resource, mode='r') as resource:  # Read the resource from the disk
                    data = await resource.read()
                    with self.cache as reference:  # Store the resource in the cache
                        reference.set(req_resource, data)
            else:  # If resource was in the cache
                self.log.debug("{} Loaded from cache".format(req_resource))
                data = cached_resource
            content_length = len(data.encode())  # Get content_length from the content
            return data, content_length, match_mime_type(file_extension), await self.detect_encoding(data.encode())
        else:
            return False, None, None, None
