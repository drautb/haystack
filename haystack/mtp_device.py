import logging
import pymtp
import os
import sys

from config import Config
from file import File
from mtp_driver import MTPDriver
from mtp_object import MTPObject
from util import Util


class MTPDevice:
    def __init__(self, config=None, mtp=None, util=None):
        if config is None:
            config = Config()

        if mtp is None:
            mtp = MTPDriver()

        if util is None:
            util = Util()

        self.config = config
        self.mtp = mtp
        self.util = util

    def transfer_media(self):
        device_info = self.mtp.detect_device()
        if not device_info:
            logging.info('No MTP devices connected, skipping MTP media transfer.')
            return

        self.__log_connected_msg(device_info)

        folders = self.mtp.get_folder_list()

        # Get the IDs for the parent folders to index.
        parent_folder_ids = self.__find_parent_folder_ids(folders)

        # Find all folder ids in the parent folders
        folder_ids = self.__find_all_folder_ids(parent_folder_ids, folders)

        # Find all media files in these folders
        media_files = self.__find_files_in_folders(folder_ids)
        if not media_files:
            logging.info('No files found to transfer.')

        # Transfer all files from the folders
        dest_dir = self.__get_staging_dir(device_info['serial'])
        self.util.mkdirp(dest_dir)
        for f in media_files:
            self.__transfer_file(f, dest_dir)

    def __log_connected_msg(self, info):
        msg_str = "Connected to device. serialnumber={} manufacturer={} modelname={}"
        msg = msg_str.format(info['serial'], info['manufacturer'], info['model'])
        logging.info(msg)

    def __find_parent_folder_ids(self, folders):
        ids = []
        folders_to_index = self.config.mtp_media_directories()
        logging.info('Folders to index: %s', folders_to_index)
        for f in folders:
            if f.name in folders_to_index:
                ids.append(f.id)

        return ids

    def __find_all_folder_ids(self, parent_folder_ids, complete_folder_list):
        logging.info('Finding all ids for folders in parent folders: %s', parent_folder_ids)
        folder_ids = set(parent_folder_ids)

        current_length = len(folder_ids)
        new_length = None
        while current_length != new_length:
            current_length = len(folder_ids)

            for f in complete_folder_list:
                if f.parent_id in folder_ids:
                    folder_ids.add(f.id)

            new_length = len(folder_ids)

        return folder_ids

    def __find_files_in_folders(self, folder_ids):
        logging.info('Finding all files in folders: %s', folder_ids)
        files_in_folders = []

        for f in self.mtp.get_filelisting():
            if f.parent_id in folder_ids:
                files_in_folders.append(f)

        return files_in_folders

    def __get_staging_dir(self, serial):
        return self.config.staging_directory(serial)

    def __transfer_file(self, src_file, dest_dir):
        try:
            f = File(src_file.name)
        except RuntimeError:
            logging.warn('Found unrecognized file in folders to index, skipping. filename=%s', src_file.name)
            return

        dest_file = '{}/{}'.format(dest_dir, src_file.name)
        logging.info('Downloading file from device. file_id=%s filename=%s destination=%s',
                     src_file.id, src_file.name, dest_file)
        self.mtp.get_file_to_file(src_file.id, dest_file)

        # Make sure it's successful before deleting.
        if not os.path.isfile(dest_file):
            logging.info('Download failed! dest_file was does not exist. file_id=%s dest_file=%s',
                         src_file.id, dest_file)
        elif os.path.getsize(dest_file) != src_file.size:
            logging.info('Download failed! dest_file size does not match expected.' +
                         ' file_id=%s dest_file=%s dest_file_size=%s src_file_size=%s',
                         src_file.id, dest_file, os.path.getsize(dest_file), src_file.size)
        else:
            logging.info('Download succeeded, deleting file from dest_file=%s', dest_file)
            self.mtp.delete_object(src_file.id)
