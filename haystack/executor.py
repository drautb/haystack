import logging
import subprocess


class Executor:
    def execute(self, args):
        logging.info('Executing command. args=%s', str(args))
        return subprocess.check_call(args)

    def execute_output(self, args):
        logging.info('Executing command and getting output. args=%s', str(args))
        output = subprocess.check_output(args)
        logging.info('Returning command output. args=%s output=%s', str(args), output)
        return output
