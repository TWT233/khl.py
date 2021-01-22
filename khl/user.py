from __future__ import annotations
from khl.bot import Bot
from typing import Any, Mapping, Sequence


class User:
    __slots__ = 'id', 'roles', 'bot'
    """
    presents a User in chat/group

    including other bots
    """
    id: str

    def __init__(self, data: Mapping[str, Any]):
        self.id: str = data['user_id']
        self.roles: Sequence[int] = data['roles'] if data['roles'] else []
        self.bot: Bot = data['bot']
        pass

    async def grant_role(self, guild_id: str, role_id: int) -> bool:
        return await self.bot.user_grant_role(self.id, guild_id, role_id)
