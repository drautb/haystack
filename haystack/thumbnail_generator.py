import logging
import os

from config import Config
from executor import Executor
from file import File
from metadata_helper import MetadataHelper
from PIL import Image
from util import Util


class ThumbnailGenerator:
    def __init__(self, config=None, util=None, metadata_helper=None, executor=None):
        if config is None:
            config = Config()

        if util is None:
            util = Util()

        if metadata_helper is None:
            metadata_helper = MetadataHelper()

        if executor is None:
            executor = Executor()

        self.config = config
        self.util = util
        self.metadata_helper = metadata_helper
        self.executor = executor

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
            ffmpeg_cmd = ['ffmpeg', '-i', path_to_file, '-vframes', '1', '-ss', '0', '-vf',
                          'scale=\'if(gte(iw,ih),' + str(thumbnail_size) + ',-1)\':\'if(gte(iw,ih),-1,' +
                          str(thumbnail_size) + ')\'', path_to_thumbnail]
            self.executor.execute(ffmpeg_cmd)
        else:
            raise RuntimeError('Unrecognized file extension!')
