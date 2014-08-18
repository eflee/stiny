import gzip
from StringIO import StringIO
from datetime import datetime

import pyrax

from controller import Controller


class CloudFilesController(Controller):
    """
    A controller for an backing store using an CloudFiles container website.

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

    def put(self, url):
        """
        Put the tiny url to the backing store.
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
        Delete the tiny url from the backing store.
        :param url: the stiny.utl.StaticURL to be deleted (tiny_text must be provided) or str of tiny_text
        :raises: TinyURLDoesNotExistsException - if the provided tiny does not exist
        """
        # if isinstance(url, URL):
        # url = url.get_tiny_uri()
        #
        # if self.exists(url):
        #     self._container.delete_key(url)
        # else:
        #     raise TinyUrlDoesNotExistException("{} does not exist".format(url))
        pass

    def list(self):
        """
        List the tiny urls in the backing store (should not list non-tinys)
        :return: Generate of (tiny_text, destination_url)
        """
        # for key in self._container:
        # try:
        #         akey = self._container.get_key(key.key)
        #         url = akey.metadata["tiny_url"]
        #         surl = URL(url=url, tiny_text=key.key, prefix_separator=self.prefix_separator)
        #         surl.last_modified = datetime.strptime(akey.last_modified, "%a, %d %b %Y %H:%M:%S %Z")
        #         yield surl
        #     except KeyError:
        #         continue
        pass

    def exists(self, url):
        """
        Check to see if the tiny_url specified exists
        :param url: the stiny.url.StaticURL to be checked (tiny_text must be provided) or str of tiny_text
        :return: Boolean of existence
        """


        # assert isinstance(self._container, pyrax.object_storage.StorageClient)  #TODO Remove
        #
        # self._container
        # if isinstance(url, URL):
        # url = url.get_tiny_uri()
        #
        # if url is None:
        #     return False
        # else:
        #     return self._container.get_key(url) is not None
        pass

    def validate(self, url):
        """
        Check to see if the tiny_url specified exists and points to the correct href
        :param url: the stiny.utl.StaticURL to validate
        :return: Boolean of validity
        """
        # return self.exists(url) and self._container.get_key(url.get_tiny_uri()).get_metadata("tiny_url") == url.url
        pass
