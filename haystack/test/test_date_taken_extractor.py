import unittest

from date_taken_extractor import DateTakenExtractor
from exiftool import ExifTool
from mock import MagicMock

TEST_FILE_MTS = '/path/to/file.mts'
TEST_FILE_MP4 = '/path/to/file.mp4'
TEST_FILE_JPG = '/path/to/file.jpg'

MISSING_DATE_MTS = '/path/to/broken/file.mts'
MISSING_DATE_MP4 = '/path/to/broken/file.mp4'
MISSING_DATE_JPG = '/path/to/broken/file.jpg'


def mock_get_metadata(*args):
    mapping = {(TEST_FILE_MTS,): {'H264:DateTimeOriginal': '2015:11:16 20:00:00-05:00'},
               (TEST_FILE_MTS.replace('.mts', '.MTS'),): {'H264:DateTimeOriginal': '2015:11:16 20:00:00-05:00'},
               (TEST_FILE_MP4,): {'QuickTime:CreateDate': '2015:10:13 00:26:44'},
               (TEST_FILE_JPG,): {'EXIF:DateTimeOriginal': '2015:06:23 21:52:13'},
               (MISSING_DATE_MTS,): {'FileType': 'H264'},
               (MISSING_DATE_MP4,): {'FileType': 'MP4'},
               (MISSING_DATE_JPG,): {'FileType': 'JPG'}}
    if args in mapping:
        return mapping[args]
    else:
        return False


class TestDateTakenExtractor(unittest.TestCase):
    def setUp(self):
        self.mock_exif_tool = MagicMock(spec=ExifTool)
        self.mock_exif_tool.get_metadata = mock_get_metadata

        self.test_model = DateTakenExtractor(self.mock_exif_tool)

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
            time = self.test_model.get_date_taken(MISSING_DATE_JPG)

    def test_it_should_raise_a_runtime_error_if_the_extension_isnt_recognized(self):
        with self.assertRaises(RuntimeError):
            time = self.test_model.get_date_taken('bogus.txt')


if __name__ == '__main__':
    unittest.main()
