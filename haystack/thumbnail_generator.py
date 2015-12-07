import ffvideo
import logging
import os

from config import Config
from file import File
from metadata_extractor import MetadataExtractor
from PIL import Image
from util import Util


class ThumbnailGenerator:
    def __init__(self, config=None, util=None, metadata_extractor=None):
        if config is None:
            config = Config()

        if util is None:
            util = Util()

        if metadata_extractor is None:
            metadata_extractor = MetadataExtractor()

        self.config = config
        self.util = util
        self.metadata_extractor = metadata_extractor

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

            rotation = self.metadata_extractor.get_rotation(path_to_file)
            if rotation == 90:
                video_thumbnail.transpose(Image.ROTATE_270)
            elif rotation == 180:
                video_thumbnail.transpose(Image.ROTATE_180)
            elif rotation == 270:
                video_thumbnail.transpose(Image.ROTATE_90)
            elif rotation != 0:
                logging.error('Invalid rotation value detected! path_to_file=%s rotation=%d', path_to_file, rotation)
                raise RuntimeError('Invalid rotation!')

            video_thumbnail.save(path_to_thumbnail)
        else:
            raise RuntimeError('Unrecognized file extension!')
