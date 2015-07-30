import os
import errno
import uuid


class Util:
    def mkdirp(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def get_uuid(self):
        return uuid.uuid4().hex
