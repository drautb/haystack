import unittest

from mock import patch
from usb_device_manager import USBDeviceManager


def mock_listdir(*args):
    return {('/Volumes',): ['dev1', 'some-file'],
            ('/media',): ['dev2', 'another-file']}[args]


def mock_isdir(*args):
    return {('/Volumes',): True,
            ('/media',): True,
            ('/Volumes/dev1',): True,
            ('/media/dev2',): True,
            ('/Volumes/some-file',): False,
            ('/media/another-file',): False}[args]


def mock_join(*args):
    return '/'.join(args)


class TestUSBDeviceManager(unittest.TestCase):
    def setUp(self):
        self.mock_os_listdir_patcher = patch('os.listdir')
        self.mock_os_listdir = self.mock_os_listdir_patcher.start()
        self.mock_os_listdir.side_effect = mock_listdir

        self.mock_path_isdir_patcher = patch('os.path.isdir')
        self.mock_path_isdir = self.mock_path_isdir_patcher.start()
        self.mock_path_isdir.side_effect = mock_isdir

        self.mock_path_join_patcher = patch('os.path.join')
        self.mock_path_join = self.mock_path_join_patcher.start()
        self.mock_path_join.side_effect = mock_join

        self.test_model = USBDeviceManager()

    def tearDown(self):
        self.mock_os_listdir_patcher.stop()
        self.mock_path_isdir_patcher.stop()
        self.mock_path_join_patcher.stop()

    def test_get_devices_should_check_for_existence(self):
        self.mock_path_isdir.side_effect = lambda *args: False
        results = self.test_model.get_devices_to_index(['/Volumes'], [])
        self.assertEqual(results, [])

    def test_get_devices_to_index_should_full_paths(self):
        results = self.test_model.get_devices_to_index(['/Volumes'], [])
        self.assertEqual(results, [('/Volumes/dev1', 'dev1')])

    def test_get_devices_to_index_should_work_with_multiple_mount_points(self):
        results = self.test_model.get_devices_to_index(['/Volumes', '/media'], [])
        self.assertEqual(results, [('/Volumes/dev1', 'dev1'), ('/media/dev2', 'dev2')])

    def test_get_devices_to_index_should_respect_devices_to_ignore(self):
        results = self.test_model.get_devices_to_index(['/Volumes', '/media'], ['dev2'])
        self.assertEqual(results, [('/Volumes/dev1', 'dev1')])


if __name__ == '__main__':
    unittest.main()
