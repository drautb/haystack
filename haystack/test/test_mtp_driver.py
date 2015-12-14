import unittest

from executor import Executor
from file import File
from mock import MagicMock
from mtp_driver import MTPDriver
from mtp_object import MTPObject

MTP_DETECT_NOT_CONNECTED_RESOURCE = 'mtp-detect-not-connected.txt'
MTP_DETECT_CONNECTED_RESOURCE = 'mtp-detect-connected.txt'
MTP_FOLDERS_CONNECTED_RESOURCE = 'mtp-folders-connected.txt'
MTP_FILES_CONNECTED_RESOURCE = 'mtp-files-connected.txt'

EXPECTED_DEVICE_INFO = {
    'manufacturer': 'motorola',
    'model': 'XT1031',
    'serial': 'TA965195GE'
}

EXPECTED_FOLDER_STRUCTURE = [
    MTPObject(1, 'Music'),
    MTPObject(2, 'Podcasts'),
    MTPObject(6, 'Pictures'),
    MTPObject(2270, 'Messenger', 6),
    MTPObject(2305, 'Screenshots', 6),
    MTPObject(7, 'Movies'),
    MTPObject(8, 'Download'),
    MTPObject(9, 'DCIM'),
    MTPObject(28, 'Camera', 9),
    MTPObject(65, '.thumbnails', 9),
    MTPObject(12, 'Android'),
    MTPObject(13, 'data', 12),
    MTPObject(14, 'com.google.android.videos', 13),
    MTPObject(15, 'files', 14),
    MTPObject(16, 'Movies', 15),
    MTPObject(2815, '.bkg', 12)
]

EXPECTED_FILE_STRUCTURE = [
    MTPObject(10, 'hangouts_message.ogg', 3, 30056),
    MTPObject(11, 'hangouts_incoming_call.ogg', 3, 76425),
    MTPObject(43, 'IMG_20150613_115842622.jpg', 28, 1286823),
    MTPObject(44, 'IMG_20150613_115844849.jpg', 28, 1328437),
    MTPObject(45, 'IMG_20150616_083227764.jpg', 28, 838619),
    MTPObject(52, 'emeals-30-minute-family-plan.pdf', 8, 447742),
    MTPObject(53, 'emeals-30-minute-for2-plan.pdf', 8, 239629),
    MTPObject(7723, 'IMG_20151211_115247128.jpg', 28, 1323560),
    MTPObject(7725, 'VID_20151211_153724770.mp4', 28, 140120613)
]


class TestMTPDriver(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.mock_executor = MagicMock(spec=Executor)

        self.test_model = MTPDriver(self.mock_executor)

    def tearDown(self):
        return

    def __get_resource(self, resource_name):
        contents = ''
        with open('test/resources/' + resource_name, 'r') as f:
            contents = f.read()

        return contents

    def test_it_should_know_if_no_devices_are_connected(self):
        self.mock_executor.execute_output.return_value = self.__get_resource(MTP_DETECT_NOT_CONNECTED_RESOURCE)
        self.assertFalse(self.test_model.detect_device())

    def test_it_should_know_if_a_device_is_connected(self):
        self.mock_executor.execute_output.return_value = self.__get_resource(MTP_DETECT_CONNECTED_RESOURCE)
        self.assertEqual(EXPECTED_DEVICE_INFO, self.test_model.detect_device())

    def test_it_should_accurately_describe_the_devices_folders(self):
        self.mock_executor.execute_output.return_value = self.__get_resource(MTP_FOLDERS_CONNECTED_RESOURCE)
        actual_folder_list = self.test_model.get_folder_list()
        self.assertItemsEqual(actual_folder_list, EXPECTED_FOLDER_STRUCTURE)

    def test_it_should_accurately_describe_the_file_structure(self):
        self.mock_executor.execute_output.return_value = self.__get_resource(MTP_FILES_CONNECTED_RESOURCE)
        actual_file_list = self.test_model.get_filelisting()
        self.assertEqual(actual_file_list, EXPECTED_FILE_STRUCTURE)

    def test_it_should_properly_copy_a_file(self):
        self.test_model.get_file_to_file(42, '/root/staging/id/file.jpg')
        self.mock_executor.execute.assert_called_once_with(['mtp-getfile', '42', '/root/staging/id/file.jpg'])

    def test_it_should_properly_delete_a_file(self):
        self.test_model.delete_object(42)
        self.mock_executor.execute.assert_called_once_with(['mtp-delfile', '-n', '42'])


if __name__ == '__main__':
    unittest.main()
