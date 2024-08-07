import asyncio

from fastapi import FastAPI, WebSocket

from core import VideoAggregator

video_aggregator = VideoAggregator()

app = FastAPI()


@app.websocket('/')
async def hello(websocket: WebSocket):
    await websocket.accept()
    while True:
        event = await websocket.receive_text()
        uuid = await websocket.receive_text()

        loop = asyncio.get_event_loop()

        if event == "init":
            mime_type = await websocket.receive_text()
            await loop.run_in_executor(None, video_aggregator.start, uuid, mime_type, 1)
        elif event == "frames":
            video_data = await websocket.receive_bytes()
            await loop.run_in_executor(None, video_aggregator.frames, uuid, video_data)
        elif event == "stop":
            loop.run_in_executor(None, video_aggregator.stop, uuid)
        elif event == "total":
            data = await loop.run_in_executor(None, video_aggregator.get_total, uuid)
            await websocket.send_text(str(data["frames"]))
            await websocket.send_text(str(data["segments_received"]))
            await websocket.send_bytes(data["first_image"])
            await websocket.send_bytes(data["last_image"])

            await asyncio.sleep(1)

            break
    await websocket.close()
