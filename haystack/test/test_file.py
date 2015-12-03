import unittest

from file import File


class TestFile(unittest.TestCase):
    def setUp(self):
        return

    def test_it_should_tell_the_truth_about_jpg_files(self):
        test_file = File('/path/to/file.jpg')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.media_type(), 'JPG')

    def test_it_should_tell_the_truth_about_JPG_files(self):
        test_file = File('/path/to/file.JPG')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.media_type(), 'JPG')

    def test_it_should_tell_the_truth_about_jpeg_files(self):
        test_file = File('/path/to/file.jpeg')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.media_type(), 'JPEG')

    def test_it_should_tell_the_truth_about_JPEG_files(self):
        test_file = File('/path/to/file.JPEG')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.media_type(), 'JPEG')

    def test_it_should_tell_the_truth_about_mp4_files(self):
        test_file = File('/path/to/file.mp4')
        self.assertFalse(test_file.is_image())
        self.assertTrue(test_file.is_video())
        self.assertEqual(test_file.media_type(), 'MP4')

    def test_it_should_tell_the_truth_about_MP4_files(self):
        test_file = File('/path/to/file.MP4')
        self.assertFalse(test_file.is_image())
        self.assertTrue(test_file.is_video())
        self.assertEqual(test_file.media_type(), 'MP4')


if __name__ == '__main__':
    unittest.main()
