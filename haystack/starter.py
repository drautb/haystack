import logging
import sys
import time
import sched

from config import Config
from mtp_device import MTPDevice
from usb_device_manager import USBDeviceManager
from usb_device import USBDevice

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    datefmt='%Y/%m/%d %I:%M:%S%p')


class Starter:
    def __init__(self, config=None, scheduler=None, mtp_device=None, usb_device_manager=None, usb_device=None):
        if config is None:
            config = Config()

        if scheduler is None:
            scheduler = sched.scheduler(time.time, time.sleep)

        if mtp_device is None:
            mtp_device = MTPDevice()

        if usb_device_manager is None:
            usb_device_manager = USBDeviceManager()

        if usb_device is None:
            usb_device = USBDevice()

        self.config = config
        self.scheduler = scheduler
        self.mtp_device = mtp_device
        self.usb_device_manager = usb_device_manager
        self.usb_device = usb_device

    # Start function
    def start(self):
        logging.info('Starting indexer.')

        # Transfer Media from all devices.
        # MTP - How does this behave if we connect two devices?
        self.mtp_device.transfer_media()

        # USB
        mounts = self.config.usb_mount_points()
        ignore = self.config.usb_devices_to_ignore()
        devices = self.usb_device_manager.get_devices_to_index(mounts, ignore)
        logging.info('Found USB devices to index. devices=%s', devices)
        for device_path, device_name in devices:
            self.usb_device.transfer_media(device_path, device_name)

        # Index staged media.

        # Schedule the next run of the indexer.
        logging.info('Indexer finished, scheduling next run.')
        self.scheduler.enter(self.config.indexer_delay(), 0, self.start, argument=())
        self.scheduler.run()


if __name__ == '__main__':
    Starter().start()
