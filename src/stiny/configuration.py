"""
Provides a mechanism for validating the configuration file in a complete and verifiable manner. The primary object, \
StinyConfiguration, is a ConfigParser-like object which uses an internal dict, voluptuous schema and ConfigParser \
to facilitate reading, wrtiing and persisting configuration options while ensureing that no invalid configration \
option is set or persisted.
"""

from copy import copy as _copy, deepcopy as _deepcopy
from ConfigParser import ConfigParser, SafeConfigParser

from voluptuous import Schema, Required, Optional, All, In, Invalid, Coerce, MultipleInvalid
from boto.s3 import regions as _s3_regions

from stiny.exceptions import InvalidConfig, UnknownConfigError
from stiny.templates import valid_template_value


def _string_list_split(value):
    """
    Splits a comma delimited string into a list
    :param value: A comma delimited list as a string
    :type value: str
    :return: list
    """
    try:
        return value.split(',')
    except AttributeError:
        raise Invalid("Must be of type str or unicode")


class StinyConfiguration(object):
    """
    This object support and validates the configutation file Schema. It behaves mostly like a ConfigParser object, but \
    uses voluptuous to create a schema and validates against the schema on set and write.
    """
    SUPPORTED_STORAGE = ['s3']
    S3_REGIONS = [region.name for region in _s3_regions()]

    _CONFIG_SCHEMA = Schema(
        {Required("main"): {
            Required("root_domain_name"): Coerce(str),
            Required("template"): All(Coerce(str), valid_template_value),
            Required("storage"): In(SUPPORTED_STORAGE),
            Required("min_length", default=3): Coerce(int),
            Required("max_retries", default=5): Coerce(int),
            Optional("expirations"): _string_list_split},
         Optional("s3"): {
             Required("region"): All(Coerce(str), In(S3_REGIONS)),
             Required("bucket_name"): Coerce(str),
             Required("aws_access_key_id"): Coerce(str),
             Required("aws_secret_access_key"): Coerce(str)}
         })

    def __init__(self, configuration):
        """
        Parses the configuraiton file for validity and returns a ConfigParser like object which support set and get \
        among other common methods
        :param configuration: The ConfigParser, file, or dict representing the configuration
        :type configuration: ConfigParser, file, or dict
        :raises MultipleInvalid: If the config does not validate against the defined schema
        """
        try:
            if isinstance(configuration, ConfigParser):
                self._configuration = StinyConfiguration._CONFIG_SCHEMA(self._configparser_to_dict(configuration))
            elif isinstance(configuration, file):
                p = SafeConfigParser()
                p.readfp(configuration)
                self._configuration = StinyConfiguration._CONFIG_SCHEMA(self._configparser_to_dict(p))
            elif isinstance(configuration, dict):
                self._configuration = StinyConfiguration._CONFIG_SCHEMA(_deepcopy(configuration))
        except MultipleInvalid as e:
            raise InvalidConfig(e.msg)

    @staticmethod
    def _configparser_to_dict(config_parser):
        """
        Parses a ConfigParser object into a dict to evaluate against a Voluptuous schema.

        :param config_parser: The configparser object
        :type config_parser: ConfigParser
        :returns dict: Dict representing a config
        """

        config_dict = dict()

        for section in config_parser.sections():
            config_dict[section] = dict()
            for option in config_parser.options(section):
                config_dict[section][option] = config_parser.get(section, option)

        return config_dict

    @staticmethod
    def _dict_to_configparser(config_dict):
        """
        Parses a config dict into a ConfigParser object

        :param config_dict: The configuration as a dictionary
        :type config_dict: dict
        :returns ConfigParser: A populated ConfigParser object from the config_dict

        .. note::
        Config dictionaries must be a maximum of two levels nested. The first level is the section and the second the \
        option:value pair
        """

        config_parser = SafeConfigParser(allow_no_value=True)

        for section in config_dict:
            config_parser.add_section(section)
            for option in config_dict[section]:
                value = config_dict[section][option]
                if isinstance(value, (list, set, tuple)):
                    value = ','.join(value)
                else:
                    value = str(value)
                config_parser.set(section, option, value)
        return config_parser

    def get(self, section, option):
        """
        Gets the option from the config

        :param section: The section the config option is in, e.g. "main" or "s3"
        :param option: The name of the option
        :raises UnknownConfigError: If the section and option are not found
        :returns: string, int or list for the option value
        """
        try:
            return _copy(self._configuration[section][option])
        except KeyError:
            raise UnknownConfigError("{}/{} cannot be found in config".format(section, option))

    def set(self, section, option, value=None):
        """
        Sets the option value in the provided section
        :param section: The section the config option is in, e.g. "main" or "s3"
        :type section: str
        :param option: The name of the option
        :type option: str
        :param value: The value to be set as the config option
        :type value: Iterable (non-dict) or autoboxable to str
        :raises MultipleInvalid: If the desited section and option are not valid in the cnofig Schema
        """
        _ALLOWED_SCHEMA_OPTIONS = {section.schema: [option.schema for option in self._CONFIG_SCHEMA.schema[section]]
                                   for section in self._CONFIG_SCHEMA.schema}
        allowed_option = section in _ALLOWED_SCHEMA_OPTIONS and option in _ALLOWED_SCHEMA_OPTIONS[section]

        if allowed_option:
            if isinstance(value, dict):
                raise TypeError("Option values cannot be dictionaries")
            elif isinstance(value, (list, tuple, set)):
                value = ','.join(value)

            self._configuration[section][option] = _copy(value)
        else:
            raise MultipleInvalid("Section:{} and Option:{} not valid on Config Schema".format(section, option))

    def sections(self):
        """
        Returns a list of sections from the config
        :return: list(str)
        """
        return _deepcopy(self._configuration.keys())

    def options(self, section):
        """
        Returns a list of option names for the section in the config
        :param section: The name of the section, e.g. "main" or "s3"
        :type section: str
        :return: list(str)
        """
        return _deepcopy(self._configuration[section].keys())

    def write(self, fp):
        """
        Persists the config to a file pointer
        :param fp: The file pointer into which the config should be persisted
        :type fp: file
        :raises MultipleInvalid: If the stored configuration is not valid in the embedded schema
        """
        self._CONFIG_SCHEMA(self._configuration)
        config_parser = self._dict_to_configparser(self._configuration)
        config_parser.write(fp)

    @property
    def config_schema(self):
        """
        Provides a one way accessor for the CONFIG_SCHEMA using a deepcopy so it is not mutable
        :returns dict: The Voluptuous Schema
        """
        return _deepcopy(self._CONFIG_SCHEMA)