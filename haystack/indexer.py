import hashlib
import logging
import os
import re
import shutil

from config import Config
from date_taken_extractor import DateTakenExtractor
from datetime import datetime
from file import File
from index import Index
from PIL import Image
from thumbnail_generator import ThumbnailGenerator
from time import strptime
from util import Util

BLOCK_SIZE_1M = 1048576  # 1024 Bytes * 1024 Bytes = 1M
READ_ONLY_RAW = 'rb'

PATTERN_REPLACE_YEAR = '%Y'
PATTERN_REPLACE_MONTH = '%M'
PATTERN_REPLACE_DAY = '%D'


class Indexer:
    def __init__(self, config=None, index=None, date_taken_extractor=None, thumbnail_generator=None, util=None):
        if config is None:
            config = Config()

        if index is None:
            index = Index()

        if date_taken_extractor is None:
            date_taken_extractor = DateTakenExtractor()

        if thumbnail_generator is None:
            thumbnail_generator = ThumbnailGenerator()

        if util is None:
            util = Util()

        self.config = config
        self.index = index
        self.date_taken_extractor = date_taken_extractor
        self.thumbnail_generator = thumbnail_generator
        self.util = util

    def run(self):
        logging.info('Indexer started.')

        # Locate the staging directory.
        staging_root = self.config.staging_root()
        logging.info('Located staging directory. staging_root=%s', staging_root)

        # Make sure that the staging directory exists
        if not os.path.isdir(staging_root):
            self.util.mkdirp(staging_root)

        for staging_dir in self.__device_staging_dirs(staging_root):
            self.__index_files(staging_dir)

    def __device_staging_dirs(self, staging_root):
        device_staging_dirs = []

        # For each device folder in the directory
        for f in os.listdir(staging_root):
            path_to_device_dir = self.config.staging_directory(f)
            if not os.path.isdir(path_to_device_dir):
                logging.info('Found non-directory file in staging root, skipping. staging_root=%s file=%s',
                             staging_root, path_to_device_dir)
            else:
                device_staging_dirs.append(f)

        return device_staging_dirs

    def __index_files(self, device_dir):
        staging_dir = self.config.staging_directory(device_dir)
        for filename in os.listdir(staging_dir):
            if os.path.isdir(filename):
                logging.error('found unexpected subdirectory in device staging directory, ignoring. ' +
                              'dir=%s staging_dir=%s', f, staging_dir)
                continue

            path_to_file = os.path.join(staging_dir, filename)
            if File(path_to_file).is_image():
                self.__index_file(device_dir, path_to_file)
            else:
                logging.info('File is not an image, not indexing. file=%s staging_dir=%s', path_to_file, staging_dir)

    def __index_file(self, device, path_to_file):
        logging.info('Indexing file=%s', path_to_file)
        file_hash = self.__get_media_hash(path_to_file)

        if self.index.is_duplicate(file_hash):
            logging.info('File hash already appears in index, file appears to be a duplicate, and will be deleted. ' +
                         'path_to_file=%s file_hash=%s', path_to_file, file_hash)
            os.remove(path_to_file)
            return

        try:
            f = File(path_to_file)

            # Get the date the media was taken.
            date_taken = self.date_taken_extractor.get_date_taken(path_to_file)

            # Generate Thumbnail.
            path_to_thumbnail = self.__generate_path_to_thumbnail(f, date_taken, file_hash)
            self.thumbnail_generator.generate_thumbnail(path_to_file, path_to_thumbnail)

            # Copy file to final place.
            path_to_final_file = self.__generate_path_to_final_file(f, date_taken, file_hash)
            logging.info('Copying staged media to final location. path_to_staged_file=%s path_to_final_file=%s',
                         path_to_file, path_to_final_file)
            shutil.copy(path_to_file, path_to_final_file)

            # Send data to index.
            self.index.index_media(path_to_final_file, path_to_thumbnail, date_taken, device, file_hash, f.media_type())

            # Remove file after successful indexing.
            logging.info('Removing file=%s', path_to_file)
            os.remove(path_to_file)
        except Exception as e:
            logging.exception('Encountered error while trying to index file, leaving file in staging area. ' +
                              'path_to_file=%s', path_to_file)

    def __get_media_hash(self, path_to_file):
        md5 = hashlib.md5()
        with open(path_to_file, READ_ONLY_RAW) as f:
            for chunk in iter(lambda: f.read(BLOCK_SIZE_1M), b''):
                md5.update(chunk)

        return md5.hexdigest()

    def __generate_path_to_thumbnail(self, f, date_taken, hash):
        path_to_thumbnail_pattern = self.config.thumbnail_path_pattern()
        return self.__generate_path_to_file(path_to_thumbnail_pattern, f, date_taken, hash)

    def __generate_path_to_final_file(self, f, date_taken, hash):
        path_to_final_file_pattern = self.config.picture_path_pattern()
        return self.__generate_path_to_file(path_to_final_file_pattern, f, date_taken, hash)

    def __generate_path_to_file(self, pattern, f, date_in_seconds, file_hash):
        date = datetime.fromtimestamp(date_in_seconds)
        pattern = pattern.replace(PATTERN_REPLACE_YEAR, str(date.year))
        pattern = pattern.replace(PATTERN_REPLACE_MONTH, str(date.month))
        pattern = pattern.replace(PATTERN_REPLACE_DAY, str(date.day))
        return os.path.join(pattern, file_hash + f.ext())
