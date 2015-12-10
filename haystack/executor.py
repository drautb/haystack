import logging
import subprocess


class Executor:
    def execute(self, args):
        logging.info('Executing command. args=%s', str(args))
        return subprocess.check_call(args)
