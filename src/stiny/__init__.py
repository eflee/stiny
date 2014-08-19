"""Stiny module - tiny url generation using static storage and jinja templates

    The stiny module consists of the following submodules:

.. moduleauthor:: Eli Flesher <eli@eflee.us>

"""

import logging

__version__ = '0.1'

_debug = 0
logger = logging.getLogger('stiny')


class _NullHandler(logging.Handler):
    def emit(self, record):
        pass

nh = _NullHandler()
nh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)


def debug(setting):
    """
    Set debug on or off

    :param setting: The log level, currently 0 is off any anything else is DEBUG
    :type setting: int
    """
    if setting == 0:
        if ch in logger.handlers:
            logger.removeHandler(ch)
        if nh not in logger.handlers:
            logger.addHandler(nh)
    else:
        if ch not in logger.handlers:
            logger.addHandler(ch)




