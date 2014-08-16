from stiny.exceptions import InvalidConfig
from copy import copy, deepcopy

from ConfigParser import ConfigParser, SafeConfigParser
from voluptuous import Schema, Required, Optional, All, In, Invalid, Coerce, MultipleInvalid
from boto.s3 import regions as s3_regions


def _template_value(value):
    """
    Validation function for template type in configuration schema
    :param value: The configured template value
    :type value: str
    :return: True or False based on validity
    """
    if not isinstance(value, (str, unicode)):
        raise Invalid("Template values must be strings")
    else:
        if value.startswith("CANNED:") or value.startswith("FILE:"):
            return value
        else:
            raise Invalid("Template values must start with 'CANNED:' or 'FILE:' and be the name of a canned template" +
                          " in stiny.templates or the path to a jinja2 template")


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
    SUPPORTED_STORAGE = ['s3']
    S3_REGIONS = [region.name for region in s3_regions()]

    CONFIG_SCHEMA = Schema(
        {Required("main"): {
            Required("root_domain_name"): Coerce(str),
            Required("template"): All(Coerce(str), _template_value),
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

    _ALLOWED_SCHEMA_OPTIONS = {section.schema: [option.schema for option in CONFIG_SCHEMA[section]]
                               for section in CONFIG_SCHEMA.schema}

    def __init__(self, configuration):
        try:
            if isinstance(configuration, ConfigParser):
                self._configuration = StinyConfiguration.CONFIG_SCHEMA(self._configparser_to_dict(configuration))
            elif isinstance(configuration, file):
                p = SafeConfigParser()
                p.readfp(configuration)
                self._configuration = StinyConfiguration.CONFIG_SCHEMA(self._configparser_to_dict(p))
            elif isinstance(configuration, dict):
                self._configuration = StinyConfiguration.CONFIG_SCHEMA(deepcopy(configuration))
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

        config_parser = SafeConfigParser()

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
        return copy(self._configuration[section][option])

    def set(self, section, option, value=None):
        allowed_option = section in self._ALLOWED_SCHEMA_OPTIONS and option in self._ALLOWED_SCHEMA_OPTIONS[section]

        if allowed_option:
            if isinstance(value, dict):
                raise TypeError("Option values cannot be dictionaries")
            elif isinstance(value, (list, tuple, set)):
                value = ','.join(value)

            self._configuration[section][option] = copy(value)
        else:
            raise MultipleInvalid("Section:{} and Option:{} not valid on Config Schema".format(section, option))

    def sections(self):
        return deepcopy(self._configuration.keys())

    def options(self, section):
        return deepcopy(self._configuration[section].keys())


