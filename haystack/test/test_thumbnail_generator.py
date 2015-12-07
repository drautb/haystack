import mock
import unittest

from config import Config
from metadata_extractor import MetadataExtractor
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

        self.mock_metadata_extractor = MagicMock(spec=MetadataExtractor)
        self.mock_metadata_extractor.get_rotation.return_value = 0

        self.test_model = ThumbnailGenerator(self.mock_config, self.mock_util, self.mock_metadata_extractor)

    def tearDown(self):
        self.mock_isdir_patcher.stop()
        self.mock_image_open_patcher.stop()

    def __run_img_test(self):
        self.test_model.generate_thumbnail(PATH_TO_IMG_FILE, PATH_TO_IMG_THUMBNAIL)
        self.mock_ffvideo.VideoStream.assert_not_called()

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

    def test_it_should_rotate_video_thumbnails_by_270_if_the_rotation_is_90(self):
        self.mock_metadata_extractor.get_rotation.return_value = 90
        self.__run_video_test()
        self.mock_video_frame_img.transpose.assert_called_once_with(Image.ROTATE_270)

    def test_it_should_rotate_video_thumbnails_by_180_if_the_rotation_is_180(self):
        self.mock_metadata_extractor.get_rotation.return_value = 180
        self.__run_video_test()
        self.mock_video_frame_img.transpose.assert_called_once_with(Image.ROTATE_180)

    def test_it_should_rotate_video_thumbnails_by_90_if_the_rotation_is_270(self):
        self.mock_metadata_extractor.get_rotation.return_value = 270
        self.__run_video_test()
        self.mock_video_frame_img.transpose.assert_called_once_with(Image.ROTATE_90)

    def test_it_should_not_rotate_video_thumbnails_if_the_rotation_is_0(self):
        self.__run_video_test()
        self.mock_video_frame_img.transpose.assert_not_called()

    def test_it_should_raise_an_error_if_the_rotation_is_not_0_90_180_or_270(self):
        with self.assertRaises(RuntimeError):
            self.mock_metadata_extractor.get_rotation.return_value = 1
            self.__run_video_test()

    def test_it_should_raise_an_error_for_non_media_files(self):
        with self.assertRaises(RuntimeError):
            self.test_model.generate_thumbnail('bogus.txt', 'doesnt-matter.txt')
