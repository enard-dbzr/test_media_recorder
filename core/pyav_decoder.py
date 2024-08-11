import multiprocessing
from io import BytesIO
from typing import Optional

import av
from av import VideoFrame

from core.video_aggregator import VideoDecoder, DecoderCreator


class BlockingIO:
    def __init__(self):
        self.buffer = bytearray()

        self.data_queue = multiprocessing.Queue()
        self.done_event = multiprocessing.Event()

    def read(self, size):
        while len(self.buffer) < size and not (self.done_event.is_set() and self.data_queue.empty()):
            self.buffer.extend(self.data_queue.get())  # Waits for data

        print("read")

        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return bytes(data)

    def write(self, data):
        self.data_queue.put(data)
        print("write")

    def done(self):
        self.done_event.set()
        self.data_queue.put(b"")

    def get_buffer_size(self):
        return len(self.buffer)


class AVDecoder(multiprocessing.Process, VideoDecoder):
    def __init__(self):
        super().__init__(daemon=True)

        self._manager = multiprocessing.Manager()
        self.result = self._manager.dict()

        self.io_object = BlockingIO()

    def run(self):
        container = av.open(self.io_object, 'r', buffer_size=1024)

        first_frame: Optional[VideoFrame] = None
        last_frame: Optional[VideoFrame] = None

        frames = 0
        for frame in container.decode(video=0):
            print(frame)
            frames += 1

            if first_frame is None:
                first_frame = frame
            last_frame = frame

        first_image, last_image = BytesIO(), BytesIO()
        first_frame.to_image().save(first_image, "JPEG")
        last_frame.to_image().save(last_image, "JPEG")

        self.result["frames"] = frames
        self.result["first_image"] = first_image.getvalue()
        self.result["last_image"] = last_image.getvalue()

    def start_decode(self):
        self.start()

    def add_data(self, data):
        self.io_object.write(data)

    def stop_decode(self):
        self.io_object.done()

    def get_result(self) -> dict:
        self.join()
        return self.result


class AVDecoderCreator(DecoderCreator):
    def create(self) -> VideoDecoder:
        return AVDecoder()
