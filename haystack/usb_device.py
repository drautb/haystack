import logging
import os
import shutil

from config import Config
from file import File
from util import Util

USB_DEVICE_ID = 'USB'


class USBDevice:
    def __init__(self, config=None, util=None):
        if config is None:
            config = Config()

        if util is None:
            util = Util()

        self.config = config
        self.util = util

    def transfer_media(self, device_path, device_id):
        paths_to_index = self.config.usb_media_directories()
        dest_dir = self.config.staging_directory(USB_DEVICE_ID)
        logging.info('Transferring media from USB device. device_id=%s dest_dir=%s device_path=%s paths_to_index=%s',
                     device_id, dest_dir, device_path, paths_to_index)
        for p in paths_to_index:
            media_path = os.path.join(device_path, p)
            if os.path.isdir(media_path):
                self.__transfer_media_from_directory(media_path, dest_dir)
            else:
                logging.info('Media path could not be found on device. device=%s media_path=%s', device_id, media_path)

    def __transfer_media_from_directory(self, media_path, dest_dir):
        self.util.mkdirp(dest_dir)
        for root, dirs, files in os.walk(media_path):
            for name in files:
                self.__transfer_file(root, name, dest_dir)
        return

    def __transfer_file(self, path, filename, dest_dir):
        try:
            File(filename)
        except RuntimeError:
            logging.warn('Found unrecognized file in folders to index, skipping. path=%s filename=%s', path, filename)
            return

        # We gen a random hash for the dest file name to avoid conflicts since
        # we're flattening the directory structure.
        dest_filename = '{}{}'.format(self.util.get_uuid(),
                                      File(filename).ext())
        dest_file = os.path.join(dest_dir, dest_filename)
        src_file = os.path.join(path, filename)
        logging.info('Transferring file from USB device. src_file=%s dest_file=%s', src_file, dest_file)
        shutil.move(src_file, dest_file)
