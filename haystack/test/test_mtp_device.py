import unittest
import pymtp
import util

from mock import ANY
from mock import MagicMock
from mock import patch
from mtp_device import MTPDevice
from pymtp import LIBMTP_Folder
from pymtp import LIBMTP_File


class TestMTPDevice(unittest.TestCase):

    def mock_folder(self, name, id, parent_id=0):
        f = MagicMock(spec=LIBMTP_Folder)
        f.name = name
        f.folder_id = id
        f.parent_id = parent_id
        return f

    def mock_file(self, name, id, parent_id, size):
        f = MagicMock(spec=LIBMTP_File)
        f.filename = name
        f.item_id = id
        f.parent_id = parent_id
        f.filesize = size
        return f

    def setUp_mtp_get_parent_folders(self, mock_mtp):
        parent_folders = [self.mock_folder('Downloads', 1),
                          self.mock_folder('DCIM', 5),
                          self.mock_folder('Blah', 10)]
        mock_mtp.get_parent_folders.return_value = parent_folders

    def setUp_mtp_get_folder_list(self, mock_mtp):
        folder_list = {1: self.mock_folder('Downloads', 1),
                       2: self.mock_folder('DCIM', 5),
                       3: self.mock_folder('Blah', 10),
                       4: self.mock_folder('Camera', 15, 5),
                       5: self.mock_folder('alternate', 20, 15),
                       6: self.mock_folder('thumbnails', 25, 5),
                       7: self.mock_folder('Stuff', 30, 10)}
        mock_mtp.get_folder_list.return_value = folder_list

    def setUp_mtp_get_filelisting(self, mock_mtp):
        file_listing = [self.mock_file('IMG_1234.jpg', 33, 20, 2048),
                        self.mock_file('boring.txt', 99, 30, 198)]
        mock_mtp.get_filelisting.return_value = file_listing

    def setUp(self):
        self.mock_config = MagicMock()
        self.mock_config.mtp_media_directories.return_value = ['DCIM', 'Pictures']
        self.mock_config.haystack_root.return_value = '/haystack'
        self.mock_config.staging_directory.return_value = '/haystack/staging/serial-number'

        self.mock_mtp = MagicMock(spec=pymtp.MTP)
        self.setUp_mtp_get_parent_folders(self.mock_mtp)
        self.setUp_mtp_get_folder_list(self.mock_mtp)
        self.setUp_mtp_get_filelisting(self.mock_mtp)
        self.mock_mtp.get_devicename.return_value = 'my-device'
        self.mock_mtp.get_serialnumber.return_value = 'serial-number'
        self.mock_mtp.get_manufacturer.return_value = 'LG'
        self.mock_mtp.get_modelname.return_value = 'Moto X'
        self.mock_mtp.get_deviceversion.return_value = '1.0'

        self.mock_path = patch('os.path').start()
        self.mock_path.isfile.return_value = True
        self.mock_path.getsize.return_value = 2048

        self.mock_util = MagicMock(spec=util.Util)

        self.test_model = MTPDevice(self.mock_config, self.mock_mtp, self.mock_util)

    def test_transfer_media_should_handle_connection_errors(self):
        self.mock_mtp.connect.side_effect = Exception('Some connection error')
        self.test_model.transfer_media()

    def test_transfer_media_should_not_disconnect_if_connect_failed(self):
        self.mock_mtp.connect.side_effect = Exception('Some connection error')
        self.test_model.transfer_media()
        self.mock_mtp.disconnect.assert_not_called()

    def test_transfer_media_should_do_nothing_if_no_devices_are_connected(self):
        self.mock_mtp.detect_devices.return_value = []
        self.test_model.transfer_media()
        self.mock_mtp.connect.assert_not_called()

    def test_transfer_media_should_only_transfer_media_from_proper_directories(self):
        self.test_model.transfer_media()
        self.mock_mtp.get_file_to_file.assert_called_once_with(33, ANY)

    def test_transfer_media_should_transfer_media_to_staging_dir(self):
        self.test_model.transfer_media()
        self.mock_mtp.get_file_to_file.assert_called_once_with(ANY, '/haystack/staging/serial-number/IMG_1234.jpg')

    def test_transfer_media_should_delete_media_after_transfer(self):
        self.test_model.transfer_media()
        self.mock_mtp.delete_object.assert_called_once_with(33)

    def test_transfer_media_should_not_delete_media_if_it_didnt_transfer(self):
        self.mock_path.isfile.return_value = False
        self.test_model.transfer_media()
        self.mock_mtp.delete_object.assert_not_called()

    def test_transfer_media_should_not_delete_media_if_it_didnt_transfer_completely(self):
        self.mock_path.getsize.return_value = 2047
        self.test_model.transfer_media()
        self.mock_mtp.delete_object.assert_not_called()


if __name__ == '__main__':
    unittest.main()
