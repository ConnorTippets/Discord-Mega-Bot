__title__ = 'Discord Mega Bot'
__author__ = 'Connor Tippets'
__license__ = 'MIT'
__copyright__ = 'Copyright 2020-present Connor'
__version__ = '1.9.1a'

from collections import namedtuple
import logging

from bot import *
from properties import *
from tools import helper

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=1, minor=9, micro=1, releaselevel='alpha', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())
