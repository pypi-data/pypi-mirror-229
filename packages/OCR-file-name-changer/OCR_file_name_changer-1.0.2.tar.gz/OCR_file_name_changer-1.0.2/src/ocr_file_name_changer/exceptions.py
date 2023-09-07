class IncorrectImageException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class DuplicateSNException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
