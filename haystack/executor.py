import subprocess


class Executor:
    def execute(self, args):
        return subprocess.check_call(args)
