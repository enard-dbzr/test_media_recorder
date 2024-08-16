import logging
import multiprocessing
import os

from core.ffmpeg_decoder import FfmpegDecoderCreator
from core.pyav_decoder import AVDecoderCreator
from core.pyav_process_decoder import AVProcessDecoderCreator
from core.video_aggregator import VideoAggregator


def create_aggregator():
    decoder_title = os.getenv("DECODER", "FFMPEG")
    pool_size = int(os.getenv("POOL_SIZE", 32))

    if decoder_title == "FFMPEG":
        decoder_creator = FfmpegDecoderCreator()
    elif decoder_title == "AV-TH":
        decoder_creator = AVDecoderCreator()
    else:
        decoder_creator = AVProcessDecoderCreator(pool_size)

    logging.info("Set decoder: %s", decoder_creator)

    return VideoAggregator(decoder_creator)
