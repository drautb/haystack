import mock
import unittest

from config import Config
from executor import Executor
from metadata_helper import MetadataHelper
from mock import ANY
from mock import MagicMock
from mock import patch
from PIL import Image
from thumbnail_generator import ThumbnailGenerator
from util import Util

PATH_TO_IMG_FILE = '/haystack/file.jpg'
PATH_TO_IMG_THUMBNAIL = '/haystack/thumbs/file.jpg'

PATH_TO_VIDEO_FILE = '/haystack/file.mp4'
PATH_TO_VIDEO_THUMBNAIL = '/haystack/thumbs/file.mp4'

DEFAULT_THUMBNAIL_SIZE = 128


class TestThumbnailGenerator(unittest.TestCase):
    def setUp(self):
        self.mock_isdir_patcher = patch('os.path.isdir')
        self.mock_isdir = self.mock_isdir_patcher.start()
        self.mock_isdir.return_value = True

        self.mock_image_file = MagicMock()

        self.mock_image_open_patcher = patch('thumbnail_generator.Image.open')
        self.mock_image_open = self.mock_image_open_patcher.start()
        self.mock_image_open.return_value = self.mock_image_file

        self.mock_config = MagicMock(spec=Config)
        self.mock_config.thumbnail_size.return_value = DEFAULT_THUMBNAIL_SIZE

        self.mock_util = MagicMock(spec=Util)

        self.mock_metadata_helper = MagicMock(spec=MetadataHelper)
        self.mock_metadata_helper.get_rotation.return_value = 0

        self.mock_executor = MagicMock(spec=Executor)

        self.test_model = ThumbnailGenerator(self.mock_config, self.mock_util, self.mock_metadata_helper,
                                             self.mock_executor)

    def tearDown(self):
        self.mock_isdir_patcher.stop()
        self.mock_image_open_patcher.stop()

    def __run_img_test(self):
        self.test_model.generate_thumbnail(PATH_TO_IMG_FILE, PATH_TO_IMG_THUMBNAIL)
        self.mock_executor.execute.assert_not_called()

    def __run_video_test(self):
        self.test_model.generate_thumbnail(PATH_TO_VIDEO_FILE, PATH_TO_VIDEO_THUMBNAIL)
        self.mock_image_file.open.assert_not_called()

    def test_it_should_open_the_right_file(self):
        self.__run_img_test()
        self.mock_image_open.assert_called_once_with(PATH_TO_IMG_FILE)

    def test_it_should_create_a_thumbnail_with_the_configured_size(self):
        self.__run_img_test()
        args, _ = self.mock_image_file.thumbnail.call_args
        self.assertTrue((DEFAULT_THUMBNAIL_SIZE, DEFAULT_THUMBNAIL_SIZE) in args)

    def test_it_should_make_sure_that_the_thumbnail_directory_exists(self):
        self.mock_isdir.return_value = False
        self.__run_img_test()
        self.mock_util.mkdirp.assert_called_once_with('/haystack/thumbs')

    def test_it_should_save_the_thumbnail_to_the_right_place(self):
        self.__run_img_test()
        self.mock_image_file.save.assert_called_once_with(PATH_TO_IMG_THUMBNAIL)

    def test_it_should_use_the_configured_thumbnail_size(self):
        self.mock_config.thumbnail_size.return_value = 196

        self.__run_img_test()
        args, _ = self.mock_image_file.thumbnail.call_args
        self.assertTrue((196, 196) in args)

    def test_it_should_get_video_thumbnails_using_the_right_ffmpeg_command(self):
        self.__run_video_test()
        expected_cmd = ['ffmpeg', '-y', '-i', PATH_TO_VIDEO_FILE, '-vframes', '1', '-ss', '0', '-vf',
                        'scale=\'if(gte(iw,ih),128,-1)\':\'if(gte(iw,ih),-1,128)\'', PATH_TO_VIDEO_THUMBNAIL]
        self.mock_executor.execute.assert_called_once_with(expected_cmd)

    def test_it_should_respect_the_configured_thumbnail_size_for_videos(self):
        self.mock_config.thumbnail_size.return_value = 196

        self.__run_video_test()
        expected_cmd = ['ffmpeg', '-y', '-i', PATH_TO_VIDEO_FILE, '-vframes', '1', '-ss', '0', '-vf',
                        'scale=\'if(gte(iw,ih),196,-1)\':\'if(gte(iw,ih),-1,196)\'', PATH_TO_VIDEO_THUMBNAIL]
        self.mock_executor.execute.assert_called_once_with(expected_cmd)

    def test_it_should_raise_an_error_for_non_media_files(self):
        with self.assertRaises(RuntimeError):
            self.test_model.generate_thumbnail('bogus.txt', 'doesnt-matter.txt')
