import logging
import re

from executor import Executor

MANUFACTURER_REGEX = re.compile('   Manufacturer: (.*)')
MODEL_REGEX = re.compile('   Model: (.*)')
SERIAL_REGEX = re.compile('   Serial number: (.*)')

FOLDER_LINE_REGEX = re.compile('^(\d+)\t(\s*)(.*)')
SPACES_PER_LEVEL = 2

ID_KEY = 'id'
NAME_KEY = 'name'
SIZE_KEY = 'size'
PARENT_KEY = 'parent_id'
DEPTH_KEY = 'depth'

FILE_ID_REGEX = re.compile('^File ID: (\d+)')
FILE_NAME_REGEX = re.compile('^   Filename: (.*)')
FILE_SIZE_REGEX = re.compile('^   File size (\d+) .* bytes')
PARENT_ID_REGEX = re.compile('^   Parent ID: (\d+)')
STORAGE_ID_REGEX = re.compile('^   Storage ID: .*')
FILE_TYPE_REGEX = re.compile('^   Filetype: .*')


class MTPDriver:
    def __init__(self, executor=None):
        if executor is None:
            executor = Executor()

        self.executor = executor

    def detect_device(self):
        output = self.executor.execute_output('mtp-detect')
        if 'No raw devices found' in output:
            return False

        return {
            'manufacturer': MANUFACTURER_REGEX.search(output).group(1),
            'model': MODEL_REGEX.search(output).group(1),
            'serial': SERIAL_REGEX.search(output).group(1)
        }

    def get_folder_list(self):
        output = self.executor.execute_output('mtp-folders').split('\n')

        # Get rid of the frontmatter
        while not FOLDER_LINE_REGEX.match(output[0]):
            del output[0]

        # Get rid of the endmatter
        while not FOLDER_LINE_REGEX.match(output[-1]):
            del output[-1]

        folder_list = []
        current_depth = 0
        parents_stack = [None]
        last_id = 0
        for line in output:
            line_data = self.__parse_folder_line(line)
            folder_id = line_data[ID_KEY]
            folder_name = line_data[NAME_KEY]
            parent_id = None
            depth = line_data[DEPTH_KEY]

            if depth > current_depth:
                parents_stack.append(last_id)
            elif depth < current_depth:
                diff = current_depth - depth
                parents_stack = parents_stack[:-diff]

            parent_id = parents_stack[-1]
            current_depth = depth
            last_id = folder_id
            folder_list.append({ID_KEY: folder_id, NAME_KEY: folder_name, PARENT_KEY: parent_id})

        return folder_list

    def get_filelisting(self):
        output = self.executor.execute_output('mtp-files').split('\n')

        # Get rid of the frontmatter
        while not FILE_ID_REGEX.match(output[0]):
            del output[0]

        file_list = []
        current_file = {}
        for line in output:
            if FILE_ID_REGEX.match(line):
                current_file[ID_KEY] = int(FILE_ID_REGEX.search(line).group(1))
            elif FILE_NAME_REGEX.match(line):
                current_file[NAME_KEY] = FILE_NAME_REGEX.search(line).group(1)
            elif FILE_SIZE_REGEX.match(line):
                current_file[SIZE_KEY] = int(FILE_SIZE_REGEX.search(line).group(1))
            elif PARENT_ID_REGEX.match(line):
                current_file[PARENT_KEY] = int(PARENT_ID_REGEX.search(line).group(1))
                file_list.append(current_file)
                current_file = {}

        return file_list

    def get_file_to_file(self, id, dest_file):
        self.executor.execute(['mtp-getfile', str(id), dest_file])

    def delete_object(self, id):
        self.executor.execute(['mtp-delfile', '-n', str(id)])

    def __parse_folder_line(self, line):
        data = {}
        match_data = FOLDER_LINE_REGEX.search(line)

        data[ID_KEY] = int(match_data.group(1))
        data[DEPTH_KEY] = int(len(match_data.group(2)) / SPACES_PER_LEVEL)
        data[NAME_KEY] = match_data.group(3)

        return data
