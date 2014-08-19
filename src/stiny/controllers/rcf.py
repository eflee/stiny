import gzip
from StringIO import StringIO
from datetime import datetime

import pyrax
from pyrax.exceptions import NoSuchObject

from controller import Controller
from ..url import URL
from ..exceptions import TinyUrlDoesNotExistException, TinyURLExistsException


class CloudFilesController(Controller):
    """
    A controller for storage using an CloudFiles container website.

    Currently, the controller assumes the container exists, is configured as a website and has an expiration policy
    in place that supports the expiration rules of the StaticURLs
    """

    def __init__(self, container_name, region, rs_username, rs_api_key, compress=True, *args, **kwargs):
        """
        :param template: The template string or Template instance for the jinja2 template used to create the
        contents of the tiny
        :type template: str or jinja2.Template
        :param int tiny_length: The length to try for autogenerating tiny text
        :param int max_retries: The max number if attempts to generate a unique tiny
        :param boolean overwrite: Overwrite (if tiny text is provided)
        :param str container_name: The name of the CloudFiles website container
        :param str region: The CloudFiles region to connect to e.g. IAD, DFW
        :param str rs_username: The AWS Access Key Id to Authentication
        :param str rs_api_key: The AWS Access Key Id to Authentication
        """
        super(CloudFilesController, self).__init__(*args, **kwargs)

        pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_default_region(region)
        pyrax.set_credentials(rs_username, rs_api_key)

        self._container = pyrax.cloudfiles.get_container(container_name)
        self._compression = compress

    def get(self, tiny_uri):
        """
        Get the tiny url from storage.

        If the tiny_text is provided in the url, it will be used (and overwritten is specified)
        Otherwise, it will attempt to generate non-conflicting tiny text up to max_retries times.
        Often, with large number of tiny_urls we see failure counts increase, in which case the initial_tiny_length
        should be increased to increase the namespace

        :param tiny_uri: the name of the tiny url
        :raises: TinyURLDoesNotExistsException - if the provided tiny exists and we're not overwriting
        """
        try:
            object_ = pyrax.cloudfiles.get_object(self._container, tiny_uri)
            url = object_.get_metadata()["tiny_url"]
            last_modified = datetime.strptime(object_.last_modified, "%a, %d %b %Y %H:%M:%S %Z")
            surl = URL(url=url, tiny_text=tiny_uri, prefix_separator=self.prefix_separator, last_modified=last_modified)
            return surl
        except (KeyError, NoSuchObject):
            return TinyUrlDoesNotExistException("tiny url '{}' does not exist.".format(tiny_uri))

    def put(self, url):
        """
        Put the tiny url to storage.
        If the tiny_text is provided in the url, it will be used (and overwritten as specified)
        Otherwise, it will attempt to generate non-conflicting tiny text
        :param url: the url to be generated
        :type url: stiny.url.URL
        :raises TooManyNameCollisions: if we're unable to autogenerate a tiny_text name
        :raises TinyURLExistsException: if the provided tiny exists and we're not overwriting

        .. note::
        This method sets the necessary CloudFiles metadata to make CloudFiles website serve the object appropriately.
        Most notably, this sets Content-Type to text/html and Content-Encoding to gzip if compression is set.
        """

        if url.tiny_text is None:
            self._select_tiny_text(url)

        if not self.exists(url):
            object_name = url.get_tiny_uri()
            object_content_type = "text/html"
            object_content_encoding = 'gzip' if self._compression else None
            object_metadata = {'tiny_url': url.url}

            sio = self._get_contents_fp(url)
            pyrax.cloudfiles.create_object(self, self._container, file_or_path=sio, obj_name=object_name,
                                           content_type=object_content_type, content_encoding=object_content_encoding,
                                           metadata=object_metadata)
            sio.close()
            url.last_modified = datetime.now()
        else:
            raise TinyURLExistsException("{} already exists".format(url.tiny_text))

    def _get_contents_fp(self, url):
        """
        Returns a file pointer to the contents of the file using StringIO (and GzipFile).
        :param url: The url to be encoded
        :type url: stiny.url.URL
        """

        if self._compression:
            sio = StringIO()
            gio = gzip.GzipFile(
                filename=url.tiny_text, mode='wb', fileobj=sio)
            gio.write(super(CloudFilesController, self)._get_contents(url))
            gio.close()
            sio.seek(0)
        else:
            sio = super(CloudFilesController, self)._get_contents_fp(url)

        return sio

    def delete(self, url):
        """
        Delete the tiny url from storage.
        :param url: the stiny.utl.StaticURL to be deleted (tiny_text must be provided) or str of tiny_text
        :raises: TinyURLDoesNotExistsException - if the provided tiny does not exist
        """
        if isinstance(url, URL):
            url = url.get_tiny_uri()

        if self.exists(url):
            pyrax.cloudfiles.delete_object(self._container, 'url')
        else:
            raise TinyUrlDoesNotExistException("{} does not exist".format(url))

    def list(self):
        """
        List the tiny urls in storage (should not list non-tinys)
        :return: Generate of (tiny_text, destination_url)
        """

        for object_ in pyrax.cloudfiles.list_container_objects(self._container):
            try:
                url = object_.get_metadata()["tiny_url"]
                last_modified = datetime.strptime(object_.last_modified, "%a, %d %b %Y %H:%M:%S %Z")
                surl = URL(url=url, tiny_text=object_.name, prefix_separator=self.prefix_separator,
                           last_modified=last_modified)
                yield surl
            except KeyError:
                continue

    def exists(self, url):
        """
        Check to see if the tiny_url specified exists
        :param url: the stiny.url.StaticURL to be checked (tiny_text must be provided) or str of tiny_text
        :return: Boolean of existence
        """

        if isinstance(url, URL):
            url = url.get_tiny_uri()

        if url is None:
            return False
        else:
            try:
                pyrax.cloudfiles.get_object(self._container, url)
                return True
            except NoSuchObject:
                return False

    def validate(self, url):
        """
        Check to see if the tiny_url specified exists and points to the correct href
        :param url: the stiny.utl.StaticURL to validate
        :return: Boolean of validity
        """

        # reimplementing exists functionality to save on head call
        try:
            object_ = pyrax.cloudfiles.get_object(self._container, url.get_tiny_uri())
            return object_.get_metadata()['tiny_url'] == url.url
        except (NoSuchObject, KeyError):
            return False

