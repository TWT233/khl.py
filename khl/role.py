from .types import RoleTypes


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
    type: RoleTypes

    def __init__(self, **kwargs):
        self.id: int = kwargs.get("role_id", 0)
        self.name: str = kwargs.get("name", "")
        self.color: int = kwargs.get("color", 0)
        self.position: int = kwargs.get("position", 0)
        self.hoist: int = kwargs.get("hoist", 0)
        self.mentionable: int = kwargs.get("mentionable", 0)
        self.permissions: int = kwargs.get("permissions", 0)
        self.type: RoleTypes = RoleTypes(kwargs.get("type", 0))

    def has_permission(self, bit_value: int) -> bool:
        """
        bitValue see https://developer.kaiheila.cn/doc/http/guild-role#%E6%9D%83%E9%99%90%E8%AF%B4%E6%98%8E
        """
        return self.permissions & (1 << bit_value) != 0
