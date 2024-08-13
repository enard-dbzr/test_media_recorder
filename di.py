import logging
import os

from core.ffmpeg_decoder import FfmpegDecoderCreator
from core.pyav_decoder import AVDecoderCreator
from core.pyav_process_decoder import AVProcessDecoderCreator
from core.video_aggregator import VideoAggregator


def create_aggregator():
    decoder_title = os.getenv("DECODER", "FFMPEG")
    if decoder_title == "FFMPEG":
        decoder_creator = FfmpegDecoderCreator()
    elif decoder_title == "AV-TH":
        decoder_creator = AVDecoderCreator()
    else:
        decoder_creator = AVProcessDecoderCreator()

    logging.info("Set decoder: %s", decoder_creator)

    return VideoAggregator(decoder_creator)
