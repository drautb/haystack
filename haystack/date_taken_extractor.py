import exiftool
import logging
import os

from dateutil import parser
from dateutil import tz
from file import File
from time import mktime

COLON = ':'
DASH = '-'

COLONS_IN_YMD = 2


class DateTakenExtractor:
    def __init__(self, exif_tool=None):
        if exif_tool is None:
            exif_tool = __get_exif_tool()

        self.exif_tool = exif_tool

    # Given a file, this function returns a UNIX timestamp (seconds)
    # in UTC that describes when the picture/video was taken.
    def get_date_taken(self, path_to_file):
        metadata = self.exif_tool.get_metadata(path_to_file)
        f = File(path_to_file)

        tag = f.date_taken_tag()
        self.__check_tag(tag, metadata, path_to_file)

        raw_date_taken_string = metadata[tag]
        massaged_date_taken_string = raw_date_taken_string.replace(COLON, DASH, COLONS_IN_YMD)

        dt_object = parser.parse(massaged_date_taken_string)
        timestamp = mktime(dt_object.timetuple())

        return int(timestamp)

    def __check_tag(self, tag, metadata, path_to_file):
        if tag not in metadata:
            logging.error('This file\'s metadata doesn\'t contain the expected tag. path_to_file=%s tag=%s',
                          path_to_file, tag)
            raise RuntimeError('This file does not have the expected metedata tag!')

    def __get_exif_tool(self):
        et = exiftool.ExifTool()
        et.start
        return et
