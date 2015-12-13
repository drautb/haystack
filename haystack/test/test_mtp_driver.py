import unittest

from file import File
from mock import MagicMock
from executor import Executor
from mtp_driver import MTPDriver

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
    {
        'id': 1,
        'name': 'Music',
        'parent_id': None
    },
    {
        'id': 2,
        'name': 'Podcasts',
        'parent_id': None
    },
    {
        'id': 6,
        'name': 'Pictures',
        'parent_id': None
    },
    {
        'id': 2270,
        'name': 'Messenger',
        'parent_id': 6
    },
    {
        'id': 2305,
        'name': 'Screenshots',
        'parent_id': 6
    },
    {
        'id': 7,
        'name': 'Movies',
        'parent_id': None
    },
    {
        'id': 8,
        'name': 'Download',
        'parent_id': None
    },
    {
        'id': 9,
        'name': 'DCIM',
        'parent_id': None
    },
    {
        'id': 28,
        'name': 'Camera',
        'parent_id': 9
    },
    {
        'id': 65,
        'name': '.thumbnails',
        'parent_id': 9
    },
    {
        'id': 12,
        'name': 'Android',
        'parent_id': None
    },
    {
        'id': 13,
        'name': 'data',
        'parent_id': 12
    },
    {
        'id': 14,
        'name': 'com.google.android.videos',
        'parent_id': 13
    },
    {
        'id': 15,
        'name': 'files',
        'parent_id': 14
    },
    {
        'id': 16,
        'name': 'Movies',
        'parent_id': 15
    },
    {
        'id': 2815,
        'name': '.bkg',
        'parent_id': 12
    }
]

EXPECTED_FILE_STRUCTURE = [
    {
        'id': 10,
        'name': 'hangouts_message.ogg',
        'size': 30056,
        'parent_id': 3,
    },
    {
        'id': 11,
        'name': 'hangouts_incoming_call.ogg',
        'size': 76425,
        'parent_id': 3
    },
    {
        'id': 43,
        'name': 'IMG_20150613_115842622.jpg',
        'size': 1286823,
        'parent_id': 28
    },
    {
        'id': 44,
        'name': 'IMG_20150613_115844849.jpg',
        'size': 1328437,
        'parent_id': 28
    },
    {
        'id': 45,
        'name': 'IMG_20150616_083227764.jpg',
        'size': 838619,
        'parent_id': 28
    },
    {
        'id': 52,
        'name': 'emeals-30-minute-family-plan.pdf',
        'size': 447742,
        'parent_id': 8
    },
    {
        'id': 53,
        'name': 'emeals-30-minute-for2-plan.pdf',
        'size': 239629,
        'parent_id': 8
    },
    {
        'id': 7723,
        'name': 'IMG_20151211_115247128.jpg',
        'size': 1323560,
        'parent_id': 28
    },
    {
        'id': 7725,
        'name': 'VID_20151211_153724770.mp4',
        'size': 140120613,
        'parent_id': 28
    }
]


class TestMTPDriver(unittest.TestCase):
    def setUp(self):
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
        self.assertEqual(actual_folder_list, EXPECTED_FOLDER_STRUCTURE)

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
