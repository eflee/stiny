"""
Defines the exception classes used throughut the stiny code for convenient reference.
"""

__author__ = 'eflee'


class FailedTinyActionError(Exception):
    """
    Generic exception used to encapsulate the errors from the storage client
    """
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


class MalformedTemplateConfig(Exception):
    """
    Raised if the template config string if not valid, i.e. starts with "CANNED:" or "FILE:"
    """
    pass


class TemplateNotFoundException(Exception):
    """
    Raised if a canned template is provided in config and cannot be found
    """
    pass


class InvalidConfig(Exception):
    """
    Raised if the config provided is not valid
    """
    pass


class UnknownConfigError(Exception):
    """
    Raise if the requsted configuration values are not set
    """
    pass


class UnsupportedStorageTypeException(Exception):
    """
    Raised if the storage type configured is not supported
    """
    pass
