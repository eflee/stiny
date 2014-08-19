"""Controllers are the heavy-lifing mechanisms of Stiny. They manipuldate storage and create a standard
interface for the Stiny cli and applications leveraging the Stiny library. Typically controllers are instantiated with
the template for the TinyURL HTML files (if necessary) and provide standard put, delete, list, validate and exists
methods.

Here is a code example if using a controller (in this case an S3Controller)::

    from stiny.controllers.s3 import S3Controller
    from stiny.templates import META_REDIRECT
    from stiny.url import URL
    from stiny.exceptions import *

    controller = S3Controller(template=META_REDIRECT,
                              bucket_name="my_bucket",
                              region="aws-region",  # e.g. us-standard, us-west-1, us-west-2
                              aws_access_key_id="AWSACCESSKEY",
                              aws_secret_access_key="AWSSECRETACCESSKEYAWSSECRETACCESSKEY")

    #Create the test URL
    url = URL(url="http://www.google.com/")

    try:
        # Put the tinyURL to storage
        controller.put(url)

        # Assert that it exists using the object
        assert(controller.exists(url))

        # Assert that it exists using the tiny_text (showing that it can be used either way)
        assert(controller.exists(url.get_tiny_uri()))

        # Assert that the url and the existing tiny are the same (valid)
        assert(controller.validate(url))

        # Get a generator of all tiny urls
        for t_url in controller.list():
            print t_url.url

        # Delete the url
        controller.delete(url)

    except (InvalidTinyTextException,
            InvalidURLException,
            TooManyNameCollisions,
            TinyURLExistsException,
            TinyUrlDoesNotExistException) as e:
        print e.message

All controllers support these basic methods, with additional methods documented in the section for the specific
controller
"""

from StringIO import StringIO
from abc import ABCMeta, abstractmethod

from jinja2 import Template

from stiny.exceptions import UnableToAutogenerateTinyText, TinyURLExistsException
from stiny.url import URL


__author__ = 'eflee'


class Controller(object):
    """
    The abstract base class for the controller of storage. This class does not actually impliment any
    functionality (other than the constructor) but rather sets the method contracts for the methods supported by all
    controllers.

    :param template: The template string or Template instance for the jinja2 template used to create the \
    contents of the tiny
    :type template: str or jinja2.Template
    :param str prefix_separator: The seperator between the prefix and tiny_text
    :param int initial_tiny_length: The length to try for autogenerating tiny text
    :param int max_retries: The max number if attempts to generate a unique tiny
    :param bool overwrite: Overwrite (if tiny text is provided)

    :ivar jinja2.Template template: The template used to generate the HTML of the tinyurl
    :ivar str prefix_separator: The separator betweek the prefix and tiny_text for any URL created by :func:`create_url`
    :ivar int initial_tiny_length: The initial length to attempt the auto_generated tiny_text, increased ny one for \
    each collision after the second.
    :ivar int max_retries: The maximum number of collisions that will be tolerated before raising an exception
    :ivar bool overwrite: Whether a duplicat (provided) tiny_text will overwrite \
    (otherwise raises :class:`TinyURLExistsException`)
    """
    __metaclass__ = ABCMeta

    def __init__(self, template, prefix_separator=".", tiny_length=4, max_retries=5, overwrite=False, analytics=None):
        self.prefix_separator = prefix_separator
        self.initial_tiny_length = tiny_length
        self.max_retries = max_retries
        self.overwrite = overwrite
        self._template = None
        self.template = template
        self.analytics = analytics

    @property
    def template(self):
        """
        The jinja2 template used to create the meta redirect

        :setter: Takes either a string (which is a valid Template) or jinja2.Template object
        :getter: Returns the jinja2.Template object
        :type: jinja2.Template
        """
        return self._template

    @template.setter
    def template(self, template):
        """
        Set the template

        :param template: The template the controller will use to generate the tinyURL
        :type template: str, jinja2.Template
        :raises; AttributeError
        """
        if isinstance(template, Template):
            self._template = template
        else:
            self.template = Template(template)

    @abstractmethod
    def put(self, url):
        """
        Put the tiny url to storage.

        If the tiny_text is provided in the url, it will be used (and overwritten is specified)
        Otherwise, it will attempt to generate non-conflicting tiny text up to max_retries times.
        Often, with large number of tiny_urls we see failure counts increase, in which case the initial_tiny_length
        should be increased to increase the namespace

        :param url: the stiny.utl.StaticURL to be generated
        :raises: TooManyNameCollisions - if we're unable to autogenerate a tiny_text name
        :raises: TinyURLExistsException - if the provided tiny exists and we're not overwriting
        """
        pass

    @abstractmethod
    def delete(self, url):
        """
        Delete the tiny url from storage.

        :param url: the stiny.utl.StaticURL to be deleted (tiny_text must be provided) or str of tiny_text
        :raises: TinyURLDoesNotExistsException - if the provided tiny does not exist
        """
        pass

    @abstractmethod
    def list(self):
        """
        List the tiny urls in storage (should not list non-tinys) in the object store

        :return: Generator of stiny.url.URLs
        """
        for x in xrange(10):
            yield (x, x)

    @abstractmethod
    def exists(self, url):
        """
        Check to see if the tiny_url specified exists

        :param url: the stiny.utl.StaticURL to be checked (tiny_text must be provided) or str of tiny_text
        :return: Boolean of existence
        """
        pass

    @abstractmethod
    def validate(self, url):
        """
        Check to see if the tiny_url specified exists and points to the correct href

        :param url: the stiny.utl.StaticURL to validate
        :return: Boolean of validity, nonexistance is considered nonvalid.
        """
        pass

    def create_url(self, *args, **kwargs):
        """
        A helper function used to create URL objects that will automaticaly pass in any persistant values set on the
        controller (like prefix_separator).

        See :py:class:`stiny.url.URL` documentation for available parameters.

        :raises: stiny.exception.InvalidURLException if the url is invalid
        :return: stiny.url.URL object
        """
        if 'prefix_seperator' not in kwargs:
            kwargs['prefix_separator'] = self.prefix_separator
        return URL(*args, **kwargs)

    def _select_tiny_text(self, url):
        """
        This method selects the tiny_text for the url by one of a number of methods. If the tiny text was provided \
        with the URL, it uses that and errors if it exists and overwrite it not set. Otherwise, it randomly generates \
        the tiny_text.
        """
        if not url.tiny_text_provided:
            retries = 0
            while url.tiny_text is None and retries < self.max_retries:
                url.tiny_text = url.generate_tiny_text(self.initial_tiny_length)
                if self.exists(url.get_tiny_uri()):
                    retries += 1
                    url.tiny_text = None

            if url.tiny_text is None:
                raise UnableToAutogenerateTinyText(
                    "Unable to generate tiny name, increase retries or increase key start length or provide a name")

        else:
            if not self.overwrite and self.exists(url.get_tiny_uri()):
                raise TinyURLExistsException("{} already exists".format(url.get_tiny_uri()))

    def _get_contents_fp(self, url):
        """
        Returns a file pointer to the contents of the file using StringIO.
        :param url: The url to be encoded
        :type url: stiny.url.URL
        """

        contents = self._get_contents(url)
        sio = StringIO(contents)
        return sio

    def _get_contents(self, url):
        return "\n".join([line for line in self.template.generate(url=url, analytics=self.analytics)])
