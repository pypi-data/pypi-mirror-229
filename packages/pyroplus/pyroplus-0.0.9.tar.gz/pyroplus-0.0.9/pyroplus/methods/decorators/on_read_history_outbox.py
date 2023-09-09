from typing import Callable

import pyroplus
from pyroplus.filters import Filter


class OnReadHistoryOutbox:
    def on_read_history_outbox(
        self=None,
        filters=None,
        group: int = 0
    ) -> Callable:
        """Decorator for handling read history outbox

        This does the same thing as :meth:`~pyroplus.Client.add_handler` using the
        :obj:`~pyroplus.handlers.ReadHistoryOutboxHandler`.

        Parameters:
            filters (:obj:`~pyroplus.filters`, *optional*):
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: Callable) -> Callable:
            if isinstance(self, pyroplus.Client):
                self.add_handler(pyroplus.handlers.ReadHistoryOutboxHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (
                        pyroplus.handlers.ReadHistoryOutboxHandler(func, self),
                        group if filters is None else filters
                    )
                )

            return func

        return decorator
