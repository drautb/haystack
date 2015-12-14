class MTPObject:
    def __init__(self, id, name, parent_id=None, size=None):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.size = size

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        try:
            return self.id == other.id and \
                   self.name == other.name and \
                   self.parent_id == other.parent_id and \
                   self.size == other.size
        except AttributeError:
            return False
