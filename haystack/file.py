import logging
import os

IMAGE_EXTENSIONS = [
    '.jpg',
    '.jpeg'
]

VIDEO_EXTENSIONS = [
    '.mp4',
    '.mts'
]

DATE_TAKEN_TAG = {
    '.mts': 'H264:DateTimeOriginal',
    '.mp4': 'QuickTime:CreateDate',
    '.jpg': 'EXIF:DateTimeOriginal',
    '.jpeg': 'EXIF:DateTimeOriginal'
}


class File:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file
        self.extension = self.__get_extension(path_to_file)
        self.type = self.extension.upper().replace('.', '')

    def is_image(self):
        return self.extension in IMAGE_EXTENSIONS

    def is_video(self):
        return self.extension in VIDEO_EXTENSIONS

    def filename(self):
        return self.path_to_file

    def ext(self):
        return self.extension

    def media_type(self):
        return self.type

    def date_taken_tag(self):
        return DATE_TAKEN_TAG[self.extension]

    def __get_extension(self, path_to_file):
        _, extension = os.path.splitext(self.path_to_file)
        extension = extension.lower()

        if not ((extension in IMAGE_EXTENSIONS or extension in VIDEO_EXTENSIONS) and
                extension in DATE_TAKEN_TAG):
            logging.error('This file has an unrecognized extension. path_to_file=%s extension=%s',
                          path_to_file, extension)
            raise RuntimeError('This file has an unrecognized extension!')

        return extension
