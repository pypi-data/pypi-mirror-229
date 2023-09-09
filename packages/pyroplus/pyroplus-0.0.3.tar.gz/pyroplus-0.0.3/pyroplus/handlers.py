from typing import Callable
from pyrogram.handlers.handler import Handler

__all__ = ['ReadHistoryInboxHandler', 'ReadHistoryOutboxHandler']


class ReadHistoryInboxHandler(Handler):

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)


class ReadHistoryOutboxHandler(Handler):

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)
