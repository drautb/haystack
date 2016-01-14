import unittest

from executor import Executor
from mock import MagicMock
from subprocess import CalledProcessError
from video_converter import VideoConverter

PATH_TO_INPUT = '/haystack/input.mts'
PATH_TO_OUTPUT = '/haystack/output.mp4'
CREATE_TIME = 1447804800  # 2015-11-18 00:00:00 GMT


class TestVideoConverter(unittest.TestCase):
    def setUp(self):
        self.mock_executor = MagicMock(spec=Executor)
        self.mock_executor.execute.return_value = 0

        self.test_model = VideoConverter(self.mock_executor)

    def __run_test(self):
        self.test_model.convert_to_mp4(PATH_TO_INPUT, PATH_TO_OUTPUT, CREATE_TIME)

    def test_it_should_properly_form_the_shell_command(self):
        self.__run_test()
        self.mock_executor.execute.assert_called_once_with(['ffmpeg', '-y', '-i', PATH_TO_INPUT, '-threads', '16', '-f',
                                                            'mp4', '-metadata', 'creation_time=2015-11-18 00:00:00',
                                                            PATH_TO_OUTPUT])

    def test_it_should_raise_an_error_if_the_conversion_failed(self):
        self.mock_executor.execute.side_effect = CalledProcessError(1, 'cmd')
        with self.assertRaises(RuntimeError):
            self.__run_test()


if __name__ == '__main__':
    unittest.main()
