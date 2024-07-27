import asyncio
import websockets
from websockets import WebSocketServerProtocol

from core import VideoAggregator

video_aggregator = VideoAggregator()


async def hello(websocket: WebSocketServerProtocol):
    while True:
        event = await websocket.recv()
        uuid = await websocket.recv()

        if event == "init":
            mime_type = await websocket.recv()
            video_aggregator.start(uuid, mime_type, 1)
        elif event == "frames":
            video_data = await websocket.recv()
            video_aggregator.frames(uuid, video_data)
        elif event == "stop":
            video_aggregator.stop(uuid)
        elif event == "total":
            data = video_aggregator.get_total(uuid)
            await websocket.send(data["image"])
            await websocket.send(str(data["segments_received"]))

            return


async def main():
    async with websockets.serve(hello, "0.0.0.0", 8000):
        await asyncio.Future()  # run forever


if __name__ == "__main__":

    asyncio.run(main())
