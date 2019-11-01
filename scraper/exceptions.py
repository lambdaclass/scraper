# -*- coding: utf-8 -*-

# Custom exceptions to provide contextual information for logger
# and notification extension.

from scrapy.exceptions import DropItem


class FileAlreadyPresent(DropItem):
    """Symbol file is already present"""
    pass


class InvalidFormat(DropItem):
    """Symbol data has invalid format"""
    pass
