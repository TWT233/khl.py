from .abc import LazyLoadable


class Channel(LazyLoadable):
    """
    `Standard Object`

    represent the place for chats, and the tunnel that msgs transferred in
    """
    id: str
    name: str
    user_id: str
    guild_id: str
    topic: str
    is_category: int
    parent_id: str
    level: int
    slow_mode: int
    type: int
    permission_overwrites: list
    permission_users: list
    permission_sync: int

    def __init__(self, **kwargs):
        self.id: str = kwargs.get('id', '')
        self.name: str = kwargs.get('name', '')
        self.user_id: str = kwargs.get('user_id', '')
        self.guild_id: str = kwargs.get('guild_id', '')
        self.topic: str = kwargs.get('topic', '')
        self.is_category: int = kwargs.get('is_category', 0)
        self.parent_id: str = kwargs.get('parent_id', '')
        self.level: int = kwargs.get('level', 0)
        self.slow_mode: int = kwargs.get('slow_mode', 0)
        self.type: int = kwargs.get('type', 1)
        self.permission_overwrites: list = kwargs.get('permission_overwrites', ())
        self.permission_users: list = kwargs.get('permission_users', ())
        self.permission_sync: int = kwargs.get('permission_sync', 1)

        self._loaded = kwargs.get('_lazy_loaded_', False)
        self._gate = kwargs.get('_gate_', None)

    async def load(self):
        pass
