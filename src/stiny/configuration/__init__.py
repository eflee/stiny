import stiny.templates
from stiny.exceptions import CannedTemplateNotFoundException, MalFormedTemplateConfig
from os.path import expanduser, exists
from copy import copy

SUPPORTED_BACKING_STORES = ['s3']


class GlobalConfiguration(object):
    CONFIG_SECTION_NAME = 'MAIN'
    _configurables = ['domain_name', 'store_type', 'template_config', 'min_length', 'max_retries']


    def __init__(self, domain_name, store_type, template_config="CANNED:META_REDIRECT_NO_BODY",
                 min_length=3, max_retries=5):
        """
        This is the class supporting the global configuration section of the Stiny configuration.

        :param str domain_name: The root domain name of the website used for TinyURLs
        :param str store_type: The backing store type.
        :param str template_config: The template to render the supporting tiny object. This can either start with 'CANNED:' \
        and then reference a template in stiny.templates or 'FILE:' and then a filesystem location of a jinja2 template
        :param int min_length: The minimum length of the tiny uri
        :param int max_retries: The max number of attempts to autogenerate the random tiny uri
        """

        self.domain_name = domain_name

        if store_type in SUPPORTED_BACKING_STORES:
            self.store_type = store_type
        else:
            raise UnknownStorageTypeException('{} is not a supported storage type'.format(store_type))
        self.template_config = template_config
        self.template = self.load_template(template_config)
        self.min_length = min_length
        self.max_retries = max_retries

    @classmethod
    def load_template(cls, template):
        if template.startswith("CANNED:"):
            return cls._load_canned_template(template)
        elif template.startswith("FILE:"):
            return cls._load_template_from_file(template)
        else:
            raise MalFormedTemplateConfig('{} not valid template config value')

    @staticmethod
    def _load_canned_template(template):
        template_name = template.split(':')[1]
        if template_name not in stiny.templates.__dict__:
            raise CannedTemplateNotFoundException("{} not found in stiny.templates".format(template_name))
        else:
            return stiny.templates.__dict__[template_name]

    @staticmethod
    def _load_template_from_file(template):
        template_file = expanduser(template.split(':')[1])
        if exists(template_file):
            return open(template_file).read()

    def to_dict(self):
        configuration = dict()
        for config_key in self._configurables:
            configuration[copy(config_key)] = copy(getattr(self, config_key))
        return configuration
