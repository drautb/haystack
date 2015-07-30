import unittest
import errno

from mock import patch
from util import Util

TEST_PATH = '/test/path'


class TestUtil(unittest.TestCase):
    def setUp(self):
        self.mock_makedirs = patch('os.makedirs').start()
        self.mock_isdir = patch('os.path.isdir').start()

        self.test_model = Util()

    def test_mkdirp_should_create_a_directory_if_it_doesnt_exist(self):
        self.test_model.mkdirp(TEST_PATH)
        self.mock_makedirs.assert_called_once_with(TEST_PATH)

    def test_mkdirp_should_continue_if_the_directory_already_exists(self):
        self.mock_makedirs.side_effect = OSError(errno.EEXIST, 'test')
        self.mock_isdir.return_value = True
        self.test_model.mkdirp(TEST_PATH)

    def test_mkdirp_should_blow_up_if_the_path_is_actually_a_file(self):
        self.mock_makedirs.side_effect = OSError(errno.EEXIST, 'test')
        self.mock_isdir.return_value = False
        with self.assertRaises(OSError):
            self.test_model.mkdirp(TEST_PATH)


if __name__ == '__main__':
    unittest.main()
