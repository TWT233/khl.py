from typing import Any, Mapping, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from khl.bot import Bot


class User():
    __slots__ = 'id', 'roles', 'bot'
    """
    presents a User in chat/group

    including other bots
    """
    id: str
    roles: Sequence[int]
    bot: 'Bot'

    def __init__(self, data: Mapping[str, Any], bot: 'Bot'):
        self.id = data['id']
        self.roles = data['roles'] if data['roles'] else []
        self.bot
        pass

    async def grant_role(self, guild_id: str, role_id: int) -> bool:
        return await self.bot.user_grant_role(self.id, guild_id, role_id)
