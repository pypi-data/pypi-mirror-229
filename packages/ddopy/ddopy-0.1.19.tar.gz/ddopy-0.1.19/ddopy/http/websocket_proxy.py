import asyncio
import websockets
import random


class WebsocketProxy:
    def __init__(self, local_port, remote_uri, packet_loss_rate=0.0):
        self.local_port = local_port
        self.remote_uri = remote_uri
        self.packet_loss_rate = packet_loss_rate
        self.emulation_enabled = False

    async def handle_client(self, websocket, path):
        async with websockets.connect(self.remote_uri) as remote_ws:
            while True:
                client_data = await websocket.recv()
                if not client_data:
                    break

                if self.emulation_enabled and random.random() > self.packet_loss_rate:
                    await remote_ws.send(client_data)

                    remote_data = await remote_ws.recv()
                    if not remote_data:
                        break

                    await websocket.send(remote_data)

    def set_packet_loss_rate(self, packet_loss_rate):
        self.packet_loss_rate = packet_loss_rate

    def start(self):
        start_server = websockets.serve(self.handle_client, "0.0.0.0", self.local_port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

