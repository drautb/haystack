import os

IMAGE_EXTENSIONS = [
    '.jpg',
    '.jpeg'
]

VIDEO_EXTENSIONS = [
    '.mp4',
    '.mts'
]


class File:
    def __init__(self, path_to_file):
        self.path_to_file = path_to_file

        _, extension = os.path.splitext(self.path_to_file)
        self.extension = extension.lower()

        self.type = self.extension.upper().replace('.', '')

    def is_image(self):
        return self.extension in IMAGE_EXTENSIONS

    def is_video(self):
        return self.extension in VIDEO_EXTENSIONS

    def media_type(self):
        return self.type
