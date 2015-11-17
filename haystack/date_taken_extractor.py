import exiftool
import logging
import os

from dateutil import parser
from dateutil import tz
from time import mktime

COLON = ':'
DASH = '-'

COLONS_IN_YMD = 2

TAG_FOR_EXTENSION = {
    '.mts': 'H264:DateTimeOriginal',
    '.mp4': 'QuickTime:CreateDate',
    '.jpg': 'EXIF:DateTimeOriginal'
}


class DateTakenExtractor:
    def __init__(self, exif_tool=None):
        if exif_tool is None:
            exif_tool = __get_exif_tool()

        self.exif_tool = exif_tool

    # Given a file, this function returns a UNIX timestamp (seconds)
    # in UTC that describes when the picture/video was taken.
    def get_date_taken(self, path_to_file):
        metadata = self.exif_tool.get_metadata(path_to_file)

        _, raw_extension = os.path.splitext(path_to_file)
        extension = raw_extension.lower()
        self.__check_extension(extension, path_to_file)

        tag = TAG_FOR_EXTENSION[extension]
        self.__check_tag(tag, metadata, path_to_file)

        raw_date_taken_string = metadata[tag]
        massaged_date_taken_string = raw_date_taken_string.replace(COLON, DASH, COLONS_IN_YMD)

        dt_object = parser.parse(massaged_date_taken_string)
        timestamp = mktime(dt_object.timetuple())

        return int(timestamp)

    def __check_extension(self, extension, path_to_file):
        if extension not in TAG_FOR_EXTENSION:
            logging.error('This file has an unrecognized extension. path_to_file=%s extension=%s',
                          path_to_file, extension)
            raise RuntimeError('This file has an unrecognized extension!')

    def __check_tag(self, tag, metadata, path_to_file):
        if tag not in metadata:
            logging.error('This file\'s metadata doesn\'t contain the expected tag. path_to_file=%s tag=%s',
                          path_to_file, tag)
            raise RuntimeError('This file does not have the expected metedata tag!')

    def __get_exif_tool(self):
        et = exiftool.ExifTool()
        et.start
        return et
