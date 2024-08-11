import os

from core.ffmpeg_decoder import FfmpegDecoderCreator
from core.pyav_decoder import AVDecoderCreator
from core.video_aggregator import VideoAggregator


def create_aggregator():
    decoder_title = os.getenv("DECODER", "FFMPEG")
    if decoder_title == "FFMPEG":
        decoder_creator = FfmpegDecoderCreator()
    else:
        decoder_creator = AVDecoderCreator()

    print(decoder_creator)

    return VideoAggregator(decoder_creator)
