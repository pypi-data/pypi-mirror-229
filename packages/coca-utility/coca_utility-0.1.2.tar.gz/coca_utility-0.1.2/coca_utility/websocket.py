import websockets, json


class WSConnector:
    def __init__(self, end_point: str, channels=[]):
        self.end_point = end_point
        self.channels = channels

    def onRecieve(self, msg: list | dict):
        raise NotImplementedError

    def onError(self, error: object):
        pass

    async def run(self):
        async for socket in websockets.connect(self.end_point):
            try:
                await self._subscribe(socket)
                async for msg in socket:
                    self.onRecieve(json.loads(msg))
            except websockets.ConnectionClosed as error:
                self.onError(error)
            except websockets.InvalidStatus as error:
                self.onError(error)

    async def _subscribe(self, socket):
        for channel in self.channels:
            await socket.send(json.dumps(channel))
