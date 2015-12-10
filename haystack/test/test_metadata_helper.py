import unittest

from exiftool import ExifTool
from metadata_helper import MetadataHelper
from mock import MagicMock
from mock import patch

TEST_FILE_MTS = '/path/to/file.mts'
TEST_FILE_MP4 = '/path/to/file.mp4'
TEST_FILE_JPG = '/path/to/file.jpg'

MISSING_DATE_MTS = '/path/to/broken/file.mts'
MISSING_DATE_MP4 = '/path/to/broken/file.mp4'
MISSING_EVERYTHING_JPG = '/path/to/broken/file.jpg'


def mock_get_metadata(*args):
    mapping = {(TEST_FILE_MTS,): {'H264:DateTimeOriginal': '2015:11:16 20:00:00-05:00'},
               (TEST_FILE_MTS.replace('.mts', '.MTS'),): {'H264:DateTimeOriginal': '2015:11:16 20:00:00-05:00'},
               (TEST_FILE_MP4,): {'QuickTime:CreateDate': '2015:10:13 00:26:44', 'Composite:Rotation': '90'},
               (TEST_FILE_JPG,): {'EXIF:DateTimeOriginal': '2015:06:23 21:52:13', 'EXIF:Orientation': '6'},
               (MISSING_DATE_MTS,): {'FileType': 'H264'},
               (MISSING_DATE_MP4,): {'FileType': 'MP4'},
               (MISSING_EVERYTHING_JPG,): {'FileType': 'JPG'}}
    if args in mapping:
        return mapping[args]
    else:
        return False


class TestMetadataHelper(unittest.TestCase):
    def setUp(self):
        self.mock_exiftool_patcher = patch('metadata_helper.exiftool')
        self.mock_exiftool = self.mock_exiftool_patcher.start()

        self.mock_exiftool_class = MagicMock(spec=ExifTool)
        self.mock_exiftool.ExifTool.return_value = self.mock_exiftool_class

        self.mock_exiftool_instance = MagicMock()
        self.mock_exiftool_instance.get_metadata = mock_get_metadata

        self.mock_exiftool_class.__enter__.return_value = self.mock_exiftool_instance

        self.test_model = MetadataHelper()

    def tearDown(self):
        self.mock_exiftool_patcher.stop()

    def test_it_should_return_a_utc_timestamp_for_mts_files(self):
        time = self.test_model.get_date_taken(TEST_FILE_MTS)
        self.assertEqual(time, 1447729200)

    def test_it_should_be_case_insensitive_on_extensions(self):
        time = self.test_model.get_date_taken(TEST_FILE_MTS.replace('.mts', '.MTS'))
        self.assertEqual(time, 1447729200)

    def test_it_should_raise_an_error_if_an_mts_file_is_missing_a_create_tag(self):
        with self.assertRaises(RuntimeError):
            time = self.test_model.get_date_taken(MISSING_DATE_MTS)

    def test_it_should_return_a_utc_timestamp_for_mp4_files(self):
        time = self.test_model.get_date_taken(TEST_FILE_MP4)
        self.assertEqual(time, 1444717604)

    def test_it_should_raise_an_error_if_an_mp4_file_is_missing_a_create_tag(self):
        with self.assertRaises(RuntimeError):
            time = self.test_model.get_date_taken(MISSING_DATE_MP4)

    def test_it_should_return_a_utc_timestamp_for_mp4_files(self):
        time = self.test_model.get_date_taken(TEST_FILE_JPG)
        self.assertEqual(time, 1435117933)

    def test_it_should_raise_an_error_if_an_jpg_file_is_missing_a_create_tag(self):
        with self.assertRaises(RuntimeError):
            time = self.test_model.get_date_taken(MISSING_EVERYTHING_JPG)

    def test_it_should_raise_a_runtime_error_if_the_extension_isnt_recognized(self):
        with self.assertRaises(RuntimeError):
            time = self.test_model.get_date_taken('bogus.txt')

    def test_it_should_return_the_right_rotation_value_if_it_exists_for_mp4_files(self):
        rotation = self.test_model.get_rotation(TEST_FILE_MP4)
        self.assertEqual(rotation, 90)

    def test_it_should_return_the_right_rotation_value_if_it_exists_for_jpg_files(self):
        rotation = self.test_model.get_rotation(TEST_FILE_JPG)
        self.assertEqual(rotation, 6)

    def test_it_should_return_the_right_rotation_value_if_it_doesnt_exist_for_jpg_files(self):
        rotation = self.test_model.get_rotation(MISSING_EVERYTHING_JPG)
        self.assertEqual(rotation, 0)

    def test_it_should_return_0_for_rotation_if_it_doesnt_exist(self):
        rotation = self.test_model.get_rotation(TEST_FILE_MTS)
        self.assertEqual(rotation, 0)

    def test_it_should_correctly_set_rotation_on_image_files(self):
        self.test_model.set_rotation(TEST_FILE_JPG, 3)
        self.mock_exiftool_instance.execute.assert_called_once_with('-EXIF:Orientation=3', '-overwrite_original',
                                                                    TEST_FILE_JPG)

if __name__ == '__main__':
    unittest.main()
