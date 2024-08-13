import logging
import multiprocessing
import queue
import threading
from io import BytesIO
from typing import Optional

import av
from av import VideoFrame

from core.video_aggregator import VideoDecoder, DecoderCreator


class BlockingIO:
    def __init__(self, data_queue: queue.Queue, stop_event: threading.Event):
        self.buffer = bytearray()

        self.data_queue = data_queue
        self.end_event = stop_event

    def read(self, size):
        logging.info("reading %d bytes", size)
        while len(self.buffer) < size and not (self.end_event.is_set() and self.data_queue.empty()):
            self.buffer.extend(self.data_queue.get())  # Waits for data

        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return bytes(data)


class AVProcessDecoder(VideoDecoder):
    def __init__(self):
        manager = multiprocessing.Manager()

        self.data_queue = manager.Queue()
        self.stop_event = manager.Event()
        self.result_dict = manager.dict()

        self.process: Optional[multiprocessing.Process] = None

    @staticmethod
    def run(data_queue: queue.Queue, stop_event: threading.Event, result: dict):
        io_object = BlockingIO(data_queue, stop_event)

        logging.info("start decoding")
        container = av.open(io_object, 'r', buffer_size=1024)

        first_frame: Optional[VideoFrame] = None
        last_frame: Optional[VideoFrame] = None

        frames = 0
        for frame in container.decode(video=0):
            logging.info(frame)
            frames += 1

            if first_frame is None:
                first_frame = frame
            last_frame = frame

        first_image, last_image = BytesIO(), BytesIO()
        first_frame.to_image().save(first_image, "JPEG")
        last_frame.to_image().save(last_image, "JPEG")

        result["frames"] = frames
        result["first_image"] = first_image.getvalue()
        result["last_image"] = last_image.getvalue()

    def start_decode(self):
        logging.info("Started")
        self.process = multiprocessing.Process(target=self.run,
                                               args=(self.data_queue, self.stop_event, self.result_dict),
                                               name="python_pyav_decoder",
                                               daemon=True)
        self.process.start()
        # print(self.process)

    def add_data(self, data):
        self.data_queue.put(data)
        logging.info("Writing data")

    def stop_decode(self):
        self.stop_event.set()
        self.data_queue.put(b"")

    def get_result(self) -> dict:
        logging.info("Waiting result")
        self.process.join()
        res = self.result_dict
        logging.info("Got res")
        return res


class AVProcessDecoderCreator(DecoderCreator):
    def create(self) -> VideoDecoder:
        return AVProcessDecoder()
