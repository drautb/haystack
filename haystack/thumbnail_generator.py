import ffvideo
import logging
import os

from config import Config
from file import File
from PIL import Image
from util import Util


class ThumbnailGenerator:
    def __init__(self, config=None, util=None):
        if config is None:
            config = Config()

        if util is None:
            util = Util()

        self.config = config
        self.util = util

    def generate_thumbnail(self, path_to_file, path_to_thumbnail):
        thumbnail_dir = os.path.dirname(path_to_thumbnail)
        if not os.path.isdir(thumbnail_dir):
            self.util.mkdirp(thumbnail_dir)

        thumbnail_size = self.config.thumbnail_size()
        f = File(path_to_file)

        if f.is_image():
            original_image = Image.open(path_to_file)
            original_image.thumbnail((thumbnail_size, thumbnail_size), Image.ANTIALIAS)
            original_image.save(path_to_thumbnail)
        elif f.is_video():
            video_stream = ffvideo.VideoStream(path_to_file, frame_size=(thumbnail_size, None), frame_mode='RGB')
            video_thumbnail = video_stream.get_frame_at_sec(0).image()
            video_thumbnail.save(path_to_thumbnail)
        else:
            raise RuntimeError('Unrecognized file extension!')
