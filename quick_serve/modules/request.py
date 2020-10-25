from quick_serve.modules.messenger import Messenger
from quick_serve.modules.resource import Resource


class Request:
    """Connection Handler - This is responsible for handling connections after accept

    :param config: Config Module
    :param log: Log Module
    :param conn: Active Socket Connection
    :param address: Client Object
    :param cache: Cache Module
    """
    def __init__(self, config, log, conn, address, cache) -> None:
        # Define Connection & Client Parameters
        self.conn = conn
        self.address = address

        # Define Modules
        self.log = log
        self.config = config
        self.messenger = Messenger(config, log, conn)
        self.resource = Resource(config, log, cache)

    async def validate_resource(self, data: list) -> bool or any:
        # Check if we received a valid resource
        resource = await self.resource.check_valid_resource(data)
        if resource is False:
            await self.messenger.send_headers("400 Bad Request")
            self.conn.close()
            return False
        return resource

    async def send_options(self) -> None:
        await self.messenger.send_headers("200 OK", allow=True)

    async def send_default(self, resource: any) -> None:
        # Try to gather the resource
        data, content_length, mime_type, encoding = await self.resource.get(resource, self.address[0])
        if data is not False and content_length is not None:
            # If the resource was found and loaded, Send Response
            content_type = mime_type + "; charset=" + str(encoding).lower() + ";"
            await self.messenger.send_data_with_headers("200 OK", data, content_length=content_length,
                                                        content_type=content_type)
            self.log.debug("Sent {} with content_length: {}".format("200 OK", content_length))
        else:
            # If the resource was not found or loaded Send 404 because file doesn't exists
            await self.messenger.send_data_with_headers("404 Not Found", "Sorry, that file does not exist")
            self.log.debug("404 - {} tried to access {}".format(self.address[0], resource))

    async def handle_request(self, method: str, data: list) -> None:
        resource = await self.validate_resource(data)
        if resource is not False:
            if method == 'OPTIONS':
                await self.send_options()
            else:
                await self.send_default(resource)
