import boto.s3
from stiny.controllers import Controller
from stiny.exceptions import TinyURLExistsException, UnableToAutogenerateTinyText, TinyUrlDoesNotExistException
from stiny.url import URL


class S3Controller(Controller):
    """
    A controller for an backing store using an S3 bucket website.

    Currently, the controller assumes the bucket exists, is configured as a website and has an expiration policy
    in place that supports the expiration rules of the StaticURLs
    """

    def __init__(self, bucket_name, region, aws_access_key_id, aws_secret_access_key, gzip = True, *args, **kwargs):
        """
        :param template: The template string or Template instance for the jinja2 template used to create the
        contents of the tiny
        :type template: str or jinja2.Template
        :param int initial_tiny_length: The length to try for autogenerating tiny text
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
        self.gzip = gzip

    def put(self, url):
        """
        Put the tiny url to the backing store.
        If the tiny_text is provided in the url, it will be used (and overwritten as specified)
        Otherwise, it will attempt to generate non-conflicting tiny text
        :param str url: the stiny.utl.StaticURL to be generated
        :raises TooManyNameCollisions: if we're unable to autogenerate a tiny_text name
        :raises TinyURLExistsException: if the provided tiny exists and we're not overwriting
        """

        if not url.tiny_text_provided:
            self._select_available_tiny_text(url)
        else:
            if not self.overwrite and self.exists(url.get_tiny_uri()):
                raise TinyURLExistsException("{} already exists".format(url.get_tiny_uri()))

        tiny_key = self._bucket.new_key(key_name=url.get_tiny_uri())
        tiny_key.set_metadata("tiny_url", url.url)
        tiny_key.set_metadata("Content-Type", "text/html")
        tiny_key.set_contents_from_string(self._generate_contents(url), policy="public-read")

    def _select_available_tiny_text(self, url):
        key_selected = False
        retries = 0
        tiny_text_length = self.initial_tiny_length

        while not key_selected and retries < self.max_retries:
            url.tiny_text = url.generate_tiny_text(tiny_text_length)
            if not self.exists(url.get_tiny_uri()):
                key_selected = True
                break
            else:
                if retries > 1:
                    # increase length on the second collision
                    tiny_text_length += 1
                retries += 1

        if not key_selected:
            url.tiny_text = None
            raise UnableToAutogenerateTinyText(
                "Unable to generate tiny name, increase retries or increase key start length or provide a name")

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

    def _generate_contents(self, url):
        return "\n".join([line for line in self.template.generate(url=url)])
