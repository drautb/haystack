import logging
import os


class USBDeviceManager:
    def __init__(self):
        return

    def get_devices_to_index(self, mount_dirs, devices_to_ignore):
        logging.info('Checking for USB devices to index. mount_dirs=%s devices_to_ignore=%s',
                     mount_dirs, devices_to_ignore)
        devices = []
        for mount_dir in mount_dirs:
            for device in self.__get_devices(mount_dir):
                if device not in devices_to_ignore:
                    devices.append((os.path.join(mount_dir, device), device))
                else:
                    logging.info('Found device in ignore list, skipping. device=%s', device)

        return devices

    def __get_devices(self, mount_dir):
        devices = []

        if not os.path.isdir(mount_dir):
            logging.info('USB mount directory does not exist, skipping. mount_dir=%s', mount_dir)
            return devices

        contents = os.listdir(mount_dir)
        for obj in contents:
            if os.path.isdir(os.path.join(mount_dir, obj)):
                devices.append(obj)

        return devices
