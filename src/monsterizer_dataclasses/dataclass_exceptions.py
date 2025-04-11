def InvalidTypeError(Exception):
    def __init__(self, message, type):
        super().__init__(message)
        self.type = type

    def str(self):
        return f"{self.message} for {self.type}"