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
    roles: Sequence[str]
    bot: 'Bot'

    def __init__(self, data: Mapping[str, Any], bot: 'Bot'):
        self.id = data['id']
        self.roles = data['roles'] if data.get('roles') else []
        self.bot = bot
        pass

    async def grant_role(self, guild_id: str, role_id: str) -> bool:
        return await self.bot.user_grant_role(self.id, guild_id, role_id)
