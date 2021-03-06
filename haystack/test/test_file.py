import unittest

from file import File


class TestFile(unittest.TestCase):
    def setUp(self):
        return

    def test_it_should_blow_up_if_the_file_isnt_recognized(self):
        with self.assertRaises(RuntimeError):
            File('bogus.txt')

    def test_it_should_tell_the_truth_about_jpg_files(self):
        test_file = File('/path/to/file.jpg')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.jpg')
        self.assertEqual(test_file.ext(), '.jpg')
        self.assertEqual(test_file.media_type(), 'JPG')
        self.assertEqual(test_file.date_taken_tag(), 'EXIF:DateTimeOriginal')
        self.assertEqual(test_file.rotation_tag(), 'EXIF:Orientation')

    def test_it_should_tell_the_truth_about_JPG_files(self):
        test_file = File('/path/to/file.JPG')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.JPG')
        self.assertEqual(test_file.ext(), '.jpg')
        self.assertEqual(test_file.media_type(), 'JPG')
        self.assertEqual(test_file.date_taken_tag(), 'EXIF:DateTimeOriginal')
        self.assertEqual(test_file.rotation_tag(), 'EXIF:Orientation')

    def test_it_should_tell_the_truth_about_jpeg_files(self):
        test_file = File('/path/to/file.jpeg')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.jpeg')
        self.assertEqual(test_file.ext(), '.jpeg')
        self.assertEqual(test_file.media_type(), 'JPEG')
        self.assertEqual(test_file.date_taken_tag(), 'EXIF:DateTimeOriginal')
        self.assertEqual(test_file.rotation_tag(), 'EXIF:Orientation')

    def test_it_should_tell_the_truth_about_JPEG_files(self):
        test_file = File('/path/to/file.JPEG')
        self.assertTrue(test_file.is_image())
        self.assertFalse(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.JPEG')
        self.assertEqual(test_file.ext(), '.jpeg')
        self.assertEqual(test_file.media_type(), 'JPEG')
        self.assertEqual(test_file.date_taken_tag(), 'EXIF:DateTimeOriginal')
        self.assertEqual(test_file.rotation_tag(), 'EXIF:Orientation')

    def test_it_should_tell_the_truth_about_mp4_files(self):
        test_file = File('/path/to/file.mp4')
        self.assertFalse(test_file.is_image())
        self.assertTrue(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.mp4')
        self.assertEqual(test_file.ext(), '.mp4')
        self.assertEqual(test_file.media_type(), 'MP4')
        self.assertEqual(test_file.date_taken_tag(), 'QuickTime:CreateDate')
        self.assertEqual(test_file.rotation_tag(), 'Composite:Rotation')

    def test_it_should_tell_the_truth_about_MP4_files(self):
        test_file = File('/path/to/file.MP4')
        self.assertFalse(test_file.is_image())
        self.assertTrue(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.MP4')
        self.assertEqual(test_file.ext(), '.mp4')
        self.assertEqual(test_file.media_type(), 'MP4')
        self.assertEqual(test_file.date_taken_tag(), 'QuickTime:CreateDate')
        self.assertEqual(test_file.rotation_tag(), 'Composite:Rotation')

    def test_it_should_tell_the_truth_about_mts_files(self):
        test_file = File('/path/to/file.mts')
        self.assertFalse(test_file.is_image())
        self.assertTrue(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.mts')
        self.assertEqual(test_file.ext(), '.mts')
        self.assertEqual(test_file.media_type(), 'MTS')
        self.assertEqual(test_file.date_taken_tag(), 'H264:DateTimeOriginal')
        self.assertEqual(test_file.rotation_tag(), 'Composite:Rotation')

    def test_it_should_tell_the_truth_about_MTS_files(self):
        test_file = File('/path/to/file.MTS')
        self.assertFalse(test_file.is_image())
        self.assertTrue(test_file.is_video())
        self.assertEqual(test_file.filename(), '/path/to/file.MTS')
        self.assertEqual(test_file.ext(), '.mts')
        self.assertEqual(test_file.media_type(), 'MTS')
        self.assertEqual(test_file.date_taken_tag(), 'H264:DateTimeOriginal')
        self.assertEqual(test_file.rotation_tag(), 'Composite:Rotation')


if __name__ == '__main__':
    unittest.main()
