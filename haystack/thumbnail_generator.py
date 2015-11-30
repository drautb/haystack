import ffvideo
import logging
import os

from PIL import Image

IMAGE_EXTENSIONS = ['.jpg', '.jpeg']


class ThumbnailGenerator:

    # from ffvideo import VideoStream

    # vs = VideoStream('video.mp4',
    #                  frame_size=(128, None),  # scale to width 128px
    #                  frame_mode='RGB')

    # frame = vs.get_frame_at_sec(0)
    # frame.image().save('thumb.jpg')

    def __init__(self, config=None):
        if config is None:
            config = Config()

        self.config = config

    def generate_thumbnail(self, path_to_file, path_to_thumbnail):
        thumbnail_size = self.config.thumbnail_size()

        _, file_extension = os.path.splitext(path_to_file)

        if file_extension in IMAGE_EXTENSIONS:
            original_image = Image.open(path_to_file)
            thumbnail_image = original_image.thumbnail((thumbnail_size, thumbnail_size), Image.ANTIALIAS)
            thumbnail_image.save(path_to_thumbnail)
        # elif file_extension in VIDEO_EXTENSIONS:
        #     video = ffvideo.VideoStream(path_to_file)
        else:
            raise RuntimeError('Unrecognized file extension!')
