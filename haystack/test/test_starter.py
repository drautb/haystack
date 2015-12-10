import config
import logging
import mtp_device
import sched
import unittest
import usb_device
import usb_device_manager
import indexer

from mock import ANY
from mock import call
from mock import MagicMock
from starter import Starter

logging.disable(logging.CRITICAL)


class TestStarter(unittest.TestCase):

    def setUp(self):
        self.mock_config = MagicMock(config.Config)
        self.mock_config.indexer_delay.return_value = 999
        self.mock_config.usb_mount_points.return_value = ['/media']
        self.mock_config.usb_devices_to_ignore.return_value = ['ignore-me']

        self.mock_scheduler = MagicMock(spec=sched.scheduler)
        self.mock_mtp_device = MagicMock(spec=mtp_device.MTPDevice)

        self.mock_usb_device_manager = MagicMock(spec=usb_device_manager.USBDeviceManager)
        self.mock_usb_device_manager.get_devices_to_index.return_value = [('/media/dev1', 'dev1'),
                                                                          ('/media/dev2', 'dev2')]

        self.mock_usb_device = MagicMock(spec=usb_device.USBDevice)

        self.mock_indexer = MagicMock(spec=indexer.Indexer)

        self.test_model = Starter(self.mock_config, self.mock_scheduler, self.mock_mtp_device,
                                  self.mock_usb_device_manager, self.mock_usb_device, self.mock_indexer)

    def test_it_should_transfer_media_from_an_mtp_device(self):
        self.test_model.start()
        self.mock_mtp_device.transfer_media.assert_called_once_with()

    def test_it_should_use_the_right_mount_points_for_usb_devices(self):
        self.test_model.start()
        self.mock_usb_device_manager.get_devices_to_index.assert_called_once_with(['/media'], ANY)

    def test_it_should_use_the_right_ignore_list_for_usb_devices(self):
        self.test_model.start()
        self.mock_usb_device_manager.get_devices_to_index.assert_called_once_with(ANY, ['ignore-me'])

    def test_it_should_transfer_media_from_usb_devices(self):
        self.test_model.start()
        calls = [call('/media/dev1', 'dev1'), call('/media/dev2', 'dev2')]
        self.mock_usb_device.transfer_media.assert_has_calls(calls)

    def test_it_should_start_the_indexer(self):
        self.test_model.start()
        self.mock_indexer.run.assert_called_once_with()

    def test_it_should_catch_errors_in_the_indexer(self):
        self.mock_indexer.run.side_effect = RuntimeError
        self.test_model.start()

    def test_it_should_use_the_config_value_to_schedule_jobs(self):
        self.test_model.start()
        self.mock_scheduler.enter.assert_called_once_with(999, ANY, ANY, argument=ANY)

    def test_it_should_use_a_zero_priority_when_scheduling_jobs(self):
        self.test_model.start()
        self.mock_scheduler.enter.assert_called_once_with(ANY, 0, ANY, argument=ANY)

    def test_it_should_not_include_any_arguments(self):
        self.test_model.start()
        self.mock_scheduler.enter.assert_called_once_with(ANY, ANY, ANY, argument=())

    def test_it_should_run_the_scheduler(self):
        self.test_model.start()
        self.mock_scheduler.run.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
