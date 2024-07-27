import base64
import io
import json
from pathlib import Path

import av
from av.video.stream import VideoStream


class VideoAggregator:
    def __init__(self):
        self.files = {}
        self.info = {}

        Path("videos").mkdir(parents=True, exist_ok=True)

    def start(self, uuid: str, mime_type, timeslice):
        uuid = str(uuid)
        ext = "webm" if mime_type == "video/webm" else "mp4"
        self.files[uuid] = open(f"videos/{uuid}.{ext}", "wb")
        self.info[uuid] = {"timeslice": int(timeslice), "segments": []}

    def stop(self, uuid: str):
        uuid = str(uuid)
        self.files[uuid].close()

        with open(f"videos/{uuid}.seg", "w") as file:
            json.dump(self.info[uuid], file)

    def frames(self, uuid: str, data):
        uuid = str(uuid)
        self.files[uuid].write(data)
        self.info[uuid]["segments"].append(len(data))

    def get_total(self, uuid: str):
        uuid = str(uuid)
        with av.open(self.files[uuid].name) as container:
            stream: VideoStream = container.streams.video[0]
            stream.codec_context.skip_frame = "NONKEY"

            # for frame in container.decode(stream):
            #     print(frame)

            frame = next(container.decode(stream))

        image = io.BytesIO()
        frame.to_image().save(image, format="PNG")

        image.seek(0)

        res = {
            "image": image.read(),
            "segments_received": len(self.info[uuid]["segments"]),
        }
        return res
