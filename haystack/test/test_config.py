import unittest

from config import Config
from ConfigParser import ConfigParser
from mock import MagicMock


def mock_config(*args):
    return {('Timing', 'ExecutionIntervalInSeconds'): '1200',
            ('MTP', 'PathsToIndex'): '/dir1,/dir2',
            ('MTP', 'Ignore'): 'serial',
            ('USB', 'PathsToIndex'): '/dir3,/dir4',
            ('USB', 'MountPoints'): '/Volumes',
            ('USB', 'Ignore'): 'Macintosh HD',
            ('PathsToFiles', 'HaystackRoot'): '/root',
            ('PathsToFiles', 'ThumbnailPath'): '/thumbnails',
            ('PathsToFiles', 'PicturePath'): '/pictures',
            ('PathsToFiles', 'VideoPath'): '/videos'}[args]


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.mock_config_parser = MagicMock(spec=ConfigParser)
        self.mock_config_parser.get.side_effect = mock_config
        self.test_model = Config(self.mock_config_parser)

    def test_it_should_load_the_right_config_file(self):
        self.mock_config_parser.read.assert_called_with('config.properties')

    def test_indexer_delay_should_refresh_the_config(self):
        self.test_model.indexer_delay()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_indexer_delay_should_return_the_right_config_value(self):
        actual_delay = self.test_model.indexer_delay()
        self.assertEqual(actual_delay, 1200)

    def test_mtp_media_directories_should_refresh_the_config(self):
        self.test_model.mtp_media_directories()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_mtp_media_directories_should_return_the_right_list(self):
        actual_value = self.test_model.mtp_media_directories()
        self.assertEqual(actual_value, ['/dir1', '/dir2'])

    def test_mtp_devices_to_ignore_should_refresh_the_config(self):
        self.test_model.mtp_devices_to_ignore()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_mtp_devices_to_ignore_should_return_the_right_list(self):
        actual_value = self.test_model.mtp_devices_to_ignore()
        self.assertEqual(actual_value, ['serial'])

    def test_usb_media_directories_should_refresh_the_config(self):
        self.test_model.usb_media_directories()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_usb_media_directories_should_return_the_right_list(self):
        actual_value = self.test_model.usb_media_directories()
        self.assertEqual(actual_value, ['/dir3', '/dir4'])

    def test_usb_mount_points_should_refresh_the_config(self):
        self.test_model.usb_mount_points()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_usb_mount_points_should_return_the_right_list(self):
        actual_value = self.test_model.usb_mount_points()
        self.assertEqual(actual_value, ['/Volumes'])

    def test_usb_devices_to_ignore_should_refresh_the_config(self):
        self.test_model.usb_devices_to_ignore()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_usb_devices_to_ignore_should_return_the_right_list(self):
        actual_value = self.test_model.usb_devices_to_ignore()
        self.assertEqual(actual_value, ['Macintosh HD'])

    def test_haystack_root_should_refresh_the_config(self):
        self.test_model.haystack_root()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_haystack_root_should_return_the_right_directory(self):
        actual_value = self.test_model.haystack_root()
        self.assertEqual(actual_value, '/root')

    def test_staging_directory_should_refresh_the_config(self):
        self.test_model.staging_directory('device-id')
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_staging_directory_should_return_the_right_directory(self):
        actual_value = self.test_model.staging_directory('device-id')
        self.assertEqual(actual_value, '/root/staging/device-id')

    def test_thumbnail_path_pattern_should_refresh_the_config(self):
        self.test_model.thumbnail_path_pattern()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_thumbnail_path_pattern_should_return_the_right_directory(self):
        actual_value = self.test_model.thumbnail_path_pattern()
        self.assertEqual(actual_value, '/thumbnails')

    def test_picture_path_pattern_should_refresh_the_config(self):
        self.test_model.picture_path_pattern()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_picture_path_pattern_should_return_the_right_directory(self):
        actual_value = self.test_model.picture_path_pattern()
        self.assertEqual(actual_value, '/pictures')

    def test_video_path_pattern_should_refresh_the_config(self):
        self.test_model.video_path_pattern()
        self.assertEqual(self.mock_config_parser.read.call_count, 2)

    def test_video_path_pattern_should_return_the_right_directory(self):
        actual_value = self.test_model.video_path_pattern()
        self.assertEqual(actual_value, '/videos')


if __name__ == '__main__':
    unittest.main()
