class Channel:
    def __init__(self, id: str = '', **kwargs):
        self.id = kwargs.get('id', id)
        self.name: str = kwargs.get('name', '')
        self.user_id: str = kwargs.get('user_id', '')
        self.guild_id: str = kwargs.get('guild_id', '')
        self.topic: str = kwargs.get('topic', '')
        self.is_category: int = kwargs.get('is_category', 0)
        self.parent_id: str = kwargs.get('parent_id', '')
        self.level: int = kwargs.get('level', 0)
        self.slow_mode: int = kwargs.get('slow_mode', 0)
        self.type: int = kwargs.get('type', 1)
        self.permission_overwrites: list = kwargs.get('permission_overwrites',
                                                      ())
        self.permission_users: list = kwargs.get('permission_users', ())
        self.permission_sync: int = kwargs.get('permission_sync', 1)
