import asyncio

class TCPClient(object):

    class Client(asyncio.Protocol):
        def __init__(self, on_connection_lost_future, msg):
            self.transport = None
            self.on_connection_lost_future = on_connection_lost_future
            self.msg = msg

        def connection_made(self, transport):
            print("Connection made")
            self.transport = transport
            self.send_message()

        def connection_lost(self, exc):
            print("Connection lost")
            self.on_connection_lost_future.set_result(True)

        def data_received(self, data):
            print("Data received {!r}".format())
            print(data.decode("utf-8"))

        def send_message(self):
            self.transport.write(self.msg.encode("utf-8"))
    
    def __init__(self):
        self.server_host = "127.0.0.1"
        self.server_port = 8888

    async def __send_msg(self, msg):
        loop = asyncio.get_running_loop()
        on_connection_lost = loop.create_future()

        (transport, protocol) = await loop.create_connection(lambda : self.Client(on_connection_lost, msg), self.server_host, self.server_port)

        try:
            await protocol.on_connection_lost_future
        finally:
            transport.close()


    def send_msg(self, msg):
        asyncio.run(self.__send_msg(msg))

if __name__ == "__main__":
    tcp = TCPClient()
    tcp.send_msg("Hola")


