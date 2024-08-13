import abc
import json
from pathlib import Path


class VideoDecoder(abc.ABC):
    @abc.abstractmethod
    def start_decode(self):
        pass

    @abc.abstractmethod
    def add_data(self, data):
        pass

    @abc.abstractmethod
    def stop_decode(self):
        pass

    @abc.abstractmethod
    def get_result(self) -> dict:
        pass


class DecoderCreator(abc.ABC):
    @abc.abstractmethod
    def create(self) -> VideoDecoder:
        pass


class VideoAggregator:
    def __init__(self, decoder_creator: DecoderCreator):
        self.files = {}
        self.info = {}
        self._renderers = {}

        self._decoder_creator = decoder_creator

        Path("videos").mkdir(parents=True, exist_ok=True)

    def start(self, uuid: str, mime_type, timeslice):
        uuid = str(uuid)
        ext = "webm" if mime_type == "video/webm" else "mp4"
        self.files[uuid] = open(f"videos/{uuid}.{ext}", "wb")
        self.info[uuid] = {"timeslice": int(timeslice), "segments": []}
        self._renderers[uuid] = self._decoder_creator.create()
        self._renderers[uuid].start_decode()

    def stop(self, uuid: str):
        uuid = str(uuid)
        self.files[uuid].close()

        with open(f"videos/{uuid}.seg", "w") as file:
            json.dump(self.info[uuid], file)

        self._renderers[uuid].stop_decode()

    def frames(self, uuid: str, data):
        uuid = str(uuid)
        self.files[uuid].write(data)
        self.info[uuid]["segments"].append(len(data))

        self._renderers[uuid].add_data(data)

    def get_total(self, uuid: str):
        result = self._renderers[uuid].get_result()
        result["segments_received"] = len(self.info[uuid]["segments"])

        del self.files[uuid]
        del self.info[uuid]
        del self._renderers[uuid]

        return result
