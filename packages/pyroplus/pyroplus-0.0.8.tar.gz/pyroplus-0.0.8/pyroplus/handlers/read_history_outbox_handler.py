from typing import Callable
from pyroplus.handlers.handler import Handler

__all__ = ['ReadHistoryOutboxHandler']


class ReadHistoryOutboxHandler(Handler):

    def __init__(self, callback: Callable, filters=None):
        super().__init__(callback, filters)
