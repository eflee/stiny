__author__ = 'eflee'


class UnknownBackingStoreException(Exception):
    """
    Raised when the configured backing stor eis unrecognized
    """
    pass


class FailedTinyActionError(Exception):
    pass


class InvalidTinyTextException(Exception):
    """
    Raised when the tiny text targeted is not lowercase letters
    """
    pass


class InvalidURLException(Exception):
    """
    Raised when the url provided is not encodeable
    """
    pass


class TooManyNameCollisions(Exception):
    """
    Raised if we're unable to autogenerate a tiny_text name
    """
    pass


class TinyURLExistsException(Exception):
    """
    Raised if the provided tiny exists and we're not overwriting
    """
    pass


class TinyUrlDoesNotExistException(Exception):
    """
    Raised if the provided tiny does not exist
    """
    pass
