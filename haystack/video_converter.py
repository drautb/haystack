import logging

from datetime import datetime
from executor import Executor
from subprocess import CalledProcessError

FFMPEG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
SPACE = ' '


class VideoConverter:
    def __init__(self, executor=None):
        if executor is None:
            executor = Executor()

        self.executor = executor

    def convert_to_mp4(self, path_to_input, path_to_output, create_time):
        create_time_str = datetime.utcfromtimestamp(create_time).strftime(FFMPEG_DATE_FORMAT)
        cmd_list = ['ffmpeg', '-i', path_to_input, '-threads', '16', '-f', 'mp4',
                    '-metadata', 'creation_time=' + create_time_str, path_to_output]

        try:
            self.executor.execute(cmd_list)
        except CalledProcessError as e:
            logging.exception('An error occurred while converting this video. path_to_input=%s path_to_output=%s ' +
                              'create_time=%s create_time_str=%s cmd="%s"', path_to_input, path_to_output, create_time,
                              create_time_str, SPACE.join(cmd_list))
            raise RuntimeError('An error occurred while converting a video to mp4!')
