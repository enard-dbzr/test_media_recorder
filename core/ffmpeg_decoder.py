
import io

import threading
from queue import Queue
from subprocess import Popen, PIPE
from typing import Optional

from PIL import Image

from core.video_aggregator import VideoDecoder, DecoderCreator


class FmpegDecoder(VideoDecoder):
    def __init__(self):
        self.stopped = threading.Event()
        self.data_queue = Queue()

        self.ffmpeg_command = [
            'ffmpeg',
            '-hwaccel', 'auto',
            '-i', '-',
            '-f', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo',
            '-an', '-sn',
            '-'
        ]

        self.ffprobe_command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height',
            '-of', 'csv=s=x:p=0',
            '-'
        ]

        self._properties_event = threading.Event()
        self.width = None
        self.height = None
        self.frame_size = None

        self._process: Optional[Popen] = None

        self.result = None
        self._render_done_event = threading.Event()

    def _data_writer(self):
        i = 0
        while not self.stopped.is_set() or not self.data_queue.empty():
            data = self.data_queue.get()

            if self.width is None:
                self._set_video_properties(data)

            i += 1
            self._process.stdin.write(data)
            self._process.stdin.flush()
        self._process.stdin.close()

    def _renderer(self):
        self._properties_event.wait()
        frames_count = 0
        first_frame = None
        last_frame = None

        while True:
            frame_data = self._process.stdout.read(self.frame_size)
            if len(frame_data) != self.frame_size:
                break

            frames_count += 1

            if first_frame is None:
                first_frame = frame_data
            last_frame = frame_data

            # cv2.imshow('Frame', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

        # cv2.destroyAllWindows()

        print("rendered", frames_count)


        first_image, last_image = io.BytesIO(), io.BytesIO()
        Image.frombytes("RGB", (self.width, self.height), first_frame).save(first_image, "JPEG")
        Image.frombytes("RGB", (self.width, self.height), last_frame).save(last_image, "JPEG")

        self._process.terminate()
        self.result = {
            "frames": frames_count,
            "first_image": first_image.getvalue(),
            "last_image": last_image.getvalue()
        }
        self._render_done_event.set()

    def _set_video_properties(self, data):
        process = Popen(self.ffprobe_command, stdin=PIPE, stdout=PIPE)
        stdout, stderr = process.communicate(input=data)

        process.terminate()

        self.width, self.height = map(int, stdout.decode().strip().split('x'))
        self.frame_size = self.width * self.height * 3
        self._properties_event.set()

    def start_decode(self):
        self._process = Popen(self.ffmpeg_command, stdin=PIPE, stdout=PIPE, bufsize=10 ** 8)

        threading.Thread(target=self._data_writer).start()
        threading.Thread(target=self._renderer).start()

    def add_data(self, data):
        self.data_queue.put(data)

    def stop_decode(self):
        self.stopped.set()
        self.data_queue.put(b"")

    def get_result(self):
        self._render_done_event.wait()
        return self.result


class FfmpegDecoderCreator(DecoderCreator):

    def create(self) -> VideoDecoder:
        return FmpegDecoder()
