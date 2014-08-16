__author__ = 'eflee'


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


class UnableToAutogenerateTinyText(Exception):
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


class CannedTemplateNotFoundException(Exception):
    """
    Raised if a canned template is provided in config and cannot be found
    """
    pass


class InvalidConfig(Exception):
    """
    Raised if the config provided is not valid
    """
    pass


class MalFormedTemplateConfig(Exception):
    """
    Raised if the template config value provided is not valid (e.g. doesn't start with FILE: or CANNED:)
    """
    pass


class UnknownStorageTypeException(Exception):
    """
    Raised if a backing store is provided in the Global config that is unrecognized
    """
    pass

