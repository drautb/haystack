import unittest

from config import Config
from metadata_extractor import MetadataExtractor
from file import File
from index import Index
from indexer import Indexer
from mock import ANY
from mock import MagicMock
from mock import Mock
from mock import mock_open
from mock import patch
from thumbnail_generator import ThumbnailGenerator
from util import Util

ISDIR_MAPPING = {}


def mock_listdir(*args):
    mapping = {('/staging',): ['device-serial-1'],
               ('/staging/device-serial-1',): ['file.jpg', 'movie.mp4']}
    if args in mapping:
        return mapping[args]
    else:
        return False


def mock_isdir(*args):
    if args in ISDIR_MAPPING:
        return ISDIR_MAPPING[args]
    else:
        return False


def mock_staging_dir(*args):
    return '/staging/{0}'.format(args[0])


class TestIndexer(unittest.TestCase):
    def __reset_isdir_mapping(self):
        ISDIR_MAPPING[('/staging',)] = True
        ISDIR_MAPPING[('/staging/device-serial-1',)] = True
        ISDIR_MAPPING[('/pictures/2015/12/3',)] = True

    def setUp(self):
        self.__reset_isdir_mapping()

        self.mock_listdir_patcher = patch('os.listdir')
        self.mock_listdir = self.mock_listdir_patcher.start()
        self.mock_listdir.side_effect = mock_listdir

        self.mock_isdir_patcher = patch('os.path.isdir')
        self.mock_isdir = self.mock_isdir_patcher.start()
        self.mock_isdir.side_effect = mock_isdir

        self.mock_copy_patcher = patch('shutil.copy')
        self.mock_copy = self.mock_copy_patcher.start()

        self.mock_open_patcher = patch('indexer.open')
        self.mock_open = self.mock_open_patcher.start()

        # http://stackoverflow.com/questions/24779893/customizing-unittest-mock-mock-open-for-iteration
        self.mock_open.return_value = mock_open(read_data='fake-file-contents').return_value

        self.mock_remove_patcher = patch('os.remove')
        self.mock_remove = self.mock_remove_patcher.start()

        self.mock_config = Mock(spec=Config)
        self.mock_config.staging_root.return_value = '/staging'
        self.mock_config.thumbnail_path_pattern.return_value = '/thumbnails/%Y/%M/%D'
        self.mock_config.picture_path_pattern.return_value = '/pictures/%Y/%M/%D'
        self.mock_config.staging_directory.side_effect = mock_staging_dir

        self.mock_metadata_extractor = Mock(spec=MetadataExtractor)
        self.mock_metadata_extractor.get_date_taken.return_value = 1449176000

        self.mock_index = Mock(spec=Index)
        self.mock_index.is_duplicate.return_value = False

        self.mock_thumbnail_generator = Mock(spec=ThumbnailGenerator)

        self.mock_util = Mock(spec=Util)

        self.test_model = Indexer(self.mock_config, self.mock_index, self.mock_metadata_extractor,
                                  self.mock_thumbnail_generator, self.mock_util)

    def tearDown(self):
        self.mock_listdir_patcher.stop()
        self.mock_isdir_patcher.stop()
        self.mock_copy_patcher.stop()
        self.mock_open_patcher.stop()
        self.mock_remove_patcher.stop()

    def test_it_should_create_the_staging_root_if_it_doesnt_exist(self):
        ISDIR_MAPPING[('/staging',)] = False

        self.test_model.run()
        self.mock_util.mkdirp.assert_called_once_with('/staging')

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_thumbnail(self):
        expected_path_to_thumbnail = '/thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.test_model.run()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(ANY, expected_path_to_thumbnail)

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_file(self):
        expected_path_to_file = '/staging/device-serial-1/file.jpg'
        self.test_model.run()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(expected_path_to_file, ANY)

    def test_it_should_make_sure_that_the_final_location_directory_exists(self):
        ISDIR_MAPPING[('/pictures/2015/12/3',)] = False

        self.test_model.run()
        self.mock_util.mkdirp.assert_called_once_with('/pictures/2015/12/3')

    def test_it_should_copy_media_from_the_staging_location_to_the_final_location(self):
        self.test_model.run()
        self.mock_copy.assert_called_once_with('/staging/device-serial-1/file.jpg',
                                               '/pictures/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg')

    def test_it_should_index_media_with_the_right_final_path(self):
        expected_path_to_file = '/pictures/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.test_model.run()
        self.mock_index.index_media.assert_called_once_with(expected_path_to_file, ANY, ANY, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_thumbnail_path(self):
        expected_path_to_thumbnail = '/thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.test_model.run()
        self.mock_index.index_media.assert_called_once_with(ANY, expected_path_to_thumbnail, ANY, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_date_taken(self):
        self.test_model.run()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, 1449176000, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_device_id(self):
        self.test_model.run()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, 'device-serial-1', ANY, ANY)

    def test_it_should_index_media_with_the_right_hash(self):
        self.test_model.run()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, ANY, '6c8abb37a65a74b526d456927a19549d', ANY)

    def test_it_should_index_media_with_the_right_media_type(self):
        self.test_model.run()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, ANY, ANY, 'JPG')

    def test_it_should_delete_staged_media_after_indexing(self):
        self.test_model.run()
        self.mock_remove.assert_called_once_with('/staging/device-serial-1/file.jpg')

    def test_it_should_not_delete_staged_media_if_an_error_occurred_during_indexing(self):
        self.mock_index.index_media.side_effect = RuntimeError
        self.test_model.run()
        self.mock_remove.assert_not_called()

    def test_it_should_not_index_videos_yet(self):
        self.test_model.run()
        self.assertEqual(self.mock_open.call_count, 1)


if __name__ == '__main__':
    unittest.main()
