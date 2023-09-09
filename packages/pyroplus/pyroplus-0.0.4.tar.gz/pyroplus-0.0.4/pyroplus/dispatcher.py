from pyrogram.dispatcher import Dispatcher as _Dispatcher
from pyrogram.raw.types import UpdateReadHistoryInbox, UpdateReadHistoryOutbox
from .client import Client
from .handlers import ReadHistoryInboxHandler
from .types import ReadHistoryInbox


class Dispatcher(_Dispatcher):

    def __init__(self, client: Client):
        super().__init__(client)

        async def read_history_inbox_parser(update, _, __):
            ...

        async def read_history_outbox_parser(update, _, __):
            return (
                ReadHistoryInbox._parse(client, update),
                ReadHistoryInboxHandler
            )

        self.update_parsers[UpdateReadHistoryInbox] = read_history_inbox_parser
        self.update_parsers[UpdateReadHistoryOutbox] = read_history_outbox_parser

