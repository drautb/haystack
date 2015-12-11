import unittest

from metadata_helper import MetadataHelper
from mock import call
from mock import MagicMock
from mock import patch
from PIL import Image
from preprocessor import Preprocessor

# http://sylvana.net/jpegcrop/exif_orientation.html


class TestPreprocessor(unittest.TestCase):
    def setUp(self):
        self.mock_metadata_helper = MagicMock(spec=MetadataHelper)

        self.mock_image_open_patcher = patch('preprocessor.Image.open')
        self.mock_image_open = self.mock_image_open_patcher.start()

        self.mock_image = MagicMock()
        self.mock_exif_data = 'a bunch of exif data'
        self.mock_image.info = {
            'exif': self.mock_exif_data
        }
        self.mock_image_open.return_value = self.mock_image

        self.mock_first_transposed_image = MagicMock()
        self.mock_image.transpose.return_value = self.mock_first_transposed_image

        self.mock_second_transposed_image = MagicMock()
        self.mock_first_transposed_image.transpose.return_value = self.mock_second_transposed_image

        self.test_model = Preprocessor(self.mock_metadata_helper)

    def tearDown(self):
        self.mock_image_open_patcher.stop()

    def test_it_should_ignore_video_files(self):
        self.test_model.preprocess('/root/staging/USB/video.mp4')
        self.mock_image_open.assert_not_called()

    def test_it_should_not_touch_images_with_rotation_of_0(self):
        self.mock_metadata_helper.get_rotation.return_value = 0
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_not_called()
        self.mock_image.save.assert_called_once_with('/root/staging/USB/image.jpg', exif=self.mock_exif_data)

    def test_it_should_not_touch_images_with_rotation_of_1(self):
        self.mock_metadata_helper.get_rotation.return_value = 1
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_not_called()
        self.mock_image.save.assert_called_once_with('/root/staging/USB/image.jpg', exif=self.mock_exif_data)

    def test_it_should_flip_horizontally_an_image_with_a_rotation_of_2(self):
        self.mock_metadata_helper.get_rotation.return_value = 2
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_called_once_with(Image.FLIP_LEFT_RIGHT)
        self.mock_first_transposed_image.save.assert_called_once_with('/root/staging/USB/image.jpg',
                                                                      exif=self.mock_exif_data)

    def test_it_should_rotate_by_180_an_image_with_a_rotation_of_3(self):
        self.mock_metadata_helper.get_rotation.return_value = 3
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_called_once_with(Image.ROTATE_180)
        self.mock_first_transposed_image.save.assert_called_once_with('/root/staging/USB/image.jpg',
                                                                      exif=self.mock_exif_data)

    def test_it_should_flip_vertically_an_image_with_a_rotation_of_4(self):
        self.mock_metadata_helper.get_rotation.return_value = 4
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_called_once_with(Image.FLIP_TOP_BOTTOM)
        self.mock_first_transposed_image.save.assert_called_once_with('/root/staging/USB/image.jpg',
                                                                      exif=self.mock_exif_data)

    def test_it_should_rotate_by_270_and_flip_horizontally_an_image_with_a_rotation_of_5(self):
        self.mock_metadata_helper.get_rotation.return_value = 5
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_called_once_with(Image.FLIP_LEFT_RIGHT)
        self.mock_first_transposed_image.transpose.assert_called_once_with(Image.ROTATE_90)
        self.mock_second_transposed_image.save.assert_called_once_with('/root/staging/USB/image.jpg',
                                                                       exif=self.mock_exif_data)

    def test_it_should_rotate_by_270_an_image_with_a_rotation_of_6(self):
        self.mock_metadata_helper.get_rotation.return_value = 6
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_called_once_with(Image.ROTATE_270)
        self.mock_first_transposed_image.save.assert_called_once_with('/root/staging/USB/image.jpg',
                                                                      exif=self.mock_exif_data)

    def test_it_should_rotate_by_90_and_flip_horizontally_an_image_with_a_rotation_of_7(self):
        self.mock_metadata_helper.get_rotation.return_value = 7
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_called_once_with(Image.ROTATE_90)
        self.mock_first_transposed_image.transpose.assert_called_once_with(Image.FLIP_LEFT_RIGHT)
        self.mock_second_transposed_image.save.assert_called_once_with('/root/staging/USB/image.jpg',
                                                                       exif=self.mock_exif_data)

    def test_it_should_rotate_by_90_an_image_with_a_rotation_of_8(self):
        self.mock_metadata_helper.get_rotation.return_value = 8
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_image.transpose.assert_called_once_with(Image.ROTATE_90)
        self.mock_first_transposed_image.save.assert_called_once_with('/root/staging/USB/image.jpg',
                                                                      exif=self.mock_exif_data)

    def test_it_should_set_the_orientation_to_1_when_done(self):
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_metadata_helper.set_rotation.assert_called_once_with('/root/staging/USB/image.jpg', 1)

    def test_it_should_not_do_anything_if_the_image_is_missing_exif_data(self):
        self.mock_image.info = {}
        self.test_model.preprocess('/root/staging/USB/image.jpg')
        self.mock_metadata_helper.get_rotation.assert_not_called()


if __name__ == '__main__':
    unittest.main()
