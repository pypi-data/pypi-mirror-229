from pyrogram import Client as _Client, raw


class Client(_Client):

    async def get_peer_dialog(self, dialog_id: int) -> raw.types.dialog.Dialog:
        peers: list = [await self.resolve_peer(dialog_id)]

        r = await self.invoke(
            raw.functions.messages.GetPeerDialogs(peers=peers),
            sleep_threshold=60
        )
        dialog: raw.types.dialog.Dialog = r.dialogs[0]
        return dialog


