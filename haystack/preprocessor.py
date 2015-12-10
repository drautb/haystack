import logging

from file import File
from metadata_helper import MetadataHelper
from PIL import Image


class Preprocessor:
    def __init__(self, metadata_helper=None):
        if metadata_helper is None:
            metadata_helper = MetadataHelper()

        self.metadata_helper = metadata_helper

    def preprocess(self, path_to_file):
        f = File(path_to_file)
        if not f.is_image():
            logging.info('File is not an image, skipping preprocessing. path_to_file=%s', path_to_file)
            return

        image = Image.open(path_to_file)
        exif_data = image.info['exif']
        rotation = self.metadata_helper.get_rotation(path_to_file)

        logging.info('Preprocessing file. path_to_file=%s rotation=%d', path_to_file, rotation)

        if rotation == 2:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif rotation == 3:
            image = image.transpose(Image.ROTATE_180)
        elif rotation == 4:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif rotation == 5:
            image = image.transpose(Image.ROTATE_90)
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif rotation == 6:
            image = image.transpose(Image.ROTATE_90)
        elif rotation == 7:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
            image = image.transpose(Image.ROTATE_90)
        elif rotation == 8:
            image = image.transpose(Image.ROTATE_270)

        image.save(path_to_file, exif=exif_data)

        logging.info('File has been processed, setting orientation to 1. path_to_file=%s', path_to_file)
        self.metadata_helper.set_rotation(path_to_file, 1)
