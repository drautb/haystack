import os

from ConfigParser import ConfigParser

CONFIG_FILE = 'config.properties'

# Section Keys
TIMING_SECTION = 'Timing'
MTP_SECTION = 'MTP'
USB_SECTION = 'USB'
PATHS_TO_FILES_SECTION = 'PathsToFiles'
INDEX_SECTION = 'Index'

# Config Keys
EXECUTION_INTERVAL = 'ExecutionIntervalInSeconds'
PATHS_TO_INDEX = 'PathsToIndex'
IGNORE = 'Ignore'
MOUNT_POINTS = 'MountPoints'
HAYSTACK_ROOT = 'HaystackRoot'
THUMBNAIL_PATH = 'ThumbnailPath'
PICTURE_PATH = 'PicturePath'
VIDEO_PATH = 'VideoPath'
THUMBNAIL_SIZE = 'ThumbnailSize'
FIREBASE_NAME = 'Firebase'
FIREBASE_SECRET = 'Secret'

STAGING_DIRECTORY = 'staging'
DELIMITER = ','


class Config:
    def __init__(self, config=None):
        if config is None:
            config = ConfigParser()

        self.config = config
        self.refresh_config()

    def refresh_config(self):
        self.config.read(CONFIG_FILE)

    def indexer_delay(self):
        self.refresh_config()
        return int(self.config.get(TIMING_SECTION, EXECUTION_INTERVAL))

    def mtp_media_directories(self):
        self.refresh_config()
        return self.config.get(MTP_SECTION, PATHS_TO_INDEX).split(DELIMITER)

    def mtp_devices_to_ignore(self):
        self.refresh_config()
        return self.config.get(MTP_SECTION, IGNORE).split(DELIMITER)

    def usb_media_directories(self):
        self.refresh_config()
        return self.config.get(USB_SECTION, PATHS_TO_INDEX).split(DELIMITER)

    def usb_mount_points(self):
        self.refresh_config()
        return self.config.get(USB_SECTION, MOUNT_POINTS).split(DELIMITER)

    def usb_devices_to_ignore(self):
        self.refresh_config()
        return self.config.get(USB_SECTION, IGNORE).split(DELIMITER)

    def haystack_root(self):
        self.refresh_config()
        return self.config.get(PATHS_TO_FILES_SECTION, HAYSTACK_ROOT)

    def staging_root(self):
        return os.path.join(self.haystack_root(), STAGING_DIRECTORY)

    def staging_directory(self, device_id):
        return os.path.join(self.staging_root(), device_id)

    def thumbnail_path_pattern(self):
        pattern = self.config.get(PATHS_TO_FILES_SECTION, THUMBNAIL_PATH)
        return os.path.join(self.haystack_root(), pattern)

    def picture_path_pattern(self):
        pattern = self.config.get(PATHS_TO_FILES_SECTION, PICTURE_PATH)
        return os.path.join(self.haystack_root(), pattern)

    def video_path_pattern(self):
        pattern = self.config.get(PATHS_TO_FILES_SECTION, VIDEO_PATH)
        return os.path.join(self.haystack_root(), pattern)

    def thumbnail_size(self):
        self.refresh_config()
        return self.config.get(PATHS_TO_FILES_SECTION, THUMBNAIL_SIZE)

    def firebase_name(self):
        self.refresh_config()
        return self.config.get(INDEX_SECTION, FIREBASE_NAME)

    def firebase_secret(self):
        self.refresh_config()
        return self.config.get(INDEX_SECTION, FIREBASE_SECRET)
