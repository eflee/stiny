"""
Defines the exception classes used throughut the stiny code for convenient reference.
"""

__author__ = 'eflee'


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


class ConfigNotFoundError(Exception):
    """
    Raised by the Stiny binary if the config file provided is not found
    """
    pass
