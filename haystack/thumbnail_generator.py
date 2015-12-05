import ffvideo
import logging
import os

from config import Config
from file import File
from PIL import Image
from util import Util


class ThumbnailGenerator:

    # from ffvideo import VideoStream

    # vs = VideoStream('video.mp4',
    #                  frame_size=(128, None),  # scale to width 128px
    #                  frame_mode='RGB')

    # frame = vs.get_frame_at_sec(0)
    # frame.image().save('thumb.jpg')

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
        # elif file_extension in VIDEO_EXTENSIONS:
        #     video = ffvideo.VideoStream(path_to_file)
        else:
            raise RuntimeError('Unrecognized file extension!')
