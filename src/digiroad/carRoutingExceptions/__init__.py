class NotMultiPointGeometryException(Exception):
    def __init__(self, message):
        super(NotMultiPointGeometryException, self).__init__(message)


class FileNotFoundException(Exception):
    pass


class NotURLDefinedException(Exception):
    pass


class NotWFSDefinedException(Exception):
    pass
