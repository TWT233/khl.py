from typing import Any, Mapping, Sequence, TYPE_CHECKING

from .hardcoded import API_URL

if TYPE_CHECKING:
    from khl.bot import Bot


class User:
    __slots__ = 'id', 'roles', 'bot', 'username'
    """
    presents a User in chat/group

    including other bots
    """
    id: str
    roles: Sequence[str]
    username: str

    def __init__(self, data: Mapping[str, Any]):
        self.id = data['id']
        self.username = data.get('username')
        self.roles = data['roles'] if data.get('roles') else []
        pass

    @property
    def mention(self):
        return f'(met){self.id}(met)'

    async def send_pm(self, bot: 'Bot', content: str, **kwargs):
        return await bot.send_dm(self.id, content, **kwargs)

    async def update_pm(self, bot: 'Bot', msg_id: str, content: str, **kwargs):
        return await bot.update_dm(msg_id, content, **kwargs)

    async def delete_pm(self, bot: 'Bot', msg_id: str):
        return await bot.delete_dm(msg_id)

    async def grant_role(self, bot: 'Bot', guild_id: str,
                         role_id: int) -> dict:
        return await bot.post(f'{API_URL}/guild-role/grant?compress=0',
                              json={
                                  'user_id': self.id,
                                  'guild_id': guild_id,
                                  'role_id': role_id
                              })

    async def revoke_role(self, bot: 'Bot', guild_id: str,
                          role_id: int) -> dict:
        return await bot.post(f'{API_URL}/guild-role/revoke?compress=0',
                              json={
                                  'user_id': self.id,
                                  'guild_id': guild_id,
                                  'role_id': role_id
                              })
