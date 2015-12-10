import atexit
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
OVERWRITE_ORIGINAL = '-overwrite_original'


class MetadataHelper:

    # Given a file, this function returns a UNIX timestamp (seconds)
    # in UTC that describes when the picture/video was taken.
    def get_date_taken(self, path_to_file):
        metadata = {}
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(path_to_file)

        f = File(path_to_file)

        tag = f.date_taken_tag()
        self.__check_tag(tag, metadata, path_to_file)

        raw_date_taken_string = metadata[tag]
        massaged_date_taken_string = raw_date_taken_string.replace(COLON, DASH, COLONS_IN_YMD)

        dt_object = parser.parse(massaged_date_taken_string)
        timestamp = mktime(dt_object.timetuple())

        return int(timestamp)

    def get_rotation(self, path_to_file):
        metadata = {}
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(path_to_file)

        f = File(path_to_file)

        tag = f.rotation_tag()
        if tag not in metadata:
            return 0

        return int(metadata[tag])

    def set_rotation(self, path_to_file, new_rotation):
        f = File(path_to_file)
        with exiftool.ExifTool() as et:
            et.execute('-' + f.rotation_tag() + '=' + str(new_rotation),
                       OVERWRITE_ORIGINAL, path_to_file)

    def __check_tag(self, tag, metadata, path_to_file):
        if tag not in metadata:
            logging.error('This file\'s metadata doesn\'t contain the expected tag. path_to_file=%s tag=%s',
                          path_to_file, tag)
            raise RuntimeError('This file does not have the expected metedata tag!')
