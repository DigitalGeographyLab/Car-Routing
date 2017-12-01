class NotOSMURLGivenException(Exception):
    pass


class NotPathException(Exception):
    pass


class NotParameterGivenException(Exception):
    """
    Thrown when some paramenters have not been given.
    """

    def __init__(self, message):
        super(NotParameterGivenException, self).__init__(message)