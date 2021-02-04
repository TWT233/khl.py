import logging
from typing import TYPE_CHECKING

from .hardcoded import API_URL

if TYPE_CHECKING:
    from .bot import Bot


class Guild:
    logger = logging.getLogger('khl.Guild')

    def __init__(self, guild_id: str):
        self.id = guild_id

    async def get_roles(self, bot: 'Bot') -> list:
        return await bot.get(f'{API_URL}/guild-role/index?compress=0',
                             json={'guild_id': self.id})

    async def create_role(self, bot: 'Bot', name: str = None) -> bool:
        return await bot.post(f'{API_URL}/guild-role/create?compress=0',
                              json={
                                  'name': name,
                                  'guild_id': self.id
                              } if name else {'guild_id': self.id})

    async def delete_role(self, bot: 'Bot', name: str) -> bool:
        return await bot.post(f'{API_URL}/guild-role/delete?compress=0',
                              json={
                                  'name': name,
                                  'guild_id': self.id
                              })

    async def update_role(self,
                          bot: 'Bot',
                          *,
                          role_id: int,
                          mentionable: bool,
                          permissions: int,
                          hoist: bool = False) -> bool:
        return await bot.post(f'{API_URL}/guild-role/update?compress=0',
                              json={
                                  'guild_id': self.id,
                                  'role_id': role_id,
                                  'hoist': 1 if hoist else 0,
                                  'mentionable': 1 if mentionable else 0,
                                  'permissions': permissions
                              })
