import gzip
from StringIO import StringIO

import boto.s3

from ..exceptions import TinyUrlDoesNotExistException
from controller import Controller
from ..url import URL


class S3Controller(Controller):
    """
    A controller for an backing store using an S3 bucket website.

    Currently, the controller assumes the bucket exists, is configured as a website and has an expiration policy
    in place that supports the expiration rules of the StaticURLs
    """

    def __init__(self, bucket_name, region, aws_access_key_id, aws_secret_access_key, compress=True, *args, **kwargs):
        """
        :param template: The template string or Template instance for the jinja2 template used to create the
        contents of the tiny
        :type template: str or jinja2.Template
        :param int tiny_length: The length to try for autogenerating tiny text
        :param int max_retries: The max number if attempts to generate a unique tiny
        :param boolean overwrite: Overwrite (if tiny text is provided)
        :param str bucket_name: The name of the S3 website bucket
        :param str region: The S3 region to connect to e.g. us-west-2
        :param str aws_access_key_id: The AWS Access Key Id to Authentication
        :param str aws_secret_access_key: The AWS Access Key Id to Authentication
        """
        super(S3Controller, self).__init__(*args, **kwargs)

        _conn = boto.s3.connect_to_region(region_name=region,
                                          aws_access_key_id=aws_access_key_id,
                                          aws_secret_access_key=aws_secret_access_key)

        self._bucket = _conn.get_bucket(bucket_name, validate=False)
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
        This method sets the necessary S3 metadata to make S3 website servie the objet appropriately. Most notably, \
        this sets Content-Type to text/html and Content-Encoding to gzip if compression is set.
        """

        if url.tiny_text is None:
            self._select_tiny_text(url)

        tiny_key = self._bucket.new_key(key_name=url.get_tiny_uri())

        tiny_key.set_metadata("tiny_url", url.url)
        tiny_key.set_metadata("Content-Type", "text/html")
        if self._compression:
            tiny_key.set_metadata("Content-Encoding", "gzip")

        sio = self._get_contents_fp(url)
        tiny_key.set_contents_from_file(fp=sio, policy="public-read")
        sio.close()

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
            gio.write(super(S3Controller, self)._get_contents(url))
            gio.close()
            sio.seek(0)
        else:
            sio = super(S3Controller, self)._get_contents_fp(url)

        return sio

    def delete(self, url):
        """
        Delete the tiny url from the backing store.
        :param url: the stiny.utl.StaticURL to be deleted (tiny_text must be provided) or str of tiny_text
        :raises: TinyURLDoesNotExistsException - if the provided tiny does not exist
        """
        if isinstance(url, URL):
            url = url.get_tiny_uri()

        if self.exists(url):
            self._bucket.delete_key(url)
        else:
            raise TinyUrlDoesNotExistException("{} does not exist".format(url))

    def list(self):
        """
        List the tiny urls in the backing store (should not list non-tinys)
        :return: Generate of (tiny_text, destination_url)
        """
        for key in self._bucket:
            try:
                akey = self._bucket.get_key(key.key)
                url = akey.metadata["tiny_url"]
                yield URL(url=url, tiny_text=key.key, prefix_separator=self.prefix_separator)
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
            return self._bucket.get_key(url) is not None

    def validate(self, url):
        """
        Check to see if the tiny_url specified exists and points to the correct href
        :param url: the stiny.utl.StaticURL to validate
        :return: Boolean of validity
        """
        return self.exists(url) and self._bucket.get_key(url.get_tiny_uri()).get_metadata("tiny_url") == url.url
