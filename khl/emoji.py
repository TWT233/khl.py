from . import api
from .gateway import Gateway, Requestable
from .user import GuildUser


class GuildEmoji(Requestable):
    """
    The custom emojis in the guild
    """
    guild_id: str
    name: str
    id: str
    user: GuildUser

    def __init__(self, _gate_: Gateway, **kwargs):
        self.guild_id = kwargs.get("guild_id")
        self.name = kwargs.get("name")
        self.id = kwargs.get("id")
        self.user = GuildUser(_gate_=_gate_, guild_id=self.guild_id, **kwargs.get("user_info"))

    async def update(self, name: str):
        """update this emoji's name"""
        await self.gate.exec_req(api.GuildEmoji.update(id=self.id, name=name))

    async def delete(self):
        """delete this custom emoji"""
        await self.gate.exec_req(api.GuildEmoji.delete(id=self.id))
