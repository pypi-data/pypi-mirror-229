from pyroplus import raw
from pyroplus.types import Object, Update


class ReadHistoryInbox(Object, Update):

    def __init__(self,
                 *,
                 client: 'pyroplus.Client',
                 peer: raw.base.Peer,
                 max_id: int,
                 still_unread_count: int,
                 folder_id: int | None = None):
        super().__init__(client)

        self.peer = peer
        self.max_id = max_id,
        self.still_unread_count = still_unread_count
        self.folder_id = folder_id

    @staticmethod
    def _parse(client: 'pyroplus.Client', update: raw.types.UpdateReadHistoryInbox) -> 'ReadHistoryInbox':
        return ReadHistoryInbox(
            client=client,
            peer=update.peer,
            max_id=update.max_id,
            still_unread_count=update.still_unread_count,
            folder_id=getattr(update, 'folder_id', None)
        )


class ReadHistoryOutbox(Object, Update):

    def __init__(self,
                 *,
                 client: 'pyroplus.Client',
                 peer: raw.base.Peer,
                 max_id: int):
        super().__init__(client)

        self.peer = peer
        self.max_id = max_id,

    @staticmethod
    def _parse(client: 'pyroplus.Client', update: raw.types.UpdateReadHistoryOutbox) -> 'ReadHistoryOutbox':
        return ReadHistoryOutbox(
            client=client,
            peer=update.peer,
            max_id=update.max_id
        )
