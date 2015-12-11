import unittest

from config import Config
from file import File
from index import Index
from indexer import Indexer
from metadata_helper import MetadataHelper
from mock import ANY
from mock import MagicMock
from mock import Mock
from mock import mock_open
from mock import patch
from preprocessor import Preprocessor
from thumbnail_generator import ThumbnailGenerator
from util import Util
from video_converter import VideoConverter

LISTDIR_MAPPING = {}
ISDIR_MAPPING = {}


def mock_listdir(*args):
    if args in LISTDIR_MAPPING:
        return LISTDIR_MAPPING[args]
    else:
        return False


def mock_isdir(*args):
    if args in ISDIR_MAPPING:
        return ISDIR_MAPPING[args]
    else:
        return False


def mock_staging_dir(*args):
    return '/root/staging/{0}'.format(args[0])


class TestIndexer(unittest.TestCase):
    def __reset_listdir_mapping(self):
        LISTDIR_MAPPING[('/root/staging',)] = ['device-serial-1']
        LISTDIR_MAPPING[('/root/staging/device-serial-1',)] = ['file.jpg']

    def __reset_isdir_mapping(self):
        ISDIR_MAPPING[('/root/staging',)] = True
        ISDIR_MAPPING[('/root/staging/device-serial-1',)] = True
        ISDIR_MAPPING[('/root/pictures/2015/12/3',)] = True
        ISDIR_MAPPING[('/root/videos/2015/12/3',)] = True

    def setUp(self):
        self.__reset_listdir_mapping()
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
        self.mock_config.haystack_root.return_value = '/root'
        self.mock_config.staging_root.return_value = '/root/staging'
        self.mock_config.thumbnail_path_pattern.return_value = '/root/thumbnails/%Y/%M/%D'
        self.mock_config.picture_path_pattern.return_value = '/root/pictures/%Y/%M/%D'
        self.mock_config.video_path_pattern.return_value = '/root/videos/%Y/%M/%D'
        self.mock_config.staging_directory.side_effect = mock_staging_dir

        self.mock_metadata_helper = Mock(spec=MetadataHelper)
        self.mock_metadata_helper.get_date_taken.return_value = 1449176000

        self.mock_index = Mock(spec=Index)
        self.mock_index.is_duplicate.return_value = False

        self.mock_thumbnail_generator = Mock(spec=ThumbnailGenerator)

        self.mock_util = Mock(spec=Util)

        self.mock_video_converter = MagicMock(spec=VideoConverter)

        self.mock_preprocessor = MagicMock(spec=Preprocessor)

        self.test_model = Indexer(self.mock_config, self.mock_index, self.mock_metadata_helper,
                                  self.mock_thumbnail_generator, self.mock_util, self.mock_video_converter,
                                  self.mock_preprocessor)

    def __run_mp4_test(self):
        LISTDIR_MAPPING[('/root/staging/device-serial-1',)] = ['file.mp4']
        self.test_model.run()

    def __run_mts_test(self):
        LISTDIR_MAPPING[('/root/staging/device-serial-1',)] = ['file.mts']
        self.test_model.run()

    def tearDown(self):
        self.mock_listdir_patcher.stop()
        self.mock_isdir_patcher.stop()
        self.mock_copy_patcher.stop()
        self.mock_open_patcher.stop()
        self.mock_remove_patcher.stop()

    def test_it_should_create_the_staging_root_if_it_doesnt_exist(self):
        ISDIR_MAPPING[('/root/staging',)] = False

        self.test_model.run()
        self.mock_util.mkdirp.assert_called_once_with('/root/staging')

    def test_it_should_preprocess_the_file(self):
        self.test_model.run()
        self.mock_preprocessor.preprocess.assert_called_once_with('/root/staging/device-serial-1/file.jpg')

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_thumbnail(self):
        expected_path_to_thumbnail = '/root/thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.test_model.run()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(ANY, expected_path_to_thumbnail)

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_file(self):
        expected_path_to_file = '/root/staging/device-serial-1/file.jpg'
        self.test_model.run()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(expected_path_to_file, ANY)

    def test_it_should_make_sure_that_the_final_location_directory_exists(self):
        ISDIR_MAPPING[('/root/pictures/2015/12/3',)] = False

        self.test_model.run()
        self.mock_util.mkdirp.assert_called_once_with('/root/pictures/2015/12/3')

    def test_it_should_copy_media_from_the_staging_location_to_the_final_location(self):
        self.test_model.run()
        self.mock_copy.assert_called_once_with('/root/staging/device-serial-1/file.jpg',
                                               '/root/pictures/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg')

    # The indexed paths are relative to the root because that is where the file server will run from.
    # It would be _bad_ to have a file server running at '/', instead of somewhere lower.
    def test_it_should_index_media_with_the_right_final_path(self):
        expected_path_to_file = 'pictures/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.test_model.run()
        self.mock_index.index_media.assert_called_once_with(expected_path_to_file, ANY, ANY, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_thumbnail_path(self):
        expected_path_to_thumbnail = 'thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
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
        self.mock_remove.assert_called_once_with('/root/staging/device-serial-1/file.jpg')

    def test_it_should_not_delete_staged_media_if_an_error_occurred_during_indexing(self):
        self.mock_index.index_media.side_effect = RuntimeError
        self.test_model.run()
        self.mock_remove.assert_not_called()

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_thumbnail_for_mp4_videos(self):
        expected_path_to_thumbnail = '/root/thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.__run_mp4_test()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(ANY, expected_path_to_thumbnail)

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_file_for_mp4_videos(self):
        expected_path_to_file = '/root/staging/device-serial-1/file.mp4'
        self.__run_mp4_test()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(expected_path_to_file, ANY)

    def test_it_should_not_convert_mp4_videos(self):
        self.__run_mp4_test()
        self.mock_video_converter.convert_to_mp4.assert_not_called()

    def test_it_should_make_sure_that_the_final_location_directory_exists_for_mp4_videos(self):
        ISDIR_MAPPING[('/root/videos/2015/12/3',)] = False

        self.__run_mp4_test()
        self.mock_util.mkdirp.assert_called_once_with('/root/videos/2015/12/3')

    def test_it_should_copy_media_from_the_staging_location_to_the_final_location_for_mp4_videos(self):
        self.__run_mp4_test()
        self.mock_copy.assert_called_once_with('/root/staging/device-serial-1/file.mp4',
                                               '/root/videos/2015/12/3/6c8abb37a65a74b526d456927a19549d.mp4')

    def test_it_should_index_media_with_the_right_final_path_for_mp4_videos(self):
        expected_path_to_file = 'videos/2015/12/3/6c8abb37a65a74b526d456927a19549d.mp4'
        self.__run_mp4_test()
        self.mock_index.index_media.assert_called_once_with(expected_path_to_file, ANY, ANY, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_thumbnail_path_for_mp4_videos(self):
        expected_path_to_thumbnail = 'thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.__run_mp4_test()
        self.mock_index.index_media.assert_called_once_with(ANY, expected_path_to_thumbnail, ANY, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_date_taken_for_mp4_videos(self):
        self.__run_mp4_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, 1449176000, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_device_id_for_mp4_videos(self):
        self.__run_mp4_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, 'device-serial-1', ANY, ANY)

    def test_it_should_index_media_with_the_right_hash_for_mp4_videos(self):
        self.__run_mp4_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, ANY, '6c8abb37a65a74b526d456927a19549d', ANY)

    def test_it_should_index_media_with_the_right_media_type_for_mp4_videos(self):
        self.__run_mp4_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, ANY, ANY, 'MP4')

    def test_it_should_delete_staged_media_after_indexing_for_mp4_videos(self):
        self.__run_mp4_test()
        self.mock_remove.assert_called_once_with('/root/staging/device-serial-1/file.mp4')

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_thumbnail_for_mts_videos(self):
        expected_path_to_thumbnail = '/root/thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.__run_mp4_test()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(ANY, expected_path_to_thumbnail)

    def test_it_should_generate_a_thumbnail_using_the_expected_path_to_file_for_mts_videos(self):
        expected_path_to_file = '/root/staging/device-serial-1/file.mts'
        self.__run_mts_test()
        self.mock_thumbnail_generator.generate_thumbnail.assert_called_once_with(expected_path_to_file, ANY)

    def test_it_should_convert_mts_videos_to_mp4_using_the_right_source_file(self):
        self.__run_mts_test()
        self.mock_video_converter.convert_to_mp4.assert_called_once_with('/root/staging/device-serial-1/file.mts',
                                                                         ANY, ANY)

    def test_it_should_convert_mts_videos_to_mp4_using_the_right_dest_file(self):
        self.__run_mts_test()
        (self.mock_video_converter.convert_to_mp4
            .assert_called_once_with(ANY, '/root/videos/2015/12/3/6c8abb37a65a74b526d456927a19549d.mp4', ANY))

    def test_it_should_convert_mts_videos_to_mp4_using_the_right_create_time(self):
        self.__run_mts_test()
        self.mock_video_converter.convert_to_mp4.assert_called_once_with(ANY, ANY, 1449176000)

    def test_it_should_make_sure_that_the_final_location_directory_exists_for_mts_videos(self):
        ISDIR_MAPPING[('/root/videos/2015/12/3',)] = False

        self.__run_mts_test()
        self.mock_util.mkdirp.assert_called_once_with('/root/videos/2015/12/3')

    # We don't have to copy it because the conversion placed it there already.
    def test_it_should_not_copy_media_from_the_staging_location_to_the_final_location_for_mts_videos(self):
        self.__run_mts_test()
        self.mock_copy.assert_not_called()

    def test_it_should_index_media_with_the_right_final_path_for_mts_videos(self):
        expected_path_to_file = 'videos/2015/12/3/6c8abb37a65a74b526d456927a19549d.mp4'
        self.__run_mts_test()
        self.mock_index.index_media.assert_called_once_with(expected_path_to_file, ANY, ANY, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_thumbnail_path_for_mts_videos(self):
        expected_path_to_thumbnail = 'thumbnails/2015/12/3/6c8abb37a65a74b526d456927a19549d.jpg'
        self.__run_mts_test()
        self.mock_index.index_media.assert_called_once_with(ANY, expected_path_to_thumbnail, ANY, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_date_taken_for_mts_videos(self):
        self.__run_mts_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, 1449176000, ANY, ANY, ANY)

    def test_it_should_index_media_with_the_right_device_id_for_mts_videos(self):
        self.__run_mts_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, 'device-serial-1', ANY, ANY)

    def test_it_should_index_media_with_the_right_hash_for_mts_videos(self):
        self.__run_mts_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, ANY, '6c8abb37a65a74b526d456927a19549d', ANY)

    def test_it_should_index_converted_mts_videos_as_mp4(self):
        self.__run_mts_test()
        self.mock_index.index_media.assert_called_once_with(ANY, ANY, ANY, ANY, ANY, 'MP4')

    def test_it_should_delete_staged_media_after_indexing_for_mts_videos(self):
        self.__run_mts_test()
        self.mock_remove.assert_called_once_with('/root/staging/device-serial-1/file.mts')

if __name__ == '__main__':
    unittest.main()
