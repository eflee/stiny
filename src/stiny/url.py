import re
import random
import string
from . import InvalidExpirationException, InvalidTinyTextException, InvalidURLException


class StaticURL(object):
    """
    The representation of the Tiny URL
    """

    def __init__(self, url, tiny_text=None, expiration=None):
        """
        :param url: The url we're creating the TinyURL for
        :type url str
        :param tiny_text: The text to be used as the tinyURL (optional)
        :type tiny_text: str
        :param expiration: The days the url will be valid for (is the backing store supports expiration)
        :type expiration: int
        """
        self._url = None
        self.url = url
        self._expiration = None
        self.expiration = expiration
        self._tiny_text = None
        self.tiny_text = tiny_text
        self.tiny_text_provided = tiny_text is not None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, href):
        if self._url_valid(href):
            self._url = href
        else:
            raise InvalidURLException("{} is an invalid url".format(href))

    @staticmethod
    def _url_valid(url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        match = regex.match(url)
        return match is not None

    @property
    def tiny_text(self):
        expiration = self.expiration + 'T' if self.expiration else ""
        return expiration + self._tiny_text

    @tiny_text.setter
    def tiny_text(self, tiny_text):
        if isinstance(tiny_text, (str, unicode)) and 'T' in tiny_text:
            tiny_split = tiny_text.split('T')
            if len(tiny_split) == 2:
                self.expiration = tiny_split[0]
                tiny_text = tiny_split[1]

        if tiny_text is None or (tiny_text.isalnum() and tiny_text.islower()):
            self._tiny_text = tiny_text
        else:
            raise InvalidTinyTextException("{} is invalid tiny text".format(tiny_text))

    def generate_tiny_text(self, length):
        # noinspection PyUnusedLocal
        expiration = self.expiration + 'T' if self.expiration else ""
        return expiration + "".join(random.choice(string.lowercase + string.digits) for i in range(int(length)))

    @property
    def expiration(self):
        return self._expiration

    @expiration.setter
    def expiration(self, expiration):
        if expiration is None:
            self._expiration = ""
        else:
            self._expiration = str(expiration)


