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
