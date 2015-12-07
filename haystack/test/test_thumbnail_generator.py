import mock
import unittest

from config import Config
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

        self.mock_image = patch('thumbnail_generator.Image').start()
        self.mock_image.open.return_value = self.mock_image_file

        self.mock_ffvideo = patch('thumbnail_generator.ffvideo').start()
        self.mock_video_stream = MagicMock()
        self.mock_ffvideo.VideoStream.return_value = self.mock_video_stream

        self.mock_video_frame = MagicMock()
        self.mock_video_stream.get_frame_at_sec.return_value = self.mock_video_frame

        self.mock_video_frame_img = MagicMock()
        self.mock_video_frame.image.return_value = self.mock_video_frame_img

        self.mock_config = MagicMock(spec=Config)
        self.mock_config.thumbnail_size.return_value = DEFAULT_THUMBNAIL_SIZE

        self.mock_util = MagicMock(spec=Util)

        self.test_model = ThumbnailGenerator(self.mock_config, self.mock_util)

    def tearDown(self):
        self.mock_isdir_patcher.stop()

    def __run_img_test(self):
        self.test_model.generate_thumbnail(PATH_TO_IMG_FILE, PATH_TO_IMG_THUMBNAIL)
        self.mock_ffvideo.VideoStream.assert_not_called()

    def __run_video_test(self):
        self.test_model.generate_thumbnail(PATH_TO_VIDEO_FILE, PATH_TO_VIDEO_THUMBNAIL)
        self.mock_image_file.open.assert_not_called()

    def test_it_should_open_the_right_file(self):
        self.__run_img_test()
        self.mock_image.open.assert_called_once_with(PATH_TO_IMG_FILE)

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

    def test_it_should_open_the_right_file_for_videos(self):
        self.__run_video_test()
        self.mock_ffvideo.VideoStream.assert_called_once_with(PATH_TO_VIDEO_FILE, frame_size=ANY, frame_mode=ANY)

    def test_it_should_open_videos_with_the_right_frame_size(self):
        self.__run_video_test()
        self.mock_ffvideo.VideoStream.assert_called_once_with(ANY, frame_size=(128, None), frame_mode=ANY)

    def test_it_should_open_videos_using_the_configured_thumbnail_size(self):
        self.mock_config.thumbnail_size.return_value = 256

        self.__run_video_test()
        self.mock_ffvideo.VideoStream.assert_called_once_with(ANY, frame_size=(256, None), frame_mode=ANY)

    def test_it_should_open_videos_with_the_right_frame_mode(self):
        self.__run_video_test()
        self.mock_ffvideo.VideoStream.assert_called_once_with(ANY, frame_size=ANY, frame_mode='RGB')

    def test_it_should_save_the_first_frame_of_the_video_as_a_thumbnail(self):
        self.__run_video_test()
        self.mock_video_stream.get_frame_at_sec.assert_called_once_with(0)
        self.mock_video_frame_img.save.assert_called_once_with(PATH_TO_VIDEO_THUMBNAIL)

    def test_it_should_raise_an_error_for_non_media_files(self):
        with self.assertRaises(RuntimeError):
            time = self.test_model.generate_thumbnail('bogus.txt', 'doesnt-matter.txt')
