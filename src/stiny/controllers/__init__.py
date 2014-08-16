"""Controllers are the heavy-lifing mechanisms of Stiny. They manipuldate the backing stores and create a standard
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
        # Put the tinyURL to the backing store
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
            TinyUrlDoesNotExistException,
            FailedTinyActionError) as e:
        print e.message

All controllers support these basic methods, with additional methods documented in the section for the specific
controller
"""

from abc import ABCMeta, abstractmethod
from jinja2 import Template
from ..url import URL


class Controller(object):
    """
    The abstract base class for the controller of a backing store. This class does not actually impliment any
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

    def __init__(self, template, prefix_separator=".", initial_tiny_length=4, max_retries=5, overwrite=False):
        self.prefix_separator = prefix_separator
        self.initial_tiny_length = initial_tiny_length
        self.max_retries = max_retries
        self.overwrite = overwrite
        self._template = None
        self.template = template

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
        Put the tiny url to the backing store.

        If the tiny_text is provided in the url, it will be used (and overwritten is specified)
        Otherwise, it will attempt to generate non-conflicting tiny text up to max_retries times.
        Often, with large number of tiny_urls we see failure counts increase, in which case the initial_tiny_length
        should be increased to increase the namespace

        :param url: the stiny.utl.StaticURL to be generated
        :raises: TooManyNameCollisions - if we're unable to autogenerate a tiny_text name
        :raises: TinyURLExistsException - if the provided tiny exists and we're not overwriting
        :raises: FailedTinyActionError - if the backing store fails to complete the put
        """
        pass

    @abstractmethod
    def delete(self, url):
        """
        Delete the tiny url from the backing store.

        :param url: the stiny.utl.StaticURL to be deleted (tiny_text must be provided) or str of tiny_text
        :raises: TinyURLDoesNotExistsException - if the provided tiny does not exist
        :raises: FailedTinyActionError - if the backing store fails to delete
        """
        pass

    @abstractmethod
    def list(self):
        """
        List the tiny urls in the backing store (should not list non-tinys) in the object store

        :return: Generator of stiny.url.URLs
        :raises: FailedTinyActionError - if the backing store fails to list
        """
        for x in xrange(10):
            yield (x, x)

    @abstractmethod
    def exists(self, url):
        """
        Check to see if the tiny_url specified exists

        :param url: the stiny.utl.StaticURL to be checked (tiny_text must be provided) or str of tiny_text
        :return: Boolean of existence
        :raises: FailedTinyActionError - if the backing store fails the query
        """
        pass

    @abstractmethod
    def validate(self, url):
        """
        Check to see if the tiny_url specified exists and points to the correct href

        :param url: the stiny.utl.StaticURL to validate
        :return: Boolean of validity, nonexistance is considered nonvalid.
        :raises: FailedTinyActionError - if the backing store fails the query
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
