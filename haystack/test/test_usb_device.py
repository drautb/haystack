import config
import unittest
import util

from mock import MagicMock
from mock import call
from mock import patch
from usb_device import USBDevice


def mock_walk(*args):
    return [(args[0], None, ['file-top.jpg']),
            (args[0] + '/subfolder1', None, ['file-1.jpg']),
            (args[0] + '/subfolder1/subfolder2', None, ['file-2.jpg'])]


def mock_isdir(*args):
    mapping = {('/Volumes/my-dev/to-index',): True,
               ('/Volumes/my-dev/also-to-index',): True,
               ('/Volumes/third-to-index',): False}
    if args in mapping:
        return mapping[args]
    else:
        return False


def mock_join(*args):
    return '/'.join(args)


class TestUSBDevice(unittest.TestCase):
    def setUp(self):
        self.mock_walk = patch('os.walk').start()
        self.mock_walk.side_effect = mock_walk

        self.mock_isdir = patch('os.path.isdir').start()
        self.mock_isdir.side_effect = mock_isdir

        self.mock_join = patch('os.path.join').start()
        self.mock_join.side_effect = mock_join

        self.mock_shutil_move = patch('shutil.move').start()

        self.mock_config = MagicMock(spec=config.Config)
        self.mock_config.usb_media_directories.return_value = ['to-index', 'also-to-index', 'third-to-index']
        self.mock_config.staging_directory.return_value = '/root/staging/device'

        self.mock_util = MagicMock(spec=util.Util)
        self.mock_util.get_uuid.return_value = 'some-uuid'

        self.test_model = USBDevice(self.mock_config, self.mock_util)

    def test_transfer_media_should_use_the_device_id_to_get_the_staging_directory(self):
        self.test_model.transfer_media('/Volumes/my-dev', 'my-dev')
        self.mock_config.staging_directory.assert_called_once_with('my-dev')

    def test_transfer_media_should_transfer_the_right_media_files(self):
        self.test_model.transfer_media('/Volumes/my-dev', 'my-dev')
        calls = [call('/Volumes/my-dev/to-index/file-top.jpg', '/root/staging/device/some-uuid.jpg'),
                 call('/Volumes/my-dev/to-index/subfolder1/file-1.jpg', '/root/staging/device/some-uuid.jpg'),
                 call('/Volumes/my-dev/to-index/subfolder1/subfolder2/file-2.jpg',
                      '/root/staging/device/some-uuid.jpg'),
                 call('/Volumes/my-dev/also-to-index/file-top.jpg', '/root/staging/device/some-uuid.jpg'),
                 call('/Volumes/my-dev/also-to-index/subfolder1/file-1.jpg', '/root/staging/device/some-uuid.jpg'),
                 call('/Volumes/my-dev/also-to-index/subfolder1/subfolder2/file-2.jpg',
                      '/root/staging/device/some-uuid.jpg')]
        self.mock_shutil_move.assert_has_calls(calls)
