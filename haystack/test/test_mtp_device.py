import unittest
import pymtp
import util

from config import Config
from mock import ANY
from mock import MagicMock
from mock import patch
from mtp_device import MTPDevice
from mtp_driver import MTPDriver
from mtp_object import MTPObject


class TestMTPDevice(unittest.TestCase):

    def mock_folder(self, name, id, parent_id=None):
        return MTPObject(id, name, parent_id)

    def mock_file(self, name, id, parent_id, size):
        return MTPObject(id, name, parent_id, size)

    def setUp_mtp_get_folder_list(self, mock_mtp):
        folder_list = [self.mock_folder('Downloads', 1),
                       self.mock_folder('DCIM', 5),
                       self.mock_folder('Blah', 10),
                       self.mock_folder('Camera', 15, 5),
                       self.mock_folder('alternate', 20, 15),
                       self.mock_folder('thumbnails', 25, 5),
                       self.mock_folder('Stuff', 30, 10)]
        mock_mtp.get_folder_list.return_value = folder_list

    def setUp_mtp_get_filelisting(self, mock_mtp):
        file_listing = [self.mock_file('IMG_1234.jpg', 33, 20, 2048),
                        self.mock_file('boring.txt', 99, 30, 198)]
        mock_mtp.get_filelisting.return_value = file_listing

    def setUp(self):
        self.mock_config = MagicMock(spec=Config)
        self.mock_config.mtp_media_directories.return_value = ['DCIM', 'Pictures']
        self.mock_config.haystack_root.return_value = '/haystack'
        self.mock_config.staging_directory.return_value = '/haystack/staging/serial-number'

        self.mock_mtp = MagicMock(spec=MTPDriver)
        self.setUp_mtp_get_folder_list(self.mock_mtp)
        self.setUp_mtp_get_filelisting(self.mock_mtp)
        self.mock_mtp.detect_device.return_value = {
            'manufacturer': 'LG',
            'serial': 'serial-number',
            'model': 'Moto X'
        }

        self.mock_util = MagicMock(spec=util.Util)

        self.test_model = MTPDevice(self.mock_config, self.mock_mtp, self.mock_util)

    def test_transfer_media_should_do_nothing_if_no_devices_are_connected(self):
        self.mock_mtp.detect_device.return_value = None
        self.test_model.transfer_media()
        self.mock_mtp.get_folder_list.assert_not_called()

    def test_transfer_media_should_only_transfer_media_from_proper_directories(self):
        self.test_model.transfer_media()
        self.mock_mtp.get_file_to_file.assert_called_once_with(33, ANY)

    @patch('os.path.splitext')
    def test_transfer_media_should_only_transfer_recognized_media(self, mock_splitext):
        mock_splitext.return_value = ('ignore', '.gif')
        self.test_model.transfer_media()
        self.mock_mtp.get_file_to_file.assert_not_called()

    def test_transfer_media_should_transfer_media_to_staging_dir(self):
        self.test_model.transfer_media()
        self.mock_mtp.get_file_to_file.assert_called_once_with(ANY, '/haystack/staging/serial-number/IMG_1234.jpg')

    @patch('os.path.getsize')
    @patch('os.path.isfile')
    def test_transfer_media_should_delete_media_after_transfer(self, mock_isfile, mock_getsize):
        mock_isfile.return_value = True
        mock_getsize.return_value = 2048

        self.test_model.transfer_media()
        self.mock_mtp.delete_object.assert_called_once_with(33)

    @patch('os.path.isfile')
    def test_transfer_media_should_not_delete_media_if_it_didnt_transfer(self, mock_isfile):
        mock_isfile.return_value = False

        self.test_model.transfer_media()
        self.mock_mtp.delete_object.assert_not_called()

    @patch('os.path.getsize')
    def test_transfer_media_should_not_delete_media_if_it_didnt_transfer_completely(self, mock_getsize):
        mock_getsize.return_value = 2047

        self.test_model.transfer_media()
        self.mock_mtp.delete_object.assert_not_called()


if __name__ == '__main__':
    unittest.main()
