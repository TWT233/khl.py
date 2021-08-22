import logging
from typing import TYPE_CHECKING, Union

from .hardcoded import API_URL

if TYPE_CHECKING:
    from .bot import Bot


class Role:

    def __init__(self, **kwargs):
        self.role_id: int = kwargs.get("role_id", 0)
        self.name: str = kwargs.get("name", "")
        self.color: int = kwargs.get("color", 0)
        self.position: int = kwargs.get("position", 0)
        self.hoist: int = kwargs.get("hoist", 0)
        self.mentionable: int = kwargs.get("mentionable", 0)
        self.permissions: int = kwargs.get("permissions", 0)


class Guild:
    logger = logging.getLogger('khl.Guild')

    def __init__(self, guild_id: Union[str, None], bot: 'Bot'):
        self.id = guild_id
        self.bot = bot

    @property
    def is_user_chat(self):
        return self.id is None
    
    async def get_channels(self) -> list:
        return await self.bot.get(f'{API_URL}/channel/list?compress=0',
                             json={'guild_id': self.id})
    
    async def create_channel(self, name: str = None, parent_id: str = '', type: int = 1) -> list:
        return await self.bot.post(f'{API_URL}/channel/create?compress=0',
                              json={
                                  'name': name,
                                  'type': type,
                                  'parent_id': parent_id,
                                  'guild_id': self.id
                              } if name else {'guild_id': self.id})
    
    async def delete_channel(self, channel_id: str = None):
        await self.bot.post(f'{API_URL}/channel/delete?compress=0',
                       json={
                           'channel_id': channel_id
                       })
    

    async def get_roles(self) -> list:
        return await self.bot.get(f'{API_URL}/guild-role/index?compress=0',
                             json={'guild_id': self.id})

    async def create_role(self, name: str = None) -> list:
        return await self.bot.post(f'{API_URL}/guild-role/create?compress=0',
                              json={
                                  'name': name,
                                  'guild_id': self.id
                              } if name else {'guild_id': self.id})

    async def delete_role(self, name: str):
        await self.bot.post(f'{API_URL}/guild-role/delete?compress=0',
                       json={
                           'name': name,
                           'guild_id': self.id
                       })

    async def update_role(self,
                          *,
                          role_id: int,
                          mentionable: bool,
                          permissions: int,
                          hoist: bool = False) -> bool:
        return await self.bot.post(f'{API_URL}/guild-role/update?compress=0',
                              json={
                                  'guild_id': self.id,
                                  'role_id': role_id,
                                  'hoist': 1 if hoist else 0,
                                  'mentionable': 1 if mentionable else 0,
                                  'permissions': permissions
                              })
