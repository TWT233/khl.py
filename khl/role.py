class Role:
    """
    `Standard Object`

    represent the component that used in permission control and user identify
    """
    id: int
    name: str
    color: int
    position: int
    hoist: int
    mentionable: int
    permissions: int

    def __init__(self, **kwargs):
        self.id: int = kwargs.get("role_id", 0)
        self.name: str = kwargs.get("name", "")
        self.color: int = kwargs.get("color", 0)
        self.position: int = kwargs.get("position", 0)
        self.hoist: int = kwargs.get("hoist", 0)
        self.mentionable: int = kwargs.get("mentionable", 0)
        self.permissions: int = kwargs.get("permissions", 0)

        self._permissions = self._perm_to_bit()

    def _perm_to_bit(self, count=28) -> str:
        return "".join([str((self.permissions >> y) & 1) for y in range(count - 1, -1, -1)])

    def has_permission(self, bit_value: int) -> bool:
        """
        bitValue see https://developer.kaiheila.cn/doc/http/guild-role#%E6%9D%83%E9%99%90%E8%AF%B4%E6%98%8E
        """
        return self._permissions[27 - bit_value] == '1'
